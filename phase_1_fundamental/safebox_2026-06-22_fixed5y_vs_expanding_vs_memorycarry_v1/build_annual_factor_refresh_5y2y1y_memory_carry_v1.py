from pathlib import Path

import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    COMBO_NAMES,
    KEEPABLE_V3_STATUSES,
    MAX_BASE_CORE_KEEP,
    MAX_IMPROVEMENT_KEEP,
    MAX_WATCH_KEEP,
    MIN_BASE_CORE_KEEP,
    MIN_REVIEW_REBALANCE_DATES,
    MIN_TEST_POSITIVE_IC_RATIO,
    MIN_TEST_RANK_IC_FOR_WEAK_SPREAD,
    MIN_TEST_REBALANCE_DATES,
    MIN_TEST_RANK_IC_MEAN,
    MIN_TEST_TOP_MINUS_BOTTOM,
    MIN_TRAIN_RANK_IC_MEAN,
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
    evaluate_score,
    format_metric,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
    summarize_combo,
    write_csv,
)


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_FOLDS_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_memory_carry_v1_folds.csv"
OUTPUT_SELECTION_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_memory_carry_v1_factor_selection.csv"
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_memory_carry_v1_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_memory_carry_v1.md"

MEMORY_CARRY_MAX_BASE = 2
MEMORY_CARRY_TEST_IC_FLOOR = -0.05
MEMORY_CARRY_TEST_POSITIVE_RATIO_FLOOR = 0.5


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
                "fold_id": f"memory_{len(folds) + 1:02d}",
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
    test_positive_pass = test_positive_ic_ratio != "" and float(test_positive_ic_ratio) >= MIN_TEST_POSITIVE_IC_RATIO
    test_spread_pass = test_top_minus_bottom != "" and float(test_top_minus_bottom) >= MIN_TEST_TOP_MINUS_BOTTOM
    test_weak_spread_override = test_ic != "" and float(test_ic) >= MIN_TEST_RANK_IC_FOR_WEAK_SPREAD
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
        "priority_score": round(
            (float(test_ic) if test_ic != "" else -999.0) * 1000
            + (float(test_positive_ic_ratio) if test_positive_ic_ratio != "" else -999.0) * 10
            + (float(test_top_minus_bottom) if test_top_minus_bottom != "" else -999.0),
            6,
        ),
        "train_pass": int(train_pass),
        "test_positive_pass": int(test_positive_pass),
    }


def apply_memory_carry(
    selection_rows: list[dict[str, object]],
    universe_rows: list[dict[str, str]],
    previous_base_core_names: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, object]], set[str]]:
    selected_rows, adjusted_rows = apply_layer_caps(selection_rows, universe_rows)
    metadata_map = {row["factor_name"]: row for row in universe_rows}
    selected_name_set = {row["factor_name"] for row in selected_rows}

    carry_candidates: list[dict[str, object]] = []
    for row in adjusted_rows:
        factor_name = str(row["factor_name"])
        if factor_name not in previous_base_core_names:
            continue
        if str(row["layer"]) != "base_core":
            continue
        if factor_name in selected_name_set:
            continue
        train_pass = int(row.get("train_pass", 0)) == 1
        test_positive_pass = int(row.get("test_positive_pass", 0)) == 1
        test_ic_value = pd.to_numeric(pd.Series([row.get("test_rank_ic_mean", "")]), errors="coerce").iloc[0]
        if not train_pass or not test_positive_pass or pd.isna(test_ic_value) or float(test_ic_value) < MEMORY_CARRY_TEST_IC_FLOOR:
            continue
        carry_candidates.append(row)

    carry_candidates = sorted(
        carry_candidates,
        key=lambda row: (
            float(row["test_rank_ic_mean"]) if row["test_rank_ic_mean"] != "" else -999.0,
            float(row["test_positive_ic_ratio"]) if row["test_positive_ic_ratio"] != "" else -999.0,
            str(row["factor_name"]),
        ),
        reverse=True,
    )

    carried_names: set[str] = set()
    for row in carry_candidates[:MEMORY_CARRY_MAX_BASE]:
        factor_name = str(row["factor_name"])
        carried_names.add(factor_name)
        selected_name_set.add(factor_name)

    for row in adjusted_rows:
        factor_name = str(row["factor_name"])
        if factor_name in carried_names:
            row["keep_flag"] = 1
            row["keep_reason"] = f"{row['keep_reason']}|carried_from_previous_base_core"

    selected_rows = [metadata_map[name] for name in sorted(selected_name_set)]
    current_base_core_names = {name for name in selected_name_set if metadata_map[name]["layer"] == "base_core"}
    return selected_rows, adjusted_rows, current_base_core_names


def select_factor_rows(
    panel_df: pd.DataFrame,
    universe_rows: list[dict[str, str]],
    fold: dict[str, object],
    previous_base_core_names: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, object]], set[str]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])

    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)

    selection_rows: list[dict[str, object]] = []
    for factor_row in universe_rows:
        evaluated = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
        selection_rows.append(evaluated | {"fold_id": fold["fold_id"]})
    return apply_memory_carry(selection_rows, universe_rows, previous_base_core_names)


def build_result_rows(
    panel_df: pd.DataFrame,
    folds: list[dict[str, object]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    result_rows: list[dict[str, object]] = []
    selection_rows: list[dict[str, object]] = []
    previous_base_core_names: set[str] = set()

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

        selected_rows, fold_selection_rows, previous_base_core_names = select_factor_rows(
            panel_df,
            universe_rows,
            fold,
            previous_base_core_names,
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
    universe_rows: list[dict[str, str]],
) -> None:
    result_df = pd.DataFrame(result_rows)
    selection_df = pd.DataFrame(selection_rows)

    lines = [
        "# Annual Factor Refresh 5Y2Y1Y Memory Carry V1",
        "",
        "Protocol:",
        "- annual refresh anchor = each year's realized May rebalance date",
        f"- train window: previous `{TRAIN_YEAR_COUNT}` realized May-anchor cycles",
        f"- test window: next `{TEST_YEAR_COUNT}` realized May-anchor cycles",
        f"- review window: next `{REVIEW_YEAR_COUNT}` realized May-anchor cycle",
        "- baseline factor selection and layer caps stay unchanged",
        "- added memory carry rule:",
        "- only previous-year selected `base_core` factors can be carried",
        f"- max carry count per year = `{MEMORY_CARRY_MAX_BASE}`",
        f"- carry requires current-year train pass, test positive ratio >= `{MEMORY_CARRY_TEST_POSITIVE_RATIO_FLOOR}`, and test ic >= `{MEMORY_CARRY_TEST_IC_FLOOR}`",
        "- carry lasts only one annual refresh cycle unless the factor re-enters by the normal rule",
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
                carried_factors=("keep_reason", lambda s: int(s.fillna("").str.contains("carried_from_previous_base_core").sum())),
            )
            .reset_index()
        )
        for _, row in selection_summary.iterrows():
            lines.append(
                f"- `{row['fold_id']}` | kept=`{int(row['kept_factors'])}` / total=`{int(row['total_factors'])}` "
                f"| carried=`{int(row['carried_factors'])}`"
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
