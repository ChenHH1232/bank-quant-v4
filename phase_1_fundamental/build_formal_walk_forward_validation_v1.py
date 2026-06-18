from pathlib import Path

import pandas as pd

from build_pre2021_rolling_validation_v1 import (
    COMBO_NAMES,
    RESEARCH_END,
    SCENARIO_BASE,
    SCENARIO_ENHANCED,
    TRAIN_YEARS,
    add_combo_scores,
    build_scored_panel,
    evaluate_score,
    load_panel,
    month_floor,
    prepare_factor_metadata,
    write_csv,
)


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_FOLDS_PATH = SCRIPT_DIR / "formal_walk_forward_validation_v1_folds.csv"
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "formal_walk_forward_validation_v1_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "formal_walk_forward_validation_v1.md"

FORMAL_START = pd.Timestamp("2021-05-01")
MIN_FORMAL_TRAIN_REBALANCE_DATES = 15


def format_metric(value: object) -> str:
    if value == "" or pd.isna(value):
        return "n/a"
    return str(value)


def build_formal_folds(all_dates: list[pd.Timestamp], validation_dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    for validation_date in validation_dates:
        if validation_date < FORMAL_START:
            continue
        train_start = month_floor(validation_date) - pd.DateOffset(years=TRAIN_YEARS)
        train_dates = [d for d in all_dates if train_start <= d < validation_date]
        if len(train_dates) < MIN_FORMAL_TRAIN_REBALANCE_DATES:
            continue
        folds.append(
            {
                "fold_id": f"wf_{len(folds) + 1:02d}",
                "train_start": train_start.strftime("%Y-%m-%d"),
                "train_end": (validation_date - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "validation_start": validation_date.strftime("%Y-%m-%d"),
                "validation_end": validation_date.strftime("%Y-%m-%d"),
                "train_rebalance_dates": len(train_dates),
                "validation_rebalance_dates": 1,
            }
        )
    return folds


def summarize_fold(df: pd.DataFrame, fold: dict[str, object], scenario_name: str, combo_name: str) -> dict[str, object]:
    train_start = pd.Timestamp(fold["train_start"])
    validation_start = pd.Timestamp(fold["validation_start"])

    train_mask = (df["rebalance_date"] >= train_start) & (df["rebalance_date"] < validation_start)
    validation_mask = df["rebalance_date"] == validation_start

    train_metrics = evaluate_score(df, combo_name, "y_quarter_avg_daily_return_close", train_mask)
    validation_metrics = evaluate_score(df, combo_name, "y_quarter_avg_daily_return_close", validation_mask)

    return {
        "fold_id": fold["fold_id"],
        "scenario_name": scenario_name,
        "combo_name": combo_name,
        "train_start": fold["train_start"],
        "train_end": fold["train_end"],
        "validation_start": fold["validation_start"],
        "validation_end": fold["validation_end"],
        "train_rebalance_dates": fold["train_rebalance_dates"],
        "validation_rebalance_dates": fold["validation_rebalance_dates"],
        "train_rows": train_metrics["rows"],
        "train_dates": train_metrics["dates"],
        "train_rank_ic_mean": train_metrics["rank_ic_mean"],
        "train_rank_ic_ir": train_metrics["rank_ic_ir"],
        "train_positive_ic_ratio": train_metrics["positive_ic_ratio"],
        "train_top_minus_bottom": train_metrics["top_minus_bottom"],
        "validation_rows": validation_metrics["rows"],
        "validation_dates": validation_metrics["dates"],
        "validation_rank_ic_mean": validation_metrics["rank_ic_mean"],
        "validation_rank_ic_ir": validation_metrics["rank_ic_ir"],
        "validation_positive_ic_ratio": validation_metrics["positive_ic_ratio"],
        "validation_top_minus_bottom": validation_metrics["top_minus_bottom"],
    }


def build_result_rows(
    panel_df: pd.DataFrame,
    folds: list[dict[str, object]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    scenario_map = {
        SCENARIO_BASE: base_rows,
        SCENARIO_ENHANCED: enhanced_rows,
    }

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)

        for scenario_name, metadata_rows in scenario_map.items():
            scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, metadata_rows, train_mask)
            scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)

            for combo_name in COMBO_NAMES:
                rows.append(summarize_fold(scored_df, fold, scenario_name, combo_name))
    return rows


def write_summary(folds: list[dict[str, object]], result_rows: list[dict[str, object]], base_rows: list[dict[str, str]], enhanced_rows: list[dict[str, str]]) -> None:
    result_df = pd.DataFrame(result_rows)
    lines = [
        "# Formal Walk-Forward Validation V1",
        "",
        "Protocol:",
        f"- formal start: `{FORMAL_START.strftime('%Y-%m-%d')}`",
        f"- each rebalance date `T` is evaluated as a standalone out-of-sample walk-forward fold",
        f"- train window: previous `{TRAIN_YEARS}` calendar years ending immediately before `T`",
        f"- minimum train history: `{MIN_FORMAL_TRAIN_REBALANCE_DATES}` rebalance dates",
        "- preprocessing and IC weights are refit inside each fold's train window only",
        "",
        "Scenarios:",
        f"- `{SCENARIO_BASE}`: `{len(base_rows)}` factors",
        f"- `{SCENARIO_ENHANCED}`: `{len(enhanced_rows)}` factors",
        "",
        f"- walk-forward fold count: `{len(folds)}`",
        "",
        "Fold definitions:",
    ]

    for fold in folds:
        lines.append(
            f"- `{fold['fold_id']}` | train=`{fold['train_start']}` to `{fold['train_end']}` "
            f"| prediction date=`{fold['validation_start']}` | train_dates=`{fold['train_rebalance_dates']}`"
        )

    lines.extend(["", "Average post-2021 validation results by scenario and combo:"])
    for scenario_name in [SCENARIO_BASE, SCENARIO_ENHANCED]:
        subset = result_df[result_df["scenario_name"] == scenario_name].copy()
        if subset.empty:
            continue
        scenario_summary = (
            subset.groupby("combo_name", dropna=False)
            .agg(
                fold_count=("fold_id", "count"),
                mean_validation_rank_ic_mean=("validation_rank_ic_mean", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_validation_rank_ic_ir=("validation_rank_ic_ir", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_validation_top_minus_bottom=("validation_top_minus_bottom", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_validation_positive_ic_ratio=("validation_positive_ic_ratio", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(
                ["mean_validation_rank_ic_mean", "mean_validation_top_minus_bottom"],
                ascending=[False, False],
            )
        )
        best_row = scenario_summary.iloc[0]
        lines.append(
            f"- `{scenario_name}` best combo: `{best_row['combo_name']}` | "
            f"mean_post2021_ic=`{format_metric(round(float(best_row['mean_validation_rank_ic_mean']), 6))}` | "
            f"mean_post2021_spread=`{format_metric(round(float(best_row['mean_validation_top_minus_bottom']), 8))}`"
        )
        for _, row in scenario_summary.iterrows():
            lines.append(
                f"- `{scenario_name}` `{row['combo_name']}` | folds=`{int(row['fold_count'])}` | "
                f"mean_post2021_ic=`{format_metric(round(float(row['mean_validation_rank_ic_mean']), 6))}` | "
                f"mean_post2021_ic_ir=`{format_metric(round(float(row['mean_validation_rank_ic_ir']), 6))}` | "
                f"mean_post2021_spread=`{format_metric(round(float(row['mean_validation_top_minus_bottom']), 8))}` | "
                f"mean_post2021_pos_ic_ratio=`{format_metric(round(float(row['mean_validation_positive_ic_ratio']), 6))}`"
            )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_FOLDS_PATH.name}]({OUTPUT_FOLDS_PATH})",
            f"- [{OUTPUT_RESULTS_PATH.name}]({OUTPUT_RESULTS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    base_rows, enhanced_rows = prepare_factor_metadata()

    dates = sorted(pd.to_datetime(panel_df["rebalance_date"].drop_duplicates()))
    all_dates = [pd.Timestamp(d) for d in dates]
    fold_dates = [d for d in all_dates if d >= RESEARCH_END]
    folds = build_formal_folds(all_dates, fold_dates)
    result_rows = build_result_rows(panel_df, folds, base_rows, enhanced_rows)

    write_csv(OUTPUT_FOLDS_PATH, folds)
    write_csv(OUTPUT_RESULTS_PATH, result_rows)
    write_summary(folds, result_rows, base_rows, enhanced_rows)

    print(OUTPUT_FOLDS_PATH)
    print(OUTPUT_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
