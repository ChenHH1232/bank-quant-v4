from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    COMBO_NAMES,
    SCENARIO_BASE,
    SCENARIO_ENHANCED,
    add_combo_scores,
    build_scored_panel,
    build_yearly_folds,
    evaluate_factor_window,
    format_metric,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
    summarize_combo,
    write_csv,
)


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_FOLDS_PATH = SCRIPT_DIR / "base_core_6_minus_log_total_assets_v1_folds.csv"
OUTPUT_SELECTION_PATH = SCRIPT_DIR / "base_core_6_minus_log_total_assets_v1_factor_selection.csv"
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "base_core_6_minus_log_total_assets_v1_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "base_core_6_minus_log_total_assets_v1.md"

EXCLUDED_FACTOR = "derived__log_total_assets"
TARGET_BASE_SET = [
    "indicator__roe",
    "indicator__eps",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]


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


def build_scenario_rows(
    selected_rows: list[dict[str, str]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    selected_names = {row["factor_name"] for row in selected_rows}
    base_selected = [row for row in base_rows if row["factor_name"] in selected_names]
    enhanced_selected = [row for row in enhanced_rows if row["factor_name"] in selected_names]
    return {
        SCENARIO_BASE: base_selected,
        SCENARIO_ENHANCED: enhanced_selected,
    }


def build_result_rows(
    panel_df: pd.DataFrame,
    folds: list[dict[str, object]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    result_rows: list[dict[str, object]] = []
    selection_rows: list[dict[str, object]] = []

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        test_start = pd.Timestamp(fold["test_start"])
        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

        selected_rows, fold_selection_rows = select_factor_rows_base6(
            panel_df,
            universe_rows,
            fold,
            base_rows,
            enhanced_rows,
        )
        selection_rows.extend(fold_selection_rows)
        scenario_map = build_scenario_rows(selected_rows, base_rows, enhanced_rows)

        for scenario_name, scenario_rows in scenario_map.items():
            if not scenario_rows:
                continue
            scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, scenario_rows, train_mask)
            scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
            for combo_name in COMBO_NAMES:
                result_rows.append(
                    summarize_combo(scored_df, fold, scenario_name, combo_name)
                    | {"selected_factor_count": len(scenario_rows)}
                )

    return result_rows, selection_rows


def write_summary(
    folds: list[dict[str, object]],
    result_rows: list[dict[str, object]],
    selection_rows: list[dict[str, object]],
) -> None:
    result_df = pd.DataFrame(result_rows)
    selection_df = pd.DataFrame(selection_rows)
    lines = [
        "# Base Core 6 Minus Log Total Assets V1",
        "",
        "Protocol:",
        "- annual anchor = realized May rebalance date",
        "- rolling window = `5y train + 2y test + 1y review`",
        f"- excluded base-core factor = `{EXCLUDED_FACTOR}`",
        "- fixed base candidate shell = remaining 6 resident factors",
        "- annual thresholds and combo scoring stay unchanged",
        "",
        "Base candidate shell:",
    ]
    for factor_name in TARGET_BASE_SET:
        lines.append(f"- `{factor_name}`")

    lines.extend(["", "Average review-year results by scenario and combo:"])
    if not result_df.empty:
        grouped = (
            result_df.groupby(["scenario_name", "combo_name"], dropna=False)
            .agg(
                folds=("fold_id", "count"),
                mean_review_ic=("review_rank_ic_mean", "mean"),
                mean_review_spread=("review_top_minus_bottom", "mean"),
                mean_selected_count=("selected_factor_count", "mean"),
            )
            .reset_index()
            .sort_values(["scenario_name", "mean_review_ic"], ascending=[True, False])
        )
        for _, row in grouped.iterrows():
            lines.append(
                f"- `{row['scenario_name']}` `{row['combo_name']}` | folds=`{int(row['folds'])}` | "
                f"mean_review_ic=`{format_metric(row['mean_review_ic'])}` | "
                f"mean_review_spread=`{format_metric(row['mean_review_spread'])}` | "
                f"mean_selected_count=`{format_metric(row['mean_selected_count'])}`"
            )

    if not selection_df.empty:
        lines.extend(["", "Selection counts by fold:"])
        for fold_id, group in selection_df.groupby("fold_id", sort=True):
            kept = int((pd.to_numeric(group["keep_flag"], errors="coerce") == 1).sum())
            total = int(len(group))
            lines.append(f"- `{fold_id}` | kept=`{kept}` / total=`{total}`")

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_FOLDS_PATH.name}]({OUTPUT_FOLDS_PATH})",
            f"- [{OUTPUT_SELECTION_PATH.name}]({OUTPUT_SELECTION_PATH})",
            f"- [{OUTPUT_RESULTS_PATH.name}]({OUTPUT_RESULTS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    base_rows, enhanced_rows, universe_rows = filter_factor_universe(base_rows, enhanced_rows, universe_rows)
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)
    result_rows, selection_rows = build_result_rows(panel_df, folds, base_rows, enhanced_rows, universe_rows)

    write_csv(OUTPUT_FOLDS_PATH, folds)
    write_csv(OUTPUT_SELECTION_PATH, selection_rows)
    write_csv(OUTPUT_RESULTS_PATH, result_rows)
    write_summary(folds, result_rows, selection_rows)
    print(OUTPUT_FOLDS_PATH)
    print(OUTPUT_SELECTION_PATH)
    print(OUTPUT_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
