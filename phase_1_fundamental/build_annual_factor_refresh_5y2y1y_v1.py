import csv
from pathlib import Path

import pandas as pd

from build_pre2021_rolling_validation_v1 import (
    COMBO_NAMES,
    SCENARIO_BASE,
    SCENARIO_ENHANCED,
    add_combo_scores,
    build_scored_panel,
    evaluate_score,
    load_panel,
    load_rows,
    prepare_factor_metadata,
    write_csv,
)


SCRIPT_DIR = Path(__file__).resolve().parent
FACTOR_POOL_PATH = SCRIPT_DIR / "final_core_factor_pool_v3.csv"

OUTPUT_FOLDS_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_v1_folds.csv"
OUTPUT_SELECTION_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_v1_factor_selection.csv"
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_v1_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_v1.md"

TRAIN_YEAR_COUNT = 5
TEST_YEAR_COUNT = 2
REVIEW_YEAR_COUNT = 1
MIN_TRAIN_REBALANCE_DATES = 15
MIN_TEST_REBALANCE_DATES = 6
MIN_REVIEW_REBALANCE_DATES = 3
MIN_TRAIN_RANK_IC_MEAN = 0.0
MIN_TEST_RANK_IC_MEAN = 0.0
MIN_TEST_POSITIVE_IC_RATIO = 0.5
MIN_TEST_TOP_MINUS_BOTTOM = 0.0
MIN_TEST_RANK_IC_FOR_WEAK_SPREAD = 0.05
MIN_BASE_CORE_KEEP = 4
MAX_BASE_CORE_KEEP = 7
MAX_IMPROVEMENT_KEEP = 2
MAX_WATCH_KEEP = 2

KEEPABLE_V3_STATUSES = {"keep_final", "keep_enhancement", "watch_keep", "downgrade_watch"}


def load_factor_universe() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    base_rows, enhanced_rows = prepare_factor_metadata()
    by_factor = {
        row["factor_name"]: row
        for row in base_rows + enhanced_rows
    }

    core_results = {row["factor_name"]: row for row in load_rows(SCRIPT_DIR / "single_factor_test_results_core_v2.csv")}
    improvement_results = {row["factor_name"]: row for row in load_rows(SCRIPT_DIR / "improvement_factor_test_results_v1.csv")}

    universe_rows: list[dict[str, str]] = []
    for row in load_rows(FACTOR_POOL_PATH):
        if row["v3_status"] not in KEEPABLE_V3_STATUSES:
            continue
        factor_name = row["factor_name"]
        if factor_name in by_factor:
            universe_rows.append(by_factor[factor_name])
            continue

        factor_result = core_results.get(factor_name) or improvement_results.get(factor_name)
        if factor_result is None:
            raise KeyError(f"Missing metadata for factor {factor_name}")
        universe_rows.append(
            {
                "factor_name": factor_name,
                "factor_family": row["factor_family"],
                "layer": row["layer"],
                "direction": factor_result["direction"],
                "target_label": factor_result["target_label"],
            }
        )

    return base_rows, enhanced_rows, universe_rows


def get_may_rebalance_dates(panel_df: pd.DataFrame) -> list[pd.Timestamp]:
    dates = sorted(pd.to_datetime(panel_df["rebalance_date"].drop_duplicates()))
    return [pd.Timestamp(d) for d in dates if pd.Timestamp(d).month == 5]


