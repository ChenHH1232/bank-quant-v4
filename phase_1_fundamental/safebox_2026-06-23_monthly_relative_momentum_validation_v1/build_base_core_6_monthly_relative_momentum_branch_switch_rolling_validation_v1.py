from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_BASE,
    add_combo_scores,
    build_scored_panel,
    build_scenario_rows,
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

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1_config_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1.md"

BRANCH_A_FACTOR_NAMES = [
    "indicator__roe",
    "indicator__eps",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]
BRANCH_B_FACTOR_NAMES = [
    "indicator__roe",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
    "bank_indicator__core_level_capital_adequacy_ratio",
]

TRAIN_YEAR_COUNT = 5
TEST_YEAR_COUNT = 2
COMBO_NAME = "combo__ic_weight_train"
HOLD_COUNT = 8


def build_variant_rows(
    metadata_map: dict[str, dict[str, str]],
    factor_names: list[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for factor_name in factor_names:
        row = metadata_map[factor_name].copy()
        row["layer"] = "base_core"
        rows.append(row)
    return rows


def select_factor_rows_variant(
    panel_df: pd.DataFrame,
    variant_rows: list[dict[str, str]],
    fold: dict[str, object],
) -> list[dict[str, str]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)

    selected_names: set[str] = set()
    for factor_row in variant_rows:
        evaluated = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
        if int(evaluated["keep_flag"]) == 1:
            selected_names.add(str(factor_row["factor_name"]))
    return [row for row in variant_rows if row["factor_name"] in selected_names]


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


def build_branch_frames(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    variant_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
    branch_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)
    context_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

    selected_rows = select_factor_rows_variant(panel_df, variant_rows, fold)
    scenario_map = build_scenario_rows(selected_rows, variant_rows, [])
    factor_specs = scenario_map.get(SCENARIO_BASE, [])
    if not factor_specs:
        return pd.DataFrame(), pd.DataFrame()

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
        panel_df[context_mask].copy(),
        factor_specs,
        train_mask[context_mask],
    )
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    scored_df["rebalance_date"] = pd.to_datetime(scored_df["rebalance_date"])
    all_dates = sorted(scored_df["rebalance_date"].drop_duplicates())
    date_to_next = {date: all_dates[idx + 1] for idx, date in enumerate(all_dates[:-1])}

    period_rows: list[dict[str, object]] = []
    daily_rows: list[pd.DataFrame] = []
    nav_value = 1.0

    for rebalance_date, group in scored_df.groupby("rebalance_date"):
        rebalance_date = pd.Timestamp(rebalance_date)
        next_rebalance_date = date_to_next.get(rebalance_date)
        if next_rebalance_date is None:
            continue
        group = group.dropna(subset=[COMBO_NAME]).copy()
        if group.empty:
            continue
        top_group = group.sort_values(COMBO_NAME, ascending=False).head(HOLD_COUNT).copy()
        top_codes = [str(code) for code in top_group["code"].astype(str).tolist()]
        daily_df, metrics = simulate_period_daily_returns(
            top_codes=top_codes,
            rebalance_date=rebalance_date,
            next_rebalance_date=next_rebalance_date,
            daily_cache=daily_cache,
        )
        if daily_df.empty:
            continue

        daily_df = daily_df.sort_values("day").reset_index(drop=True)
        daily_df["branch_name"] = branch_name
        daily_df["fold_id"] = fold["fold_id"]
        daily_df["rebalance_date"] = rebalance_date
        daily_df["next_rebalance_date"] = next_rebalance_date
        daily_df["window_label"] = (
            "train" if rebalance_date < test_start else ("test" if rebalance_date < review_start else "review")
        )
        daily_df["nav"] = nav_value * (1.0 + pd.to_numeric(daily_df["daily_return"], errors="coerce")).cumprod()
        nav_value = float(daily_df["nav"].iloc[-1])
        daily_rows.append(daily_df)

        period_rows.append(
            {
                "fold_id": fold["fold_id"],
                "branch_name": branch_name,
                "rebalance_date": rebalance_date,
                "next_rebalance_date": next_rebalance_date,
                "window_label": daily_df["window_label"].iloc[0],
                "selected_factor_count": int(len(factor_specs)),
                f"return__top_{HOLD_COUNT:02d}": float((1.0 + pd.to_numeric(daily_df["daily_return"], errors="coerce")).prod() - 1.0),
                f"avg_cash_weight__top_{HOLD_COUNT:02d}": metrics["avg_cash_weight"],
                f"invested_stock_count__top_{HOLD_COUNT:02d}": metrics["invested_stock_count"],
            }
        )

    if not period_rows or not daily_rows:
        return pd.DataFrame(), pd.DataFrame()

    period_df = pd.DataFrame(period_rows).sort_values("rebalance_date").reset_index(drop=True)
    daily_nav_df = pd.concat(daily_rows, ignore_index=True).sort_values("day").reset_index(drop=True)
    return period_df, daily_nav_df


def resolve_monthly_signal(
    rule_name: str,
    branch_a_nav: pd.DataFrame,
    branch_b_nav: pd.DataFrame,
    decision_date: pd.Timestamp,
) -> dict[str, object]:
    current_day = decision_date - pd.Timedelta(days=1)
    a_curr_row = branch_a_nav.loc[branch_a_nav["day"] <= current_day].tail(1)
    b_curr_row = branch_b_nav.loc[branch_b_nav["day"] <= current_day].tail(1)
    if a_curr_row.empty or b_curr_row.empty:
        return {"chosen_branch": "branch_a", "reason": "fallback_no_nav", "rel_1m": np.nan, "rel_3m": np.nan}

    a_curr_nav = float(a_curr_row["nav"].iloc[0])
    b_curr_nav = float(b_curr_row["nav"].iloc[0])
    if a_curr_nav <= 0 or b_curr_nav <= 0:
        return {"chosen_branch": "branch_a", "reason": "fallback_bad_nav", "rel_1m": np.nan, "rel_3m": np.nan}

    def calc_rel(months: int) -> float:
        lookback_day = current_day - pd.DateOffset(months=months)
        a_prev_row = branch_a_nav.loc[branch_a_nav["day"] <= lookback_day].tail(1)
        b_prev_row = branch_b_nav.loc[branch_b_nav["day"] <= lookback_day].tail(1)
        if a_prev_row.empty or b_prev_row.empty:
            return np.nan
        a_prev_nav = float(a_prev_row["nav"].iloc[0])
        b_prev_nav = float(b_prev_row["nav"].iloc[0])
        if a_prev_nav <= 0 or b_prev_nav <= 0:
            return np.nan
        ratio_now = b_curr_nav / a_curr_nav
        ratio_prev = b_prev_nav / a_prev_nav
        if ratio_prev <= 0:
            return np.nan
        return float(ratio_now / ratio_prev - 1.0)

    rel_1m = calc_rel(1)
    rel_3m = calc_rel(3)

    if rule_name == "branch_a_always":
        return {"chosen_branch": "branch_a", "reason": "fixed_a", "rel_1m": rel_1m, "rel_3m": rel_3m}
    if rule_name == "branch_b_always":
        return {"chosen_branch": "branch_b", "reason": "fixed_b", "rel_1m": rel_1m, "rel_3m": rel_3m}
    if rule_name == "branch_b_if_rel_1m_gt_0":
        chosen_branch = "branch_b" if pd.notna(rel_1m) and rel_1m > 0 else "branch_a"
        reason = "rel_1m_gt_0" if chosen_branch == "branch_b" else "fallback_a"
        return {"chosen_branch": chosen_branch, "reason": reason, "rel_1m": rel_1m, "rel_3m": rel_3m}
    if rule_name == "branch_b_if_rel_3m_gt_0":
        chosen_branch = "branch_b" if pd.notna(rel_3m) and rel_3m > 0 else "branch_a"
        reason = "rel_3m_gt_0" if chosen_branch == "branch_b" else "fallback_a"
        return {"chosen_branch": chosen_branch, "reason": reason, "rel_1m": rel_1m, "rel_3m": rel_3m}
    if rule_name == "branch_b_if_rel_3m_gt_2pct":
        chosen_branch = "branch_b" if pd.notna(rel_3m) and rel_3m > 0.02 else "branch_a"
        reason = "rel_3m_gt_2pct" if chosen_branch == "branch_b" else "fallback_a"
        return {"chosen_branch": chosen_branch, "reason": reason, "rel_1m": rel_1m, "rel_3m": rel_3m}
    raise ValueError(f"unknown rule: {rule_name}")


def build_config_rows(
    panel_df: pd.DataFrame,
    may_dates: list[pd.Timestamp],
    metadata_map: dict[str, dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
) -> list[dict[str, object]]:
    folds = build_yearly_folds_custom(
        may_dates=may_dates,
        train_year_count=TRAIN_YEAR_COUNT,
        test_year_count=TEST_YEAR_COUNT,
        review_year_count=REVIEW_YEAR_COUNT,
    )
    branch_a_rows = build_variant_rows(metadata_map, BRANCH_A_FACTOR_NAMES)
    branch_b_rows = build_variant_rows(metadata_map, BRANCH_B_FACTOR_NAMES)
    rules = [
        "branch_a_always",
        "branch_b_always",
        "branch_b_if_rel_1m_gt_0",
        "branch_b_if_rel_3m_gt_0",
        "branch_b_if_rel_3m_gt_2pct",
    ]

    rows: list[dict[str, object]] = []
    for fold in folds:
        branch_a_period_df, branch_a_nav_df = build_branch_frames(panel_df, fold, branch_a_rows, daily_cache, "branch_a")
        branch_b_period_df, branch_b_nav_df = build_branch_frames(panel_df, fold, branch_b_rows, daily_cache, "branch_b")
        if branch_a_period_df.empty or branch_b_period_df.empty or branch_a_nav_df.empty or branch_b_nav_df.empty:
            continue

        branch_a_period_df = branch_a_period_df.sort_values("rebalance_date").reset_index(drop=True)
        branch_b_period_df = branch_b_period_df.sort_values("rebalance_date").reset_index(drop=True)
        common_dates = sorted(set(branch_a_period_df["rebalance_date"]) & set(branch_b_period_df["rebalance_date"]))
        if not common_dates:
            continue

        for rule_name in rules:
            chosen_rows: list[dict[str, object]] = []
            branch_b_count = 0
            branch_a_count = 0
            for decision_date in common_dates:
                choice = resolve_monthly_signal(rule_name, branch_a_nav_df, branch_b_nav_df, pd.Timestamp(decision_date))
                if choice["chosen_branch"] == "branch_b":
                    branch_b_count += 1
                    selected = branch_b_period_df.loc[branch_b_period_df["rebalance_date"] == decision_date].iloc[0].to_dict()
                else:
                    branch_a_count += 1
                    selected = branch_a_period_df.loc[branch_a_period_df["rebalance_date"] == decision_date].iloc[0].to_dict()
                selected["chosen_branch"] = choice["chosen_branch"]
                selected["choice_reason"] = choice["reason"]
                selected["rel_1m"] = choice["rel_1m"]
                selected["rel_3m"] = choice["rel_3m"]
                chosen_rows.append(selected)

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
                    "config_key": f"monthly_relative_mom__{rule_name}",
                    "rule_name": rule_name,
                    "branch_b_period_count": branch_b_count,
                    "branch_a_period_count": branch_a_count,
                    "mean_selected_factor_count": float(pd.to_numeric(chosen_df["selected_factor_count"], errors="coerce").mean()),
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
        OUTPUT_SUMMARY_PATH.write_text("# Base Core 6 Monthly Relative Momentum Branch Switch Rolling Validation V1\n\n- no rows\n", encoding="utf-8")
        return

    summary_df = (
        config_df.groupby(["config_key", "rule_name"], dropna=False)
        .agg(
            folds=("fold_id", "count"),
            mean_train_cum=("train__cum_portfolio_return", "mean"),
            mean_test_cum=("test__cum_portfolio_return", "mean"),
            mean_review_cum=("review__cum_portfolio_return", "mean"),
            mean_branch_b_period_count=("branch_b_period_count", "mean"),
            mean_branch_a_period_count=("branch_a_period_count", "mean"),
            mean_rel_1m=("mean_rel_1m", "mean"),
            mean_rel_3m=("mean_rel_3m", "mean"),
        )
        .reset_index()
    )
    baseline_test = float(summary_df.loc[summary_df["rule_name"] == "branch_a_always", "mean_test_cum"].iloc[0])
    baseline_review = float(summary_df.loc[summary_df["rule_name"] == "branch_a_always", "mean_review_cum"].iloc[0])
    summary_df["delta_test_vs_branch_a"] = summary_df["mean_test_cum"] - baseline_test
    summary_df["delta_review_vs_branch_a"] = summary_df["mean_review_cum"] - baseline_review
    summary_df = summary_df.sort_values(
        ["delta_review_vs_branch_a", "delta_test_vs_branch_a", "mean_train_cum"],
        ascending=[False, False, False],
    )

    lines = [
        "# Base Core 6 Monthly Relative Momentum Branch Switch Rolling Validation V1",
        "",
        "Protocol:",
        "- branch A = balanced pure-fundamental `base_core_6 + top_08`",
        "- branch B = capital-quality side candidate `base_core_6 - indicator__eps + bank_indicator__core_level_capital_adequacy_ratio`",
        "- build daily NAV paths for both branches inside each fold",
        "- update relative momentum monthly from branch B versus branch A, but only apply the choice when the strategy reaches the next rebalance date",
        "- this tests whether monthly style strength can improve over annual one-shot branch switching",
        "",
        "Rules tested:",
        "- `branch_a_always`",
        "- `branch_b_always`",
        "- `branch_b_if_rel_1m_gt_0`",
        "- `branch_b_if_rel_3m_gt_0`",
        "- `branch_b_if_rel_3m_gt_2pct`",
        "",
        "Ranking by mean review return:",
    ]
    for _, row in summary_df.iterrows():
        lines.append(
            f"- `{row['rule_name']}` | folds=`{int(row['folds'])}` | "
            f"mean_train_cum=`{format_float(row['mean_train_cum'])}` | "
            f"mean_test_cum=`{format_float(row['mean_test_cum'])}` | "
            f"mean_review_cum=`{format_float(row['mean_review_cum'])}` | "
            f"delta_test_vs_branch_a=`{format_float(row['delta_test_vs_branch_a'])}` | "
            f"delta_review_vs_branch_a=`{format_float(row['delta_review_vs_branch_a'])}` | "
            f"mean_branch_b_period_count=`{format_float(row['mean_branch_b_period_count'])}` | "
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
    may_dates = get_may_rebalance_dates(panel_df)

    daily_cache: dict[str, pd.DataFrame] = {}
    for code in sorted(panel_df["code"].astype(str).unique()):
        daily_cache[code] = load_daily_path(code)

    config_rows = build_config_rows(
        panel_df=panel_df,
        may_dates=may_dates,
        metadata_map=metadata_map,
        daily_cache=daily_cache,
    )
    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_summary(config_rows)
    print(OUTPUT_CONFIG_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
