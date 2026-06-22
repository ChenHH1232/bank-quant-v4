from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    add_combo_scores,
    build_scored_panel,
    evaluate_factor_window,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
)
from build_base_core_6_robustness_validation_v1 import (
    REVIEW_YEAR_COUNT,
    build_yearly_folds_custom,
    flatten_window_metrics,
    format_float,
    get_aligned_row,
    load_daily_path,
    summarize_window_returns,
)


SCRIPT_DIR = Path(__file__).resolve().parent

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1_config_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1.md"

PROFITABILITY_FACTORS = [
    "indicator__roe",
    "indicator__eps",
]
QUALITY_FACTORS = [
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]
TARGET_FACTOR_NAMES = PROFITABILITY_FACTORS + QUALITY_FACTORS

TRAIN_YEAR_COUNT = 5
TEST_YEAR_COUNT = 2
HOLD_COUNT = 8


def build_variant_base_rows(metadata_map: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for factor_name in TARGET_FACTOR_NAMES:
        row = metadata_map[factor_name].copy()
        row["layer"] = "base_core"
        rows.append(row)
    return rows


def evaluate_factor_map(
    panel_df: pd.DataFrame,
    factor_rows: list[dict[str, str]],
    fold: dict[str, object],
) -> dict[str, dict[str, object]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)
    out: dict[str, dict[str, object]] = {}
    for factor_row in factor_rows:
        out[factor_row["factor_name"]] = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
    return out


def simulate_period_daily_returns(
    top_codes: list[str],
    rebalance_date: pd.Timestamp,
    next_rebalance_date: pd.Timestamp,
    daily_cache: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, float]]:
    if not top_codes:
        return pd.DataFrame(columns=["day", "daily_return", "cash_weight"]), {"avg_cash_weight": np.nan, "invested_stock_count": 0}

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
        return pd.DataFrame(columns=["day", "daily_return", "cash_weight"]), {"avg_cash_weight": np.nan, "invested_stock_count": 0}

    rows: list[dict[str, object]] = []
    for day in sorted(all_days):
        portfolio_return = 0.0
        active_weight_sum = 0.0
        for _, day_map in stock_windows.items():
            daily_return = day_map.get(day)
            if daily_return is None:
                continue
            if pd.notna(daily_return):
                portfolio_return += base_weight * float(daily_return)
            active_weight_sum += base_weight
        rows.append(
            {
                "day": pd.Timestamp(day),
                "daily_return": portfolio_return,
                "cash_weight": max(0.0, 1.0 - active_weight_sum),
            }
        )

    daily_df = pd.DataFrame(rows)
    if daily_df.empty:
        return pd.DataFrame(columns=["day", "daily_return", "cash_weight"]), {"avg_cash_weight": np.nan, "invested_stock_count": 0}

    metrics = {
        "avg_cash_weight": float(pd.to_numeric(daily_df["cash_weight"], errors="coerce").mean()),
        "invested_stock_count": int(len(stock_windows)),
    }
    return daily_df, metrics


def apply_group_tilt_scores(
    scored_df: pd.DataFrame,
    profitability_weight: float,
    quality_weight: float,
) -> pd.DataFrame:
    df = scored_df.copy()
    profit_adj_cols = [f"adj__{name}" for name in PROFITABILITY_FACTORS if f"adj__{name}" in df.columns]
    quality_adj_cols = [f"adj__{name}" for name in QUALITY_FACTORS if f"adj__{name}" in df.columns]
    if not profit_adj_cols or not quality_adj_cols:
        return pd.DataFrame()

    df["profitability_score_raw"] = df[profit_adj_cols].mean(axis=1, skipna=True)
    df["quality_score_raw"] = df[quality_adj_cols].mean(axis=1, skipna=True)
    profit_count = df[profit_adj_cols].notna().sum(axis=1)
    quality_count = df[quality_adj_cols].notna().sum(axis=1)
    df["profitability_score"] = df["profitability_score_raw"].where(profit_count > 0, np.nan)
    df["quality_score"] = df["quality_score_raw"].where(quality_count > 0, np.nan)
    df["final_score"] = profitability_weight * df["profitability_score"] + quality_weight * df["quality_score"]
    df = df.dropna(subset=["final_score"]).copy()
    return df