def build_yearly_folds(may_dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    required_span = TRAIN_YEAR_COUNT + TEST_YEAR_COUNT + REVIEW_YEAR_COUNT
    for start_idx in range(0, len(may_dates) - required_span + 1):
        train_dates = may_dates[start_idx : start_idx + TRAIN_YEAR_COUNT]
        test_dates = may_dates[start_idx + TRAIN_YEAR_COUNT : start_idx + TRAIN_YEAR_COUNT + TEST_YEAR_COUNT]
        review_dates = may_dates[start_idx + TRAIN_YEAR_COUNT + TEST_YEAR_COUNT : start_idx + required_span]
        if len(train_dates) < TRAIN_YEAR_COUNT or len(test_dates) < TEST_YEAR_COUNT or len(review_dates) < REVIEW_YEAR_COUNT:
            continue

        folds.append(
            {
                "fold_id": f"annual_{len(folds) + 1:02d}",
                "train_start": train_dates[0].strftime("%Y-%m-%d"),
                "train_end": (test_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "test_start": test_dates[0].strftime("%Y-%m-%d"),
                "test_end": (review_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "review_start": review_dates[0].strftime("%Y-%m-%d"),
                "review_end": (review_dates[0] + pd.DateOffset(years=1) - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            }
        )
    return folds


def evaluate_factor_window(panel_df: pd.DataFrame, factor_row: dict[str, str], train_mask: pd.Series, test_mask: pd.Series) -> dict[str, object]:
    factor_name = factor_row["factor_name"]
    scored_df, _, _ = build_scored_panel(panel_df, [factor_row], train_mask)
    adj_col = f"adj__{factor_name}"
    train_metrics = evaluate_score(scored_df, adj_col, factor_row["target_label"], train_mask)
    test_metrics = evaluate_score(scored_df, adj_col, factor_row["target_label"], test_mask)

    train_ic = train_metrics["rank_ic_mean"]
    test_ic = test_metrics["rank_ic_mean"]
    test_positive_ic_ratio = test_metrics["positive_ic_ratio"]
    test_top_minus_bottom = test_metrics["top_minus_bottom"]

    train_pass = train_ic != "" and float(train_ic) > MIN_TRAIN_RANK_IC_MEAN
    test_ic_pass = test_ic != "" and float(test_ic) > MIN_TEST_RANK_IC_MEAN
    test_positive_pass = (
        test_positive_ic_ratio != "" and float(test_positive_ic_ratio) >= MIN_TEST_POSITIVE_IC_RATIO
    )
    test_spread_pass = (
        test_top_minus_bottom != "" and float(test_top_minus_bottom) >= MIN_TEST_TOP_MINUS_BOTTOM
    )
    test_weak_spread_override = (
        test_ic != "" and float(test_ic) >= MIN_TEST_RANK_IC_FOR_WEAK_SPREAD
    )
    keep_flag = int(
        train_pass
        and test_ic_pass
        and test_positive_pass
        and (test_spread_pass or test_weak_spread_override)
    )
    return {
        "factor_name": factor_name,
        "factor_family": factor_row["factor_family"],
        "layer": factor_row["layer"],
        "direction": factor_row["direction"],
        "target_label": factor_row["target_label"],
        "train_rank_ic_mean": train_ic,
        "test_rank_ic_mean": test_ic,
        "train_positive_ic_ratio": train_metrics["positive_ic_ratio"],
        "test_positive_ic_ratio": test_metrics["positive_ic_ratio"],
        "train_top_minus_bottom": train_metrics["top_minus_bottom"],
        "test_top_minus_bottom": test_metrics["top_minus_bottom"],
        "keep_flag": keep_flag,
        "keep_reason": (
            "pass_train_ic_and_test_ic_positive_ratio_and_structure"
            if keep_flag == 1
            else "fail_threshold_rule"
        ),
        "priority_score": (
            round(
                (float(test_ic) if test_ic != "" else -999.0) * 1000
                + (float(test_positive_ic_ratio) if test_positive_ic_ratio != "" else -999.0) * 10
                + (float(test_top_minus_bottom) if test_top_minus_bottom != "" else -999.0),
                6,
            )
        ),
    }


def apply_layer_caps(selection_rows: list[dict[str, object]], universe_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    metadata_map = {row["factor_name"]: row for row in universe_rows}
    passed_rows = [row.copy() for row in selection_rows if int(row["keep_flag"]) == 1]

    def sort_key(row: dict[str, object]) -> tuple[float, float, float, str]:
        test_ic = float(row["test_rank_ic_mean"]) if row["test_rank_ic_mean"] != "" else -999.0
        test_spread = float(row["test_top_minus_bottom"]) if row["test_top_minus_bottom"] != "" else -999.0
        test_pos = float(row["test_positive_ic_ratio"]) if row["test_positive_ic_ratio"] != "" else -999.0
        return (test_ic, test_pos, test_spread, str(row["factor_name"]))

    base_candidates = sorted([row for row in passed_rows if row["layer"] == "base_core"], key=sort_key, reverse=True)
    improvement_candidates = sorted([row for row in passed_rows if row["layer"] == "improvement_layer"], key=sort_key, reverse=True)
    watch_candidates = sorted([row for row in passed_rows if row["layer"] == "watch_layer"], key=sort_key, reverse=True)

    selected_names: set[str] = set()

    for row in base_candidates[:MAX_BASE_CORE_KEEP]:
        selected_names.add(str(row["factor_name"]))

    if len(selected_names) < MIN_BASE_CORE_KEEP:
        for row in base_candidates[MAX_BASE_CORE_KEEP:]:
            selected_names.add(str(row["factor_name"]))
            if len([name for name in selected_names if metadata_map[name]["layer"] == "base_core"]) >= MIN_BASE_CORE_KEEP:
                break

    for row in improvement_candidates[:MAX_IMPROVEMENT_KEEP]:
        selected_names.add(str(row["factor_name"]))

    for row in watch_candidates[:MAX_WATCH_KEEP]:
        selected_names.add(str(row["factor_name"]))

    adjusted_rows: list[dict[str, object]] = []
    for row in selection_rows:
        row_copy = row.copy()
        if int(row_copy["keep_flag"]) == 1 and str(row_copy["factor_name"]) in selected_names:
            row_copy["keep_flag"] = 1
            row_copy["keep_reason"] = f"{row_copy['keep_reason']}|selected_after_layer_caps"
        elif int(row_copy["keep_flag"]) == 1:
            row_copy["keep_flag"] = 0
            row_copy["keep_reason"] = f"{row_copy['keep_reason']}|dropped_by_layer_caps"
        adjusted_rows.append(row_copy)

    selected_rows = [metadata_map[name] for name in sorted(selected_names)]
    return selected_rows, adjusted_rows


def select_factor_rows(panel_df: pd.DataFrame, universe_rows: list[dict[str, str]], fold: dict[str, object]) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])

    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)

    selection_rows: list[dict[str, object]] = []
    for factor_row in universe_rows:
        evaluated = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
        selection_rows.append(evaluated | {"fold_id": fold["fold_id"]})
    return apply_layer_caps(selection_rows, universe_rows)


def build_scenario_rows(selected_rows: list[dict[str, str]], base_rows: list[dict[str, str]], enhanced_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    selected_names = {row["factor_name"] for row in selected_rows}
    base_selected = [row for row in base_rows if row["factor_name"] in selected_names]
    enhanced_selected = [row for row in enhanced_rows if row["factor_name"] in selected_names]
    return {
        SCENARIO_BASE: base_selected,
        SCENARIO_ENHANCED: enhanced_selected,
    }


def summarize_combo(df: pd.DataFrame, fold: dict[str, object], scenario_name: str, combo_name: str) -> dict[str, object]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

    train_mask = (df["rebalance_date"] >= train_start) & (df["rebalance_date"] < test_start)
    test_mask = (df["rebalance_date"] >= test_start) & (df["rebalance_date"] < review_start)
    review_mask = (df["rebalance_date"] >= review_start) & (df["rebalance_date"] < review_end)

    train_metrics = evaluate_score(df, combo_name, "y_quarter_avg_daily_return_close", train_mask)
    test_metrics = evaluate_score(df, combo_name, "y_quarter_avg_daily_return_close", test_mask)
    review_metrics = evaluate_score(df, combo_name, "y_quarter_avg_daily_return_close", review_mask)

    return {
        "fold_id": fold["fold_id"],
        "scenario_name": scenario_name,
        "combo_name": combo_name,
        "train_start": fold["train_start"],
        "train_end": fold["train_end"],
        "test_start": fold["test_start"],
        "test_end": fold["test_end"],
        "review_start": fold["review_start"],
        "review_end": fold["review_end"],
        "train_rank_ic_mean": train_metrics["rank_ic_mean"],
        "test_rank_ic_mean": test_metrics["rank_ic_mean"],
        "review_rank_ic_mean": review_metrics["rank_ic_mean"],
        "train_top_minus_bottom": train_metrics["top_minus_bottom"],
        "test_top_minus_bottom": test_metrics["top_minus_bottom"],
        "review_top_minus_bottom": review_metrics["top_minus_bottom"],
        "review_positive_ic_ratio": review_metrics["positive_ic_ratio"],
        "review_dates": review_metrics["dates"],
        "review_rows": review_metrics["rows"],
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
        review_start = pd.Timestamp(fold["review_start"])
        review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
        test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)
        review_mask = (panel_df["rebalance_date"] >= review_start) & (panel_df["rebalance_date"] < review_end)

        train_dates = int(panel_df.loc[train_mask, "rebalance_date"].nunique())
        test_dates = int(panel_df.loc[test_mask, "rebalance_date"].nunique())
        review_dates = int(panel_df.loc[review_mask, "rebalance_date"].nunique())
        if train_dates < MIN_TRAIN_REBALANCE_DATES or test_dates < MIN_TEST_REBALANCE_DATES or review_dates < MIN_REVIEW_REBALANCE_DATES:
            continue

        selected_rows, fold_selection_rows = select_factor_rows(panel_df, universe_rows, fold)
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


def format_metric(value: object) -> str:
    if value == "" or pd.isna(value):
        return "n/a"
    return str(value)


def write_summary(
    folds: list[dict[str, object]],
    result_rows: list[dict[str, object]],
    selection_rows: list[dict[str, object]],
    universe_rows: list[dict[str, str]],
) -> None:
    result_df = pd.DataFrame(result_rows)
    selection_df = pd.DataFrame(selection_rows)

    lines = [
        "# Annual Factor Refresh 5Y2Y1Y V1",
        "",
        "Protocol:",
        "- annual refresh anchor = each year's realized May rebalance date, not a hard-coded `May 1` calendar boundary",
        f"- train window: previous `{TRAIN_YEAR_COUNT}` realized May-anchor cycles",
        f"- test window: next `{TEST_YEAR_COUNT}` realized May-anchor cycles",
        f"- review window: next `{REVIEW_YEAR_COUNT}` realized May-anchor cycle",
        "- factor selection is refreshed once per year, then frozen for the whole review year",
        f"- keep rule: train_ic>`{MIN_TRAIN_RANK_IC_MEAN}`, test_ic>`{MIN_TEST_RANK_IC_MEAN}`, test_positive_ic_ratio>=`{MIN_TEST_POSITIVE_IC_RATIO}`",
        f"- structure rule: keep only if test_top_minus_bottom>=`{MIN_TEST_TOP_MINUS_BOTTOM}` or test_ic>=`{MIN_TEST_RANK_IC_FOR_WEAK_SPREAD}`",
        f"- layer caps: base_core min/max=`{MIN_BASE_CORE_KEEP}/{MAX_BASE_CORE_KEEP}`, improvement max=`{MAX_IMPROVEMENT_KEEP}`, watch max=`{MAX_WATCH_KEEP}`",
        "",
        f"- controlled factor universe size: `{len(universe_rows)}`",
        f"- fold count: `{len(result_df['fold_id'].drop_duplicates()) if not result_df.empty else 0}`",
        "",
        "Fold definitions:",
    ]

    for fold in folds:
        lines.append(
            f"- `{fold['fold_id']}` | train=`{fold['train_start']}` to `{fold['train_end']}` "
            f"| test=`{fold['test_start']}` to `{fold['test_end']}` "
            f"| review=`{fold['review_start']}` to `{fold['review_end']}`"
        )

    if not selection_df.empty:
        lines.extend(["", "Annual factor selection counts:"])
        selection_summary = (
            selection_df.groupby("fold_id")
            .agg(
                kept_factors=("keep_flag", "sum"),
                total_factors=("factor_name", "count"),
            )
            .reset_index()
        )
        for _, row in selection_summary.iterrows():
            lines.append(
                f"- `{row['fold_id']}` | kept=`{int(row['kept_factors'])}` / total=`{int(row['total_factors'])}`"
            )

    if not result_df.empty:
        lines.extend(["", "Average review-year results by scenario and combo:"])
        for scenario_name in [SCENARIO_BASE, SCENARIO_ENHANCED]:
            subset = result_df[result_df["scenario_name"] == scenario_name].copy()
            if subset.empty:
                continue
            scenario_summary = (
                subset.groupby("combo_name", dropna=False)
                .agg(
                    fold_count=("fold_id", "count"),
                    mean_review_rank_ic_mean=("review_rank_ic_mean", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                    mean_review_top_minus_bottom=("review_top_minus_bottom", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                    mean_review_positive_ic_ratio=("review_positive_ic_ratio", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                    mean_selected_factor_count=("selected_factor_count", "mean"),
                )
                .reset_index()
                .sort_values(
                    ["mean_review_rank_ic_mean", "mean_review_top_minus_bottom"],
                    ascending=[False, False],
                )
            )
            best_row = scenario_summary.iloc[0]
            lines.append(
                f"- `{scenario_name}` best combo: `{best_row['combo_name']}` | "
                f"mean_review_ic=`{format_metric(round(float(best_row['mean_review_rank_ic_mean']), 6))}` | "
                f"mean_review_spread=`{format_metric(round(float(best_row['mean_review_top_minus_bottom']), 8))}` | "
                f"mean_selected_count=`{format_metric(round(float(best_row['mean_selected_factor_count']), 2))}`"
            )
            for _, row in scenario_summary.iterrows():
                lines.append(
                    f"- `{scenario_name}` `{row['combo_name']}` | folds=`{int(row['fold_count'])}` | "
                    f"mean_review_ic=`{format_metric(round(float(row['mean_review_rank_ic_mean']), 6))}` | "
                    f"mean_review_spread=`{format_metric(round(float(row['mean_review_top_minus_bottom']), 8))}` | "
                    f"mean_review_pos_ic_ratio=`{format_metric(round(float(row['mean_review_positive_ic_ratio']), 6))}` | "
                    f"mean_selected_count=`{format_metric(round(float(row['mean_selected_factor_count']), 2))}`"
                )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_FOLDS_PATH.name}]({OUTPUT_FOLDS_PATH})",
            f"- [{OUTPUT_SELECTION_PATH.name}]({OUTPUT_SELECTION_PATH})",
            f"- [{OUTPUT_RESULTS_PATH.name}]({OUTPUT_RESULTS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)
    result_rows, selection_rows = build_result_rows(panel_df, folds, base_rows, enhanced_rows, universe_rows)

    write_csv(OUTPUT_FOLDS_PATH, folds)
    write_csv(OUTPUT_SELECTION_PATH, selection_rows)
    write_csv(OUTPUT_RESULTS_PATH, result_rows)
    write_summary(folds, result_rows, selection_rows, universe_rows)

    print(OUTPUT_FOLDS_PATH)
    print(OUTPUT_SELECTION_PATH)
    print(OUTPUT_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
