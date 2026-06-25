from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_BASE,
    add_combo_scores,
    build_scored_panel,
    evaluate_factor_window,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
)
from build_phase1_training_panel import load_price_history


SCRIPT_DIR = Path(__file__).resolve().parent

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "base_core_6_robustness_validation_v1_config_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "base_core_6_robustness_validation_v1.md"

EXCLUDED_FACTOR = "derived__log_total_assets"
TARGET_BASE_SET = [
    "indicator__roe",
    "indicator__eps",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]

TRAIN_YEAR_COUNTS = [3, 5, 7]
TEST_YEAR_COUNTS = [1, 2]
REVIEW_YEAR_COUNT = 1
HOLD_COUNTS = [6, 8, 10, 12]
COMBO_CANDIDATES = [
    "combo__equal_weight",
    "combo__ic_weight_train",
    "combo__quarterly_plus_annual",
]
BASELINE_CONFIG_KEY = "window_5y_2y_1y__combo__ic_weight_train__top_08"


def filter_factor_universe(
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    filtered_base_rows = [row for row in base_rows if row["factor_name"] in TARGET_BASE_SET]
    filtered_enhanced_rows = [
        row for row in enhanced_rows
        if row["factor_name"] in TARGET_BASE_SET or row["factor_name"] != EXCLUDED_FACTOR
    ]
    filtered_universe_rows = [row for row in universe_rows if row["factor_name"] != EXCLUDED_FACTOR]
    return filtered_base_rows, filtered_enhanced_rows, filtered_universe_rows


def apply_fixed_base_selection(
    selection_rows: list[dict[str, object]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    metadata_map = {row["factor_name"]: row for row in base_rows + enhanced_rows}
    selected_names = {
        row["factor_name"]
        for row in selection_rows
        if row["factor_name"] in TARGET_BASE_SET and int(row["keep_flag"]) == 1
    }

    adjusted_rows: list[dict[str, object]] = []
    for row in selection_rows:
        row_copy = row.copy()
        factor_name = str(row_copy["factor_name"])
        if factor_name in TARGET_BASE_SET and int(row_copy["keep_flag"]) == 1 and factor_name in selected_names:
            row_copy["keep_reason"] = f"{row_copy['keep_reason']}|kept_in_base_core_6"
        elif factor_name in TARGET_BASE_SET and int(row_copy["keep_flag"]) == 1:
            row_copy["keep_flag"] = 0
            row_copy["keep_reason"] = f"{row_copy['keep_reason']}|dropped_from_base_core_6"
        adjusted_rows.append(row_copy)

    selected_rows = [metadata_map[name] for name in TARGET_BASE_SET if name in selected_names]
    return selected_rows, adjusted_rows


def select_factor_rows_base6(
    panel_df: pd.DataFrame,
    universe_rows: list[dict[str, str]],
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])

    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)

    selection_rows: list[dict[str, object]] = []
    for factor_row in universe_rows:
        evaluated = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
        selection_rows.append(evaluated | {"fold_id": fold["fold_id"]})
    return apply_fixed_base_selection(selection_rows, base_rows, enhanced_rows)


def build_yearly_folds_custom(
    may_dates: list[pd.Timestamp],
    train_year_count: int,
    test_year_count: int,
    review_year_count: int,
) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    required_span = train_year_count + test_year_count + review_year_count
    for start_idx in range(0, len(may_dates) - required_span + 1):
        train_dates = may_dates[start_idx : start_idx + train_year_count]
        test_dates = may_dates[start_idx + train_year_count : start_idx + train_year_count + test_year_count]
        review_dates = may_dates[
            start_idx + train_year_count + test_year_count : start_idx + required_span
        ]
        if (
            len(train_dates) < train_year_count
            or len(test_dates) < test_year_count
            or len(review_dates) < review_year_count
        ):
            continue
        folds.append(
            {
                "fold_id": f"annual_{len(folds) + 1:02d}",
                "train_start": train_dates[0].strftime("%Y-%m-%d"),
                "train_end": (test_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "test_start": test_dates[0].strftime("%Y-%m-%d"),
                "test_end": (review_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "review_start": review_dates[0].strftime("%Y-%m-%d"),
                "review_end": (
                    review_dates[0] + pd.DateOffset(years=review_year_count) - pd.Timedelta(days=1)
                ).strftime("%Y-%m-%d"),
            }
        )
    return folds


def load_daily_path(code: str) -> pd.DataFrame:
    price_df = load_price_history(code).copy()
    if price_df.empty:
        return pd.DataFrame(columns=["day", "close", "daily_return"])
    price_df["day"] = pd.to_datetime(price_df["day"]).dt.date
    price_df["close"] = pd.to_numeric(price_df["close"], errors="coerce")
    price_df = (
        price_df.dropna(subset=["day", "close"])
        .sort_values("day")
        .drop_duplicates(subset=["day"], keep="last")
        .reset_index(drop=True)
    )
    if price_df.empty:
        return pd.DataFrame(columns=["day", "close", "daily_return"])
    price_df["daily_return"] = price_df["close"].pct_change()
    return price_df[["day", "close", "daily_return"]].copy()


def get_aligned_row(df: pd.DataFrame, target_date: pd.Timestamp | str, mode: str) -> pd.Series | None:
    if df.empty:
        return None
    target_day = pd.Timestamp(target_date).date()
    if mode == "anchor":
        eligible = df[df["day"] >= target_day].copy()
    else:
        eligible = df[df["day"] <= target_day].copy()
    if eligible.empty:
        return None
    eligible = eligible.sort_values("day")
    return eligible.iloc[0] if mode == "anchor" else eligible.iloc[-1]


def simulate_period_return(
    top_codes: list[str],
    rebalance_date: pd.Timestamp,
    next_rebalance_date: pd.Timestamp,
    daily_cache: dict[str, pd.DataFrame],
) -> tuple[float, dict[str, float]]:
    if not top_codes:
        return np.nan, {"avg_cash_weight": np.nan, "invested_stock_count": 0}

    base_weight = 1.0 / float(len(top_codes))
    all_days: set[object] = set()
    stock_windows: dict[str, dict[object, float]] = {}

    for code in top_codes:
        stock_df = daily_cache.get(code, pd.DataFrame()).copy()
        if stock_df.empty:
            continue
        entry_row = get_aligned_row(stock_df, rebalance_date, "anchor")
        end_row = get_aligned_row(stock_df, next_rebalance_date, "end")
        if entry_row is None or end_row is None:
            continue
        entry_day = entry_row["day"]
        end_day = end_row["day"]
        if entry_day >= end_day:
            continue
        window = stock_df[(stock_df["day"] > entry_day) & (stock_df["day"] <= end_day)].copy()
        if window.empty:
            continue
        stock_windows[code] = {
            row["day"]: float(row["daily_return"]) if pd.notna(row["daily_return"]) else np.nan
            for _, row in window.iterrows()
        }
        all_days.update(stock_windows[code].keys())

    if not stock_windows:
        return np.nan, {"avg_cash_weight": np.nan, "invested_stock_count": 0}

    ordered_days = sorted(all_days)
    period_returns: list[float] = []
    cash_weights: list[float] = []

    for day in ordered_days:
        portfolio_return = 0.0
        active_weight_sum = 0.0
        for code, day_map in stock_windows.items():
            daily_return = day_map.get(day)
            if daily_return is None:
                continue
            if pd.notna(daily_return):
                portfolio_return += base_weight * float(daily_return)
            active_weight_sum += base_weight
        cash_weights.append(max(0.0, 1.0 - active_weight_sum))
        period_returns.append(portfolio_return)

    if not period_returns:
        return np.nan, {"avg_cash_weight": np.nan, "invested_stock_count": 0}

    total_return = float(np.prod([1.0 + x for x in period_returns]) - 1.0)
    metrics = {
        "avg_cash_weight": float(np.mean(cash_weights)) if cash_weights else 0.0,
        "invested_stock_count": int(len(stock_windows)),
    }
    return total_return, metrics


def build_config_key(train_year_count: int, test_year_count: int, combo_name: str, hold_count: int) -> str:
    return (
        f"window_{train_year_count}y_{test_year_count}y_{REVIEW_YEAR_COUNT}y__"
        f"{combo_name}__top_{hold_count:02d}"
    )


def build_master_frame(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
    combo_name: str,
) -> pd.DataFrame:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

    context_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

    selected_rows, _ = select_factor_rows_base6(
        panel_df=panel_df,
        universe_rows=universe_rows,
        fold=fold,
        base_rows=base_rows,
        enhanced_rows=enhanced_rows,
    )
    factor_specs = [row for row in base_rows if row["factor_name"] in {spec["factor_name"] for spec in selected_rows}]
    if not factor_specs:
        return pd.DataFrame()

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
        panel_df[context_mask].copy(),
        factor_specs,
        train_mask[context_mask],
    )
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty or combo_name not in scored_df.columns:
        return pd.DataFrame()

    scored_df["rebalance_date"] = pd.to_datetime(scored_df["rebalance_date"])
    scored_df = scored_df.sort_values(["rebalance_date", combo_name], ascending=[True, False]).copy()
    rebalance_dates = sorted(pd.to_datetime(scored_df["rebalance_date"].drop_duplicates()))

    rows: list[dict[str, object]] = []
    for idx, rebalance_date in enumerate(rebalance_dates):
        if rebalance_date < train_start or rebalance_date >= review_end or idx + 1 >= len(rebalance_dates):
            continue
        next_rebalance_date = rebalance_dates[idx + 1]
        if next_rebalance_date > review_end:
            next_rebalance_date = review_end - pd.Timedelta(days=1)

        group = scored_df[scored_df["rebalance_date"] == rebalance_date].copy()
        group = group.dropna(subset=[combo_name]).sort_values(combo_name, ascending=False).copy()
        if len(group) < min(HOLD_COUNTS):
            continue

        row = {
            "rebalance_date": pd.Timestamp(rebalance_date),
            "next_rebalance_date": pd.Timestamp(next_rebalance_date),
            "window_label": (
                "train" if rebalance_date < test_start else ("test" if rebalance_date < review_start else "review")
            ),
            "ranked_count": int(len(group)),
            "selected_factor_count": int(len(factor_specs)),
        }
        for hold_count in HOLD_COUNTS:
            top_codes = group.head(hold_count)["code"].astype(str).tolist()
            period_return, metrics = simulate_period_return(
                top_codes=top_codes,
                rebalance_date=rebalance_date,
                next_rebalance_date=next_rebalance_date,
                daily_cache=daily_cache,
            )
            row[f"return__top_{hold_count:02d}"] = period_return
            row[f"avg_cash_weight__top_{hold_count:02d}"] = metrics["avg_cash_weight"]
            row[f"invested_stock_count__top_{hold_count:02d}"] = metrics["invested_stock_count"]
        rows.append(row)

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def summarize_window_returns(returns: pd.Series) -> dict[str, object]:
    series = pd.to_numeric(returns, errors="coerce").dropna()
    if series.empty:
        return {
            "snapshot_count": int(len(returns)),
            "covered_snapshot_count": 0,
            "coverage_ratio": 0.0,
            "mean_period_return": np.nan,
            "cum_portfolio_return": np.nan,
        }
    return {
        "snapshot_count": int(len(returns)),
        "covered_snapshot_count": int(len(series)),
        "coverage_ratio": float(len(series) / len(returns)) if len(returns) > 0 else 0.0,
        "mean_period_return": float(series.mean()),
        "cum_portfolio_return": float((1.0 + series).prod() - 1.0),
    }


def flatten_window_metrics(window_metrics: dict[str, dict[str, object]]) -> dict[str, object]:
    flattened: dict[str, object] = {}
    for window_label, metrics in window_metrics.items():
        for key, value in metrics.items():
            flattened[f"{window_label}__{key}"] = value
    return flattened


def compute_selection_score(window_metrics: dict[str, dict[str, object]]) -> float:
    train_cum = window_metrics["train"]["cum_portfolio_return"]
    test_cum = window_metrics["test"]["cum_portfolio_return"]
    review_cum = window_metrics["review"]["cum_portfolio_return"]
    train_cov = window_metrics["train"]["coverage_ratio"]
    test_cov = window_metrics["test"]["coverage_ratio"]
    review_cov = window_metrics["review"]["coverage_ratio"]
    if any(pd.isna(value) for value in [train_cum, test_cum, review_cum]):
        return np.nan
    if min(train_cov, test_cov, review_cov) < 1.0:
        return np.nan
    return float(test_cum * 1000.0 + review_cum * 100.0 + train_cum)


def build_config_rows(
    panel_df: pd.DataFrame,
    may_dates: list[pd.Timestamp],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for train_year_count in TRAIN_YEAR_COUNTS:
        for test_year_count in TEST_YEAR_COUNTS:
            folds = build_yearly_folds_custom(
                may_dates=may_dates,
                train_year_count=train_year_count,
                test_year_count=test_year_count,
                review_year_count=REVIEW_YEAR_COUNT,
            )
            for combo_name in COMBO_CANDIDATES:
                for fold in folds:
                    master_df = build_master_frame(
                        panel_df=panel_df,
                        fold=fold,
                        base_rows=base_rows,
                        enhanced_rows=enhanced_rows,
                        universe_rows=universe_rows,
                        daily_cache=daily_cache,
                        combo_name=combo_name,
                    )
                    if master_df.empty:
                        continue
                    for hold_count in HOLD_COUNTS:
                        window_metrics = {
                            label: summarize_window_returns(
                                master_df.loc[master_df["window_label"] == label, f"return__top_{hold_count:02d}"]
                            )
                            for label in ["train", "test", "review"]
                        }
                        config_key = build_config_key(train_year_count, test_year_count, combo_name, hold_count)
                        rows.append(
                            {
                                "fold_id": fold["fold_id"],
                                "config_key": config_key,
                                "train_year_count": train_year_count,
                                "test_year_count": test_year_count,
                                "review_year_count": REVIEW_YEAR_COUNT,
                                "combo_name": combo_name,
                                "hold_count": hold_count,
                                "selection_status": "baseline" if config_key == BASELINE_CONFIG_KEY else "candidate",
                                **flatten_window_metrics(window_metrics),
                                "selection_score": np.nan
                                if config_key == BASELINE_CONFIG_KEY
                                else compute_selection_score(window_metrics),
                                "review__mean_avg_cash_weight": float(
                                    pd.to_numeric(
                                        master_df.loc[
                                            master_df["window_label"] == "review",
                                            f"avg_cash_weight__top_{hold_count:02d}",
                                        ],
                                        errors="coerce",
                                    ).mean()
                                ),
                                "review__mean_invested_stock_count": float(
                                    pd.to_numeric(
                                        master_df.loc[
                                            master_df["window_label"] == "review",
                                            f"invested_stock_count__top_{hold_count:02d}",
                                        ],
                                        errors="coerce",
                                    ).mean()
                                ),
                                "mean_selected_factor_count": float(
                                    pd.to_numeric(master_df["selected_factor_count"], errors="coerce").mean()
                                ),
                            }
                        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key in seen:
                continue
            seen.add(key)
            fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.{digits}f}"


def write_summary(config_rows: list[dict[str, object]]) -> None:
    config_df = pd.DataFrame(config_rows)
    if config_df.empty:
        OUTPUT_SUMMARY_PATH.write_text("# Base Core 6 Robustness Validation V1\n\n- no rows\n", encoding="utf-8")
        return

    lines = [
        "# Base Core 6 Robustness Validation V1",
        "",
        "Protocol:",
        "- factor engine = annual pure-fundamental `base_core_6`",
        f"- removed factor from mother shell = `{EXCLUDED_FACTOR}`",
        "- each year still re-trains and re-selects from the remaining 6-factor shell",
        "- this validation perturbs window lengths, combo scoring, and hold counts together",
        f"- tested train windows = `{ ' / '.join(str(v) for v in TRAIN_YEAR_COUNTS) }` years",
        f"- tested test windows = `{ ' / '.join(str(v) for v in TEST_YEAR_COUNTS) }` years",
        f"- tested review window = `{REVIEW_YEAR_COUNT}` year",
        f"- tested hold counts = `{ ' / '.join(str(v) for v in HOLD_COUNTS) }`",
        "",
        f"Baseline config: `{BASELINE_CONFIG_KEY}`",
        "",
        "Base candidate shell:",
    ]
    for factor_name in TARGET_BASE_SET:
        lines.append(f"- `{factor_name}`")

    baseline_df = config_df[config_df["config_key"] == BASELINE_CONFIG_KEY].copy()
    baseline_test_mean = float(pd.to_numeric(baseline_df["test__cum_portfolio_return"], errors="coerce").mean())
    baseline_review_mean = float(pd.to_numeric(baseline_df["review__cum_portfolio_return"], errors="coerce").mean())

    summary_df = (
        config_df.groupby(
            [
                "config_key",
                "train_year_count",
                "test_year_count",
                "review_year_count",
                "combo_name",
                "hold_count",
            ],
            dropna=False,
        )
        .agg(
            folds=("fold_id", "count"),
            mean_train_cum=("train__cum_portfolio_return", "mean"),
            mean_test_cum=("test__cum_portfolio_return", "mean"),
            mean_review_cum=("review__cum_portfolio_return", "mean"),
            mean_selection_score=("selection_score", "mean"),
            mean_selected_factor_count=("mean_selected_factor_count", "mean"),
            mean_review_cash=("review__mean_avg_cash_weight", "mean"),
        )
        .reset_index()
    )
    summary_df["delta_test_vs_baseline"] = summary_df["mean_test_cum"] - baseline_test_mean
    summary_df["delta_review_vs_baseline"] = summary_df["mean_review_cum"] - baseline_review_mean
    summary_df = summary_df.sort_values(
        ["delta_test_vs_baseline", "delta_review_vs_baseline", "mean_train_cum"],
        ascending=[False, False, False],
    )

    lines.extend(["", "Top configs by mean test return:"])
    for _, row in summary_df.head(12).iterrows():
        lines.append(
            f"- `{row['config_key']}` | folds=`{int(row['folds'])}` | "
            f"mean_train_cum=`{format_float(row['mean_train_cum'])}` | "
            f"mean_test_cum=`{format_float(row['mean_test_cum'])}` | "
            f"mean_review_cum=`{format_float(row['mean_review_cum'])}` | "
            f"delta_test_vs_baseline=`{format_float(row['delta_test_vs_baseline'])}` | "
            f"delta_review_vs_baseline=`{format_float(row['delta_review_vs_baseline'])}` | "
            f"mean_selected_count=`{format_float(row['mean_selected_factor_count'])}` | "
            f"mean_review_cash=`{format_float(row['mean_review_cash'])}`"
        )

    if not baseline_df.empty:
        lines.extend(
            [
                "",
                "Baseline means:",
                f"- mean_train_cum=`{format_float(baseline_df['train__cum_portfolio_return'].mean())}`",
                f"- mean_test_cum=`{format_float(baseline_df['test__cum_portfolio_return'].mean())}`",
                f"- mean_review_cum=`{format_float(baseline_df['review__cum_portfolio_return'].mean())}`",
            ]
        )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_CONFIG_RESULTS_PATH.name}]({OUTPUT_CONFIG_RESULTS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    panel_df["rebalance_date"] = pd.to_datetime(panel_df["rebalance_date"])
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    base_rows, enhanced_rows, universe_rows = filter_factor_universe(base_rows, enhanced_rows, universe_rows)
    may_dates = get_may_rebalance_dates(panel_df)

    daily_cache: dict[str, pd.DataFrame] = {}
    for code in sorted(panel_df["code"].astype(str).unique()):
        daily_cache[code] = load_daily_path(code)

    config_rows = build_config_rows(
        panel_df=panel_df,
        may_dates=may_dates,
        base_rows=base_rows,
        enhanced_rows=enhanced_rows,
        universe_rows=universe_rows,
        daily_cache=daily_cache,
    )
    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_summary(config_rows)
    print(OUTPUT_CONFIG_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