def build_sleeve_frames(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    factor_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)
    context_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
        panel_df[context_mask].copy(),
        factor_rows,
        train_mask[context_mask],
    )
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    scored_df["rebalance_date"] = pd.to_datetime(scored_df["rebalance_date"])
    all_dates = sorted(scored_df["rebalance_date"].drop_duplicates())
    date_to_next = {date: all_dates[idx + 1] for idx, date in enumerate(all_dates[:-1])}

    period_rows: list[dict[str, object]] = []
    profit_daily_rows: list[pd.DataFrame] = []
    quality_daily_rows: list[pd.DataFrame] = []
    profit_nav_value = 1.0
    quality_nav_value = 1.0

    for rebalance_date, group in scored_df.groupby("rebalance_date"):
        rebalance_date = pd.Timestamp(rebalance_date)
        next_rebalance_date = date_to_next.get(rebalance_date)
        if next_rebalance_date is None:
            continue

        profit_df = apply_group_tilt_scores(group, profitability_weight=1.0, quality_weight=0.0)
        quality_df = apply_group_tilt_scores(group, profitability_weight=0.0, quality_weight=1.0)
        if profit_df.empty or quality_df.empty:
            continue

        profit_top_codes = [str(code) for code in profit_df.sort_values("final_score", ascending=False).head(HOLD_COUNT)["code"].astype(str).tolist()]
        quality_top_codes = [str(code) for code in quality_df.sort_values("final_score", ascending=False).head(HOLD_COUNT)["code"].astype(str).tolist()]

        profit_daily_df, profit_metrics = simulate_period_daily_returns(
            top_codes=profit_top_codes,
            rebalance_date=rebalance_date,
            next_rebalance_date=next_rebalance_date,
            daily_cache=daily_cache,
        )
        quality_daily_df, quality_metrics = simulate_period_daily_returns(
            top_codes=quality_top_codes,
            rebalance_date=rebalance_date,
            next_rebalance_date=next_rebalance_date,
            daily_cache=daily_cache,
        )
        if profit_daily_df.empty or quality_daily_df.empty:
            continue

        window_label = (
            "train" if rebalance_date < test_start else ("test" if rebalance_date < review_start else "review")
        )

        profit_daily_df = profit_daily_df.sort_values("day").reset_index(drop=True)
        profit_daily_df["fold_id"] = fold["fold_id"]
        profit_daily_df["rebalance_date"] = rebalance_date
        profit_daily_df["window_label"] = window_label
        profit_daily_df["sleeve_name"] = "profitability"
        profit_daily_df["nav"] = profit_nav_value * (1.0 + pd.to_numeric(profit_daily_df["daily_return"], errors="coerce")).cumprod()
        profit_nav_value = float(profit_daily_df["nav"].iloc[-1])
        profit_daily_rows.append(profit_daily_df)

        quality_daily_df = quality_daily_df.sort_values("day").reset_index(drop=True)
        quality_daily_df["fold_id"] = fold["fold_id"]
        quality_daily_df["rebalance_date"] = rebalance_date
        quality_daily_df["window_label"] = window_label
        quality_daily_df["sleeve_name"] = "quality"
        quality_daily_df["nav"] = quality_nav_value * (1.0 + pd.to_numeric(quality_daily_df["daily_return"], errors="coerce")).cumprod()
        quality_nav_value = float(quality_daily_df["nav"].iloc[-1])
        quality_daily_rows.append(quality_daily_df)

        period_rows.append(
            {
                "fold_id": fold["fold_id"],
                "rebalance_date": rebalance_date,
                "next_rebalance_date": next_rebalance_date,
                "window_label": window_label,
                "profitability_return": float((1.0 + pd.to_numeric(profit_daily_df["daily_return"], errors="coerce")).prod() - 1.0),
                "quality_return": float((1.0 + pd.to_numeric(quality_daily_df["daily_return"], errors="coerce")).prod() - 1.0),
                "profitability_avg_cash_weight": profit_metrics["avg_cash_weight"],
                "quality_avg_cash_weight": quality_metrics["avg_cash_weight"],
            }
        )

    if not period_rows or not profit_daily_rows or not quality_daily_rows:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    return (
        pd.DataFrame(period_rows).sort_values("rebalance_date").reset_index(drop=True),
        pd.concat(profit_daily_rows, ignore_index=True).sort_values("day").reset_index(drop=True),
        pd.concat(quality_daily_rows, ignore_index=True).sort_values("day").reset_index(drop=True),
    )


