from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_BASE,
    add_combo_scores,
    build_scenario_rows,
    build_scored_panel,
    build_yearly_folds,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
    select_factor_rows,
)
from build_phase1_training_panel import load_price_history


SCRIPT_DIR = Path(__file__).resolve().parent

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "pure_fundamental_execution_rolling_validation_v1_config_results.csv"
OUTPUT_CHOSEN_PATH = SCRIPT_DIR / "pure_fundamental_execution_rolling_validation_v1_chosen.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "pure_fundamental_execution_rolling_validation_v1.md"

TARGET_COMBO = "combo__ic_weight_train"
BASELINE_CONFIG_KEY = "pf_exec__top_08__delay_00"

HOLD_COUNTS = [8, 10, 12]
ENTRY_DELAY_DAYS = [0, 5]


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


def get_delay_entry_row(stock_df: pd.DataFrame, rebalance_date: pd.Timestamp, delay_days: int) -> pd.Series | None:
    anchor_row = get_aligned_row(stock_df, rebalance_date, "anchor")
    if anchor_row is None:
        return None
    anchor_day = anchor_row["day"]
    eligible = stock_df[stock_df["day"] >= anchor_day].copy().sort_values("day").reset_index(drop=True)
    if eligible.empty:
        return None
    target_idx = min(delay_days, len(eligible) - 1)
    return eligible.iloc[target_idx]


def build_strategy_key(config: dict[str, int]) -> str:
    return "pf_exec__top_%02d__delay_%02d" % (
        int(config["hold_count"]),
        int(config["entry_delay_days"]),
    )


def simulate_period_return(
    top_codes: list[str],
    rebalance_date: pd.Timestamp,
    next_rebalance_date: pd.Timestamp,
    config: dict[str, int],
    daily_cache: dict[str, pd.DataFrame],
) -> tuple[float, dict[str, float]]:
    if not top_codes:
        return np.nan, {"avg_cash_weight": np.nan, "invested_stock_count": 0}

    base_weight = 1.0 / float(len(top_codes))
    all_days: set[object] = set()
    stock_windows: dict[str, dict[object, float]] = {}
    entry_days: dict[str, object] = {}

    for code in top_codes:
        stock_df = daily_cache.get(code, pd.DataFrame()).copy()
        if stock_df.empty:
            continue
        entry_row = get_delay_entry_row(stock_df, rebalance_date, int(config["entry_delay_days"]))
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
        entry_days[code] = entry_day
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
            if entry_days.get(code) is None or day <= entry_days[code]:
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


def build_master_frame(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

    context_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

    selected_rows, _ = select_factor_rows(panel_df, universe_rows, fold)
    scenario_map = build_scenario_rows(selected_rows, base_rows, enhanced_rows)
    factor_specs = scenario_map.get(SCENARIO_BASE, [])
    if not factor_specs:
        return pd.DataFrame()

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
        panel_df[context_mask].copy(),
        factor_specs,
        train_mask[context_mask],
    )
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty:
        return pd.DataFrame()

    scored_df["rebalance_date"] = pd.to_datetime(scored_df["rebalance_date"])
    scored_df = scored_df.sort_values(["rebalance_date", TARGET_COMBO], ascending=[True, False]).copy()
    rebalance_dates = sorted(pd.to_datetime(scored_df["rebalance_date"].drop_duplicates()))

    rows: list[dict[str, object]] = []
    for idx, rebalance_date in enumerate(rebalance_dates):
        if rebalance_date < train_start or rebalance_date >= review_end:
            continue
        if idx + 1 >= len(rebalance_dates):
            continue
        next_rebalance_date = rebalance_dates[idx + 1]
        if next_rebalance_date > review_end:
            next_rebalance_date = review_end - pd.Timedelta(days=1)

        group = scored_df[scored_df["rebalance_date"] == rebalance_date].copy()
        group = group.dropna(subset=[TARGET_COMBO]).sort_values(TARGET_COMBO, ascending=False).copy()
        if len(group) < min(HOLD_COUNTS):
            continue

        row = {
            "rebalance_date": pd.Timestamp(rebalance_date),
            "next_rebalance_date": pd.Timestamp(next_rebalance_date),
            "window_label": (
                "train" if rebalance_date < test_start else
                ("test" if rebalance_date < review_start else "review")
            ),
            "ranked_count": int(len(group)),
        }

        for hold_count in HOLD_COUNTS:
            top_codes = group.head(hold_count)["code"].astype(str).tolist()
            row[f"selected_codes__top_{hold_count:02d}"] = "|".join(top_codes)
            for delay_days in ENTRY_DELAY_DAYS:
                config = {"hold_count": hold_count, "entry_delay_days": delay_days}
                strategy_key = build_strategy_key(config)
                period_return, metrics = simulate_period_return(
                    top_codes=top_codes,
                    rebalance_date=rebalance_date,
                    next_rebalance_date=next_rebalance_date,
                    config=config,
                    daily_cache=daily_cache,
                )
                row[f"return__{strategy_key}"] = period_return
                row[f"avg_cash_weight__{strategy_key}"] = metrics["avg_cash_weight"]
                row[f"invested_stock_count__{strategy_key}"] = metrics["invested_stock_count"]
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
    train_cov = window_metrics["train"]["coverage_ratio"]
    test_cov = window_metrics["test"]["coverage_ratio"]
    if any(pd.isna(value) for value in [train_cum, test_cum]) or train_cov < 1.0 or test_cov < 1.0:
        return np.nan
    return float(test_cum * 1000.0 + train_cum)


