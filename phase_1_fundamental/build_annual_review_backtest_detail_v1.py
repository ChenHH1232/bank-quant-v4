import csv
from pathlib import Path

import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    COMBO_NAMES,
    SCENARIO_BASE,
    SCENARIO_ENHANCED,
    add_combo_scores,
    build_result_rows,
    build_scenario_rows,
    build_scored_panel,
    build_yearly_folds,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
    select_factor_rows,
)
from build_pre2021_rolling_validation_v1 import assign_groups


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_GROUPS_PATH = SCRIPT_DIR / "annual_review_backtest_detail_v1_groups.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "annual_review_backtest_detail_v1.md"


def build_group_rows(
    panel_df: pd.DataFrame,
    folds: list[dict[str, object]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        test_start = pd.Timestamp(fold["test_start"])
        review_start = pd.Timestamp(fold["review_start"])
        review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
        selected_rows, _ = select_factor_rows(panel_df, universe_rows, fold)
        scenario_map = build_scenario_rows(selected_rows, base_rows, enhanced_rows)

        for scenario_name, scenario_rows in scenario_map.items():
            if not scenario_rows:
                continue

            scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, scenario_rows, train_mask)
            scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
            review_df = scored_df[
                (scored_df["rebalance_date"] >= review_start) & (scored_df["rebalance_date"] < review_end)
            ].copy()

            for combo_name in COMBO_NAMES:
                for rebalance_date, group in review_df.groupby("rebalance_date"):
                    group = group.dropna(subset=[combo_name, "y_quarter_avg_daily_return_close"]).copy()
                    if len(group) < 5:
                        continue
                    group["bucket"] = assign_groups(group[combo_name], 5)
                    group = group.dropna(subset=["bucket"])
                    if group.empty:
                        continue

                    mean_map = group.groupby("bucket")["y_quarter_avg_daily_return_close"].mean().to_dict()
                    count_map = group.groupby("bucket")["code"].count().to_dict()
                    for bucket in sorted(mean_map):
                        rows.append(
                            {
                                "fold_id": fold["fold_id"],
                                "scenario_name": scenario_name,
                                "combo_name": combo_name,
                                "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                                "bucket": int(bucket),
                                "stock_count": int(count_map[bucket]),
                                "avg_return": round(float(mean_map[bucket]), 10),
                            }
                        )
    return rows


def write_group_rows(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_GROUPS_PATH.write_text("", encoding="utf-8")
        return
    with OUTPUT_GROUPS_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_SUMMARY_PATH.write_text("# Annual Review Backtest Detail V1\n\n- no rows", encoding="utf-8")
        return

    df = pd.DataFrame(rows)
    lines = [
        "# Annual Review Backtest Detail V1",
        "",
        "This file shows the review-year grouped return detail after each annual factor refresh has already been frozen.",
        "",
        f"- review rebalance snapshots: `{df[['fold_id', 'scenario_name', 'combo_name', 'rebalance_date']].drop_duplicates().shape[0]}`",
        "",
        "Grouped review-year return summary:",
    ]

    for fold_id in sorted(df["fold_id"].unique()):
        fold_df = df[df["fold_id"] == fold_id]
        lines.append(f"- `{fold_id}`")
        for scenario_name in [SCENARIO_BASE, SCENARIO_ENHANCED]:
            for combo_name in COMBO_NAMES:
                subset = fold_df[(fold_df["scenario_name"] == scenario_name) & (fold_df["combo_name"] == combo_name)]
                if subset.empty:
                    continue
                mean_by_bucket = subset.groupby("bucket")["avg_return"].mean().to_dict()
                top_bottom = mean_by_bucket.get(5, 0.0) - mean_by_bucket.get(1, 0.0)
                lines.append(
                    f"- `{fold_id}` `{scenario_name}` `{combo_name}` | "
                    f"bucket1=`{mean_by_bucket.get(1, '')}` | bucket5=`{mean_by_bucket.get(5, '')}` | "
                    f"top_minus_bottom=`{round(float(top_bottom), 10)}`"
                )

    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_GROUPS_PATH.name}]({OUTPUT_GROUPS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)

    # Build the main result rows first so the detail script always follows the same
    # eligibility logic as the annual refresh driver.
    build_result_rows(panel_df, folds, base_rows, enhanced_rows, universe_rows)
    rows = build_group_rows(panel_df, folds, base_rows, enhanced_rows, universe_rows)
    write_group_rows(rows)
    write_summary(rows)
    print(OUTPUT_GROUPS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