def resolve_monthly_tilt(
    rule_name: str,
    profit_nav_df: pd.DataFrame,
    quality_nav_df: pd.DataFrame,
    decision_date: pd.Timestamp,
) -> dict[str, object]:
    current_day = decision_date - pd.Timedelta(days=1)
    p_curr_row = profit_nav_df.loc[profit_nav_df["day"] <= current_day].tail(1)
    q_curr_row = quality_nav_df.loc[quality_nav_df["day"] <= current_day].tail(1)
    if p_curr_row.empty or q_curr_row.empty:
        return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "fallback_no_nav", "rel_1m": np.nan, "rel_3m": np.nan}

    p_curr_nav = float(p_curr_row["nav"].iloc[0])
    q_curr_nav = float(q_curr_row["nav"].iloc[0])
    if p_curr_nav <= 0 or q_curr_nav <= 0:
        return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "fallback_bad_nav", "rel_1m": np.nan, "rel_3m": np.nan}

    def calc_rel(months: int) -> float:
        lookback_day = current_day - pd.DateOffset(months=months)
        p_prev_row = profit_nav_df.loc[profit_nav_df["day"] <= lookback_day].tail(1)
        q_prev_row = quality_nav_df.loc[quality_nav_df["day"] <= lookback_day].tail(1)
        if p_prev_row.empty or q_prev_row.empty:
            return np.nan
        p_prev_nav = float(p_prev_row["nav"].iloc[0])
        q_prev_nav = float(q_prev_row["nav"].iloc[0])
        if p_prev_nav <= 0 or q_prev_nav <= 0:
            return np.nan
        ratio_now = p_curr_nav / q_curr_nav
        ratio_prev = p_prev_nav / q_prev_nav
        if ratio_prev <= 0:
            return np.nan
        return float(ratio_now / ratio_prev - 1.0)

    rel_1m = calc_rel(1)
    rel_3m = calc_rel(3)

    if rule_name == "equal_50_50":
        return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_default", "rel_1m": rel_1m, "rel_3m": rel_3m}
    if rule_name == "profit_60_if_rel_1m_gt_0_else_quality_60":
        if pd.notna(rel_1m) and rel_1m > 0:
            return {"profitability_weight": 0.6, "quality_weight": 0.4, "reason": "profit_rel_1m_gt_0", "rel_1m": rel_1m, "rel_3m": rel_3m}
        return {"profitability_weight": 0.4, "quality_weight": 0.6, "reason": "quality_fallback", "rel_1m": rel_1m, "rel_3m": rel_3m}
    if rule_name == "profit_70_if_rel_3m_gt_0_else_quality_70":
        if pd.notna(rel_3m) and rel_3m > 0:
            return {"profitability_weight": 0.7, "quality_weight": 0.3, "reason": "profit_rel_3m_gt_0", "rel_1m": rel_1m, "rel_3m": rel_3m}
        return {"profitability_weight": 0.3, "quality_weight": 0.7, "reason": "quality_fallback", "rel_1m": rel_1m, "rel_3m": rel_3m}
    if rule_name == "profit_70_if_rel_3m_gt_2pct_else_quality_60":
        if pd.notna(rel_3m) and rel_3m > 0.02:
            return {"profitability_weight": 0.7, "quality_weight": 0.3, "reason": "profit_rel_3m_gt_2pct", "rel_1m": rel_1m, "rel_3m": rel_3m}
        return {"profitability_weight": 0.4, "quality_weight": 0.6, "reason": "quality_fallback", "rel_1m": rel_1m, "rel_3m": rel_3m}
    raise ValueError(f"unknown rule: {rule_name}")


