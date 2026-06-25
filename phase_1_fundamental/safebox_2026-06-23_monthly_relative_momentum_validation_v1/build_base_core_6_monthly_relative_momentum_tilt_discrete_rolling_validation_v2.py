from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    add_combo_scores,
    build_scored_panel,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
)
from build_base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1 import (
    HOLD_COUNT,
    PROFITABILITY_FACTORS,
    QUALITY_FACTORS,
    build_sleeve_frames,
    build_variant_base_rows,
)
from build_base_core_6_robustness_validation_v1 import (
    REVIEW_YEAR_COUNT,
    build_yearly_folds_custom,
    flatten_window_metrics,
    format_float,
    summarize_window_returns,
    load_daily_path,
)


SCRIPT_DIR = Path(__file__).resolve().parent

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2_config_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2.md"

TRAIN_YEAR_COUNT = 5
TEST_YEAR_COUNT = 2


def resolve_discrete_tilt(
    rule_name: str,
    profit_nav_df: pd.DataFrame,
    quality_nav_df: pd.DataFrame,
    decision_date: pd.Timestamp,
) -> dict[str, object]:
    current_day = decision_date - pd.Timedelta(days=1)
    p_curr_row = profit_nav_df.loc[profit_nav_df["day"] <= current_day].tail(1)
    q_curr_row = quality_nav_df.loc[quality_nav_df["day"] <= current_day].tail(1)
    if p_curr_row.empty or q_curr_row.empty:
        return {
            "profitability_weight": 0.5,
            "quality_weight": 0.5,
            "reason": "fallback_no_nav",
            "rel_1m": np.nan,
            "rel_3m": np.nan,
            "state": "50_50",
        }

    p_curr_nav = float(p_curr_row["nav"].iloc[0])
    q_curr_nav = float(q_curr_row["nav"].iloc[0])
    if p_curr_nav <= 0 or q_curr_nav <= 0:
        return {
            "profitability_weight": 0.5,
            "quality_weight": 0.5,
            "reason": "fallback_bad_nav",
            "rel_1m": np.nan,
            "rel_3m": np.nan,
            "state": "50_50",
        }

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
        return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_default", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "50_50"}
    if rule_name == "quality_60_if_rel_3m_le_0_else_50":
        if pd.notna(rel_3m) and rel_3m <= 0:
            return {"profitability_weight": 0.4, "quality_weight": 0.6, "reason": "quality_60_rel_3m_le_0", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "40_60"}
        return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_fallback", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "50_50"}
    if rule_name == "quality_70_if_rel_3m_le_0_else_50":
        if pd.notna(rel_3m) and rel_3m <= 0:
            return {"profitability_weight": 0.3, "quality_weight": 0.7, "reason": "quality_70_rel_3m_le_0", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "30_70"}
        return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_fallback", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "50_50"}
    if rule_name == "quality_ladder_50_40_30_by_rel_3m":
        if pd.isna(rel_3m):
            return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_fallback", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "50_50"}
        if rel_3m <= -0.02:
            return {"profitability_weight": 0.3, "quality_weight": 0.7, "reason": "quality_70_rel_3m_le_neg2pct", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "30_70"}
        if rel_3m <= 0:
            return {"profitability_weight": 0.4, "quality_weight": 0.6, "reason": "quality_60_rel_3m_le_0", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "40_60"}
        return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_rel_3m_gt_0", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "50_50"}
    if rule_name == "symmetric_ladder_70_50_30_by_rel_3m":
        if pd.isna(rel_3m):
            return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_fallback", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "50_50"}
        if rel_3m >= 0.02:
            return {"profitability_weight": 0.7, "quality_weight": 0.3, "reason": "profit_70_rel_3m_ge_2pct", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "70_30"}
        if rel_3m > 0:
            return {"profitability_weight": 0.5, "quality_weight": 0.5, "reason": "equal_rel_3m_gt_0", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "50_50"}
        if rel_3m <= -0.02:
            return {"profitability_weight": 0.3, "quality_weight": 0.7, "reason": "quality_70_rel_3m_le_neg2pct", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "30_70"}
        return {"profitability_weight": 0.4, "quality_weight": 0.6, "reason": "quality_60_rel_3m_le_0", "rel_1m": rel_1m, "rel_3m": rel_3m, "state": "40_60"}
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
        "quality_60_if_rel_3m_le_0_else_50",
        "quality_70_if_rel_3m_le_0_else_50",
        "quality_ladder_50_40_30_by_rel_3m",
        "symmetric_ladder_70_50_30_by_rel_3m",
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
                tilt = resolve_discrete_tilt(rule_name, profit_nav_df, quality_nav_df, decision_date)
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
                        "tilt_state": tilt["state"],
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
                    "config_key": f"monthly_relative_tilt_discrete__{rule_name}",
                    "rule_name": rule_name,
                    "mean_profitability_weight": float(pd.to_numeric(chosen_df["profitability_weight"], errors="coerce").mean()),
                    "mean_quality_weight": float(pd.to_numeric(chosen_df["quality_weight"], errors="coerce").mean()),
                    "mean_rel_1m": float(pd.to_numeric(chosen_df["rel_1m"], errors="coerce").mean()),
                    "mean_rel_3m": float(pd.to_numeric(chosen_df["rel_3m"], errors="coerce").mean()),
                    "count_state_50_50": int((chosen_df["tilt_state"] == "50_50").sum()),
                    "count_state_40_60": int((chosen_df["tilt_state"] == "40_60").sum()),
                    "count_state_30_70": int((chosen_df["tilt_state"] == "30_70").sum()),
                    "count_state_70_30": int((chosen_df["tilt_state"] == "70_30").sum()),
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
        OUTPUT_SUMMARY_PATH.write_text("# Base Core 6 Monthly Relative Momentum Tilt Discrete Rolling Validation V2\n\n- no rows\n", encoding="utf-8")
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
            mean_count_state_50_50=("count_state_50_50", "mean"),
            mean_count_state_40_60=("count_state_40_60", "mean"),
            mean_count_state_30_70=("count_state_30_70", "mean"),
            mean_count_state_70_30=("count_state_70_30", "mean"),
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
        "# Base Core 6 Monthly Relative Momentum Tilt Discrete Rolling Validation V2",
        "",
        "Protocol:",
        "- rebalance only on the strategy's existing rebalance dates",
        "- monthly relative momentum is used only as a state signal before each rebalance decision",
        "- tested discrete tilt buckets centered on `50/50`, then stepping toward `40/60` or `30/70` when profitability relative momentum weakens",
        f"- profitability factors = `{', '.join(PROFITABILITY_FACTORS)}`",
        f"- quality factors = `{', '.join(QUALITY_FACTORS)}`",
        "",
        "Rules tested:",
        "- `equal_50_50`",
        "- `quality_60_if_rel_3m_le_0_else_50`",
        "- `quality_70_if_rel_3m_le_0_else_50`",
        "- `quality_ladder_50_40_30_by_rel_3m`",
        "- `symmetric_ladder_70_50_30_by_rel_3m`",
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
            f"state_50_50=`{format_float(row['mean_count_state_50_50'])}` | "
            f"state_40_60=`{format_float(row['mean_count_state_40_60'])}` | "
            f"state_30_70=`{format_float(row['mean_count_state_30_70'])}` | "
            f"state_70_30=`{format_float(row['mean_count_state_70_30'])}`"
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
