from pathlib import Path

import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    COMBO_NAMES,
    MAX_BASE_CORE_KEEP,
    MAX_IMPROVEMENT_KEEP,
    MAX_WATCH_KEEP,
    MIN_BASE_CORE_KEEP,
    MIN_REVIEW_REBALANCE_DATES,
    MIN_TEST_REBALANCE_DATES,
    MIN_TRAIN_REBALANCE_DATES,
    REVIEW_YEAR_COUNT,
    SCENARIO_BASE,
    SCENARIO_ENHANCED,
    TEST_YEAR_COUNT,
    TRAIN_YEAR_COUNT,
    add_combo_scores,
    apply_layer_caps,
    build_scenario_rows,
    build_scored_panel,
    evaluate_factor_window,
    evaluate_score,
    format_metric,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
    summarize_combo,
    write_csv,
)


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_FOLDS_PATH = SCRIPT_DIR / "annual_factor_refresh_expanding_5y2y1y_v1_folds.csv"
OUTPUT_SELECTION_PATH = SCRIPT_DIR / "annual_factor_refresh_expanding_5y2y1y_v1_factor_selection.csv"
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "annual_factor_refresh_expanding_5y2y1y_v1_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "annual_factor_refresh_expanding_5y2y1y_v1.md"


def build_yearly_folds_expanding(may_dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    required_span = TRAIN_YEAR_COUNT + TEST_YEAR_COUNT + REVIEW_YEAR_COUNT
    if len(may_dates) < required_span:
        return folds

    anchor_train_start = may_dates[0]
    for review_idx in range(TRAIN_YEAR_COUNT + TEST_YEAR_COUNT, len(may_dates) - REVIEW_YEAR_COUNT + 1):
        test_start_idx = review_idx - TEST_YEAR_COUNT
        train_dates = may_dates[0:test_start_idx]
        test_dates = may_dates[test_start_idx:review_idx]
        review_dates = may_dates[review_idx:review_idx + REVIEW_YEAR_COUNT]
        if len(train_dates) < TRAIN_YEAR_COUNT or len(test_dates) < TEST_YEAR_COUNT or len(review_dates) < REVIEW_YEAR_COUNT:
            continue

        folds.append(
            {
                "fold_id": f"expanding_{len(folds) + 1:02d}",
                "train_start": anchor_train_start.strftime("%Y-%m-%d"),
                "train_end": (test_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "test_start": test_dates[0].strftime("%Y-%m-%d"),
                "test_end": (review_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "review_start": review_dates[0].strftime("%Y-%m-%d"),
                "review_end": (review_dates[0] + pd.DateOffset(years=1) - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "train_anchor_years": len(train_dates),
                "test_anchor_years": len(test_dates),
                "review_anchor_years": len(review_dates),
            }
        )
    return folds


def select_factor_rows(panel_df: pd.DataFrame, universe_rows: list[dict[str, str]], fold: dict[str, object]) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])

    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)

    selection_rows: list[dict[str, object]] = []
    for factor_row in universe_rows:
        evaluated = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
        selection_rows.append(evaluated | {"fold_id": fold["fold_id"], "train_anchor_years": fold["train_anchor_years"]})
    return apply_layer_caps(selection_rows, universe_rows)


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
                    | {
                        "selected_factor_count": len(scenario_rows),
                        "train_anchor_years": fold["train_anchor_years"],
                    }
                )

    return result_rows, selection_rows


def write_summary(
    folds: list[dict[str, object]],
    result_rows: list[dict[str, object]],
    selection_rows: list[dict[str, object]],
    universe_rows: list[dict[str, str]],
) -> None:
    result_df = pd.DataFrame(result_rows)
    selection_df = pd.DataFrame(selection_rows)

    lines = [
        "# Annual Factor Refresh Expanding 5Y2Y1Y V1",
        "",
        "Protocol:",
        "- annual refresh anchor = each year's realized May rebalance date, not a hard-coded `May 1` calendar boundary",
        f"- initial train window: first `{TRAIN_YEAR_COUNT}` realized May-anchor cycles",
        "- expanding rule: after the first usable fold, the train start stays fixed and the train end moves forward by one realized May-anchor cycle each year",
        f"- test window: next `{TEST_YEAR_COUNT}` realized May-anchor cycles",
        f"- review window: next `{REVIEW_YEAR_COUNT}` realized May-anchor cycle",
        "- factor selection is refreshed once per year, then frozen for the whole review year",
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
            f"| review=`{fold['review_start']}` to `{fold['review_end']}` "
            f"| train_anchor_years=`{fold['train_anchor_years']}`"
        )

    if not selection_df.empty:
        lines.extend(["", "Annual factor selection counts:"])
        selection_summary = (
            selection_df.groupby(["fold_id", "train_anchor_years"])
            .agg(
                kept_factors=("keep_flag", "sum"),
                total_factors=("factor_name", "count"),
            )
            .reset_index()
        )
        for _, row in selection_summary.iterrows():
            lines.append(
                f"- `{row['fold_id']}` | train_anchor_years=`{int(row['train_anchor_years'])}` | "
                f"kept=`{int(row['kept_factors'])}` / total=`{int(row['total_factors'])}`"
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
                    mean_train_anchor_years=("train_anchor_years", "mean"),
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
                f"mean_selected_count=`{format_metric(round(float(best_row['mean_selected_factor_count']), 2))}` | "
                f"mean_train_anchor_years=`{format_metric(round(float(best_row['mean_train_anchor_years']), 2))}`"
            )
            for _, row in scenario_summary.iterrows():
                lines.append(
                    f"- `{scenario_name}` `{row['combo_name']}` | folds=`{int(row['fold_count'])}` | "
                    f"mean_review_ic=`{format_metric(round(float(row['mean_review_rank_ic_mean']), 6))}` | "
                    f"mean_review_spread=`{format_metric(round(float(row['mean_review_top_minus_bottom']), 8))}` | "
                    f"mean_review_pos_ic_ratio=`{format_metric(round(float(row['mean_review_positive_ic_ratio']), 6))}` | "
                    f"mean_selected_count=`{format_metric(round(float(row['mean_selected_factor_count']), 2))}` | "
                    f"mean_train_anchor_years=`{format_metric(round(float(row['mean_train_anchor_years']), 2))}`"
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
    folds = build_yearly_folds_expanding(may_dates)
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