def build_config_rows(
    panel_df: pd.DataFrame,
    may_dates: list[pd.Timestamp],
    factor_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    folds = build_yearly_folds_custom(
        may_dates=may_dates,
        train_year_count=TRAIN_YEAR_COUNT,
        test_year_count=TEST_YEAR_COUNT,
        review_year_count=REVIEW_YEAR_COUNT,
    )
    rules = [
        "equal_50_50",
        "profit_60_if_rel_1m_gt_0_else_quality_60",
        "profit_70_if_rel_3m_gt_0_else_quality_70",
        "profit_70_if_rel_3m_gt_2pct_else_quality_60",
    ]

    rows: list[dict[str, object]] = []
    for fold in folds:
        period_df, profit_nav_df, quality_nav_df = build_sleeve_frames(panel_df, fold, factor_rows, daily_cache)
        if period_df.empty or profit_nav_df.empty or quality_nav_df.empty:
            continue

        for rule_name in rules:
            chosen_rows: list[dict[str, object]] = []
            for _, period_row in period_df.iterrows():
                decision_date = pd.Timestamp(period_row["rebalance_date"])
                tilt = resolve_monthly_tilt(rule_name, profit_nav_df, quality_nav_df, decision_date)
                profitability_weight = float(tilt["profitability_weight"])
                quality_weight = float(tilt["quality_weight"])
                portfolio_return = (
                    profitability_weight * float(period_row["profitability_return"])
                    + quality_weight * float(period_row["quality_return"])
                )
                chosen_rows.append(
                    {
                        "rebalance_date": decision_date,
                        "window_label": period_row["window_label"],
                        f"return__top_{HOLD_COUNT:02d}": portfolio_return,
                        "profitability_weight": profitability_weight,
                        "quality_weight": quality_weight,
                        "choice_reason": tilt["reason"],
                        "rel_1m": tilt["rel_1m"],
                        "rel_3m": tilt["rel_3m"],
                    }
                )

            chosen_df = pd.DataFrame(chosen_rows)
            window_metrics = {
                label: summarize_window_returns(
                    chosen_df.loc[chosen_df["window_label"] == label, f"return__top_{HOLD_COUNT:02d}"]
                )
                for label in ["train", "test", "review"]
            }
            rows.append(
                {
                    "fold_id": fold["fold_id"],
                    "config_key": f"monthly_relative_tilt__{rule_name}",
                    "rule_name": rule_name,
                    "mean_profitability_weight": float(pd.to_numeric(chosen_df["profitability_weight"], errors="coerce").mean()),
                    "mean_quality_weight": float(pd.to_numeric(chosen_df["quality_weight"], errors="coerce").mean()),
                    "mean_rel_1m": float(pd.to_numeric(chosen_df["rel_1m"], errors="coerce").mean()),
                    "mean_rel_3m": float(pd.to_numeric(chosen_df["rel_3m"], errors="coerce").mean()),
                    **flatten_window_metrics(window_metrics),
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


def write_summary(config_rows: list[dict[str, object]]) -> None:
    config_df = pd.DataFrame(config_rows)
    if config_df.empty:
        OUTPUT_SUMMARY_PATH.write_text("# Base Core 6 Monthly Relative Momentum Tilt Rolling Validation V1\n\n- no rows\n", encoding="utf-8")
        return

    summary_df = (
        config_df.groupby(["config_key", "rule_name"], dropna=False)
        .agg(
            folds=("fold_id", "count"),
            mean_train_cum=("train__cum_portfolio_return", "mean"),
            mean_test_cum=("test__cum_portfolio_return", "mean"),
            mean_review_cum=("review__cum_portfolio_return", "mean"),
            mean_profitability_weight=("mean_profitability_weight", "mean"),
            mean_quality_weight=("mean_quality_weight", "mean"),
            mean_rel_1m=("mean_rel_1m", "mean"),
            mean_rel_3m=("mean_rel_3m", "mean"),
        )
        .reset_index()
    )
    baseline_test = float(summary_df.loc[summary_df["rule_name"] == "equal_50_50", "mean_test_cum"].iloc[0])
    baseline_review = float(summary_df.loc[summary_df["rule_name"] == "equal_50_50", "mean_review_cum"].iloc[0])
    summary_df["delta_test_vs_equal"] = summary_df["mean_test_cum"] - baseline_test
    summary_df["delta_review_vs_equal"] = summary_df["mean_review_cum"] - baseline_review
    summary_df = summary_df.sort_values(
        ["delta_review_vs_equal", "delta_test_vs_equal", "mean_train_cum"],
        ascending=[False, False, False],
    )

    lines = [
        "# Base Core 6 Monthly Relative Momentum Tilt Rolling Validation V1",
        "",
        "Protocol:",
        "- keep profitability and quality inside the same pure-fundamental shell",
        "- build separate daily NAV paths for the profitability sleeve and the quality sleeve",
        "- update their relative momentum monthly and let the next rebalance lean toward the stronger sleeve",
        "- this tests dynamic tilt, not binary style replacement",
        "",
        "Rules tested:",
        "- `equal_50_50`",
        "- `profit_60_if_rel_1m_gt_0_else_quality_60`",
        "- `profit_70_if_rel_3m_gt_0_else_quality_70`",
        "- `profit_70_if_rel_3m_gt_2pct_else_quality_60`",
        "",
        "Ranking by mean review return:",
    ]
    for _, row in summary_df.iterrows():
        lines.append(
            f"- `{row['rule_name']}` | folds=`{int(row['folds'])}` | "
            f"mean_train_cum=`{format_float(row['mean_train_cum'])}` | "
            f"mean_test_cum=`{format_float(row['mean_test_cum'])}` | "
            f"mean_review_cum=`{format_float(row['mean_review_cum'])}` | "
            f"delta_test_vs_equal=`{format_float(row['delta_test_vs_equal'])}` | "
            f"delta_review_vs_equal=`{format_float(row['delta_review_vs_equal'])}` | "
            f"mean_profitability_weight=`{format_float(row['mean_profitability_weight'])}` | "
            f"mean_quality_weight=`{format_float(row['mean_quality_weight'])}` | "
            f"mean_rel_1m=`{format_float(row['mean_rel_1m'])}` | "
            f"mean_rel_3m=`{format_float(row['mean_rel_3m'])}`"
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
    _, _, universe_rows = load_factor_universe()
    metadata_map = {row["factor_name"]: row for row in universe_rows}
    factor_rows = build_variant_base_rows(metadata_map)
    may_dates = get_may_rebalance_dates(panel_df)

    daily_cache: dict[str, pd.DataFrame] = {}
    for code in sorted(panel_df["code"].astype(str).unique()):
        daily_cache[code] = load_daily_path(code)

    config_rows = build_config_rows(
        panel_df=panel_df,
        may_dates=may_dates,
        factor_rows=factor_rows,
        daily_cache=daily_cache,
    )
    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_summary(config_rows)
    print(OUTPUT_CONFIG_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