def build_config_rows(master_df: pd.DataFrame, fold: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for hold_count in HOLD_COUNTS:
        for delay_days in ENTRY_DELAY_DAYS:
            config = {"hold_count": hold_count, "entry_delay_days": delay_days}
            strategy_key = build_strategy_key(config)
            window_metrics = {
                label: summarize_window_returns(master_df.loc[master_df["window_label"] == label, f"return__{strategy_key}"])
                for label in ["train", "test", "review"]
            }
            selection_status = "baseline" if strategy_key == BASELINE_CONFIG_KEY else "candidate"
            rows.append(
                {
                    "fold_id": fold["fold_id"],
                    "config_key": strategy_key,
                    "hold_count": hold_count,
                    "entry_delay_days": delay_days,
                    "selection_status": selection_status,
                    **flatten_window_metrics(window_metrics),
                    "selection_score": np.nan if selection_status == "baseline" else compute_selection_score(window_metrics),
                    "review__mean_avg_cash_weight": float(pd.to_numeric(
                        master_df.loc[master_df["window_label"] == "review", f"avg_cash_weight__{strategy_key}"],
                        errors="coerce",
                    ).mean()),
                    "review__mean_invested_stock_count": float(pd.to_numeric(
                        master_df.loc[master_df["window_label"] == "review", f"invested_stock_count__{strategy_key}"],
                        errors="coerce",
                    ).mean()),
                }
            )
    return rows


def choose_best_configs(config_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    df = pd.DataFrame(config_rows)
    chosen_rows: list[dict[str, object]] = []
    for fold_id, fold_df in df.groupby("fold_id", sort=True):
        baseline_row = fold_df[fold_df["config_key"] == BASELINE_CONFIG_KEY].iloc[0].to_dict()
        candidate_df = fold_df[
            (fold_df["config_key"] != BASELINE_CONFIG_KEY)
            & (fold_df["test__coverage_ratio"] >= 1.0)
            & (fold_df["review__coverage_ratio"] >= 1.0)
            & pd.to_numeric(fold_df["selection_score"], errors="coerce").notna()
        ].copy()
        if candidate_df.empty:
            baseline_row["selection_status"] = "chosen_baseline_no_candidate"
            chosen_rows.append(baseline_row)
            continue

        baseline_train = pd.to_numeric(pd.Series([baseline_row["train__cum_portfolio_return"]]), errors="coerce").iloc[0]
        baseline_test = pd.to_numeric(pd.Series([baseline_row["test__cum_portfolio_return"]]), errors="coerce").iloc[0]
        candidate_df["train__cum_portfolio_return"] = pd.to_numeric(candidate_df["train__cum_portfolio_return"], errors="coerce")
        candidate_df["test__cum_portfolio_return"] = pd.to_numeric(candidate_df["test__cum_portfolio_return"], errors="coerce")
        admissible = candidate_df[
            (candidate_df["train__cum_portfolio_return"] >= baseline_train)
            & (candidate_df["test__cum_portfolio_return"] > baseline_test)
        ].copy()
        pool = admissible if not admissible.empty else candidate_df
        pool["selection_score"] = pd.to_numeric(pool["selection_score"], errors="coerce")
        chosen = pool.sort_values(
            ["selection_score", "test__cum_portfolio_return", "train__cum_portfolio_return"],
            ascending=[False, False, False],
        ).iloc[0].to_dict()
        chosen["selection_status"] = "chosen_overlay" if not admissible.empty else "chosen_best_available"
        chosen_rows.append(chosen)
    return chosen_rows


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


def write_summary(config_rows: list[dict[str, object]], chosen_rows: list[dict[str, object]]) -> None:
    config_df = pd.DataFrame(config_rows)
    chosen_df = pd.DataFrame(chosen_rows)
    lines = [
        "# Pure Fundamental Execution Rolling Validation V1",
        "",
        "Protocol:",
        "- factor engine stays fixed at annual pure-fundamental `base_core_7 + combo__ic_weight_train`",
        "- this branch changes only execution-layer parameters",
        "- stock selection uses direct score ranking instead of changing factor definitions",
        "- tested hold counts = `8 / 10 / 12`",
        "- tested entry delays = `0 / 5` trading days after each rebalance date",
        "- capital not yet deployed during delay stays in cash with `0` return",
        "",
        f"Baseline config: `{BASELINE_CONFIG_KEY}`",
        "",
        "Chosen fold results:",
    ]

    for _, row in chosen_df.sort_values("fold_id").iterrows():
        lines.append(
            f"- `{row['fold_id']}` | status=`{row['selection_status']}` | config=`{row['config_key']}` | "
            f"hold_count=`{row.get('hold_count', 'n/a')}` | entry_delay_days=`{row.get('entry_delay_days', 'n/a')}` | "
            f"train_cum=`{format_float(row.get('train__cum_portfolio_return'))}` | "
            f"test_cum=`{format_float(row.get('test__cum_portfolio_return'))}` | "
            f"review_cum=`{format_float(row.get('review__cum_portfolio_return'))}` | "
            f"review_mean_cash=`{format_float(row.get('review__mean_avg_cash_weight'))}` | "
            f"review_mean_invested_stock_count=`{format_float(row.get('review__mean_invested_stock_count'))}`"
        )

    candidate_df = config_df[config_df["config_key"] != BASELINE_CONFIG_KEY].copy()
    if not candidate_df.empty:
        summary_df = (
            candidate_df.groupby(["config_key", "hold_count", "entry_delay_days"], dropna=False)
            .agg(
                folds=("fold_id", "count"),
                mean_train_cum=("train__cum_portfolio_return", "mean"),
                mean_test_cum=("test__cum_portfolio_return", "mean"),
                mean_review_cum=("review__cum_portfolio_return", "mean"),
                mean_review_cash=("review__mean_avg_cash_weight", "mean"),
            )
            .reset_index()
            .sort_values(["mean_test_cum", "mean_train_cum"], ascending=[False, False])
        )
        lines.extend(["", "Mean config ranking:"])
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['config_key']}` | folds=`{int(row['folds'])}` | "
                f"mean_train_cum=`{format_float(row['mean_train_cum'])}` | "
                f"mean_test_cum=`{format_float(row['mean_test_cum'])}` | "
                f"mean_review_cum=`{format_float(row['mean_review_cum'])}` | "
                f"mean_review_cash=`{format_float(row['mean_review_cash'])}`"
            )

    baseline_df = config_df[config_df["config_key"] == BASELINE_CONFIG_KEY].copy()
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
            f"- [{OUTPUT_CHOSEN_PATH.name}]({OUTPUT_CHOSEN_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    panel_df["rebalance_date"] = pd.to_datetime(panel_df["rebalance_date"])
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)
    base_rows, enhanced_rows, universe_rows = load_factor_universe()

    daily_cache: dict[str, pd.DataFrame] = {}
    for code in sorted(panel_df["code"].astype(str).unique()):
        daily_cache[code] = load_daily_path(code)

    config_rows: list[dict[str, object]] = []
    for fold in folds:
        master_df = build_master_frame(
            panel_df=panel_df,
            fold=fold,
            base_rows=base_rows,
            enhanced_rows=enhanced_rows,
            universe_rows=universe_rows,
            daily_cache=daily_cache,
        )
        if master_df.empty:
            continue
        config_rows.extend(build_config_rows(master_df, fold))

    chosen_rows = choose_best_configs(config_rows)
    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_csv(OUTPUT_CHOSEN_PATH, chosen_rows)
    write_summary(config_rows, chosen_rows)
    print(OUTPUT_CONFIG_RESULTS_PATH)
    print(OUTPUT_CHOSEN_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
