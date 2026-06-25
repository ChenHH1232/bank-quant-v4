import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_BASE,
    SCENARIO_ENHANCED,
    add_combo_scores,
    build_scenario_rows,
    build_yearly_folds,
    get_may_rebalance_dates,
    load_factor_universe,
    select_factor_rows,
)
from build_pre2021_rolling_validation_v1 import (
    BASE_PANEL_PATH,
    IMPROVEMENT_PANEL_PATH,
    assign_groups,
    build_scored_panel,
)


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_LOCAL_DETAIL_PATH = SCRIPT_DIR / "execution_faithful_validation_v1_local_detail.csv"
OUTPUT_LOCAL_SUMMARY_PATH = SCRIPT_DIR / "execution_faithful_validation_v1_local_summary.csv"
OUTPUT_REPORT_PATH = SCRIPT_DIR / "execution_faithful_validation_v1.md"

TARGET_COMBO = "combo__ic_weight_train"
TARGET_SCENARIO = SCENARIO_BASE
TARGET_YEARS = [2021, 2022, 2024, 2025]


def load_full_panel_with_pool_flag() -> pd.DataFrame:
    base_df = pd.read_csv(BASE_PANEL_PATH, encoding="utf-8-sig")
    base_df["rebalance_date"] = pd.to_datetime(base_df["rebalance_date"])

    improvement_df = pd.read_csv(IMPROVEMENT_PANEL_PATH, encoding="utf-8-sig")
    improvement_df["rebalance_date"] = pd.to_datetime(improvement_df["rebalance_date"])
    improve_cols = [col for col in improvement_df.columns if col.startswith("improve__")]

    merged = base_df.merge(
        improvement_df[["rebalance_date", "code"] + improve_cols],
        how="left",
        on=["rebalance_date", "code"],
    )
    merged["rebalance_stock_pool_flag"] = pd.to_numeric(
        merged["rebalance_stock_pool_flag"], errors="coerce"
    ).fillna(0).astype(int)
    return merged


def load_scoring_panel(full_panel_df: pd.DataFrame) -> pd.DataFrame:
    return full_panel_df[full_panel_df["rebalance_stock_pool_flag"] == 1].copy()


def pick_target_dates(scoring_panel_df: pd.DataFrame) -> list[pd.Timestamp]:
    may_dates = get_may_rebalance_dates(scoring_panel_df)
    chosen: list[pd.Timestamp] = []
    for year in TARGET_YEARS:
        year_dates = [d for d in may_dates if pd.Timestamp(d).year == year]
        if year_dates:
            chosen.append(pd.Timestamp(sorted(year_dates)[0]))
    return chosen


def get_fold_for_date(folds: list[dict[str, object]], rebalance_date: pd.Timestamp) -> dict[str, object]:
    for fold in folds:
        review_start = pd.Timestamp(fold["review_start"])
        review_end = pd.Timestamp(fold["review_end"])
        if review_start <= rebalance_date <= review_end:
            return fold
    raise KeyError(f"No annual fold found for {rebalance_date.strftime('%Y-%m-%d')}")


def build_factor_weight_map(train_ic_weight_map: dict[str, float], factor_groups: dict[str, list[str]]) -> dict[str, float]:
    factor_cols = factor_groups["all_factors"]
    total_weight = sum(float(train_ic_weight_map.get(col, 0.0)) for col in factor_cols)
    if total_weight <= 0:
        return {col: np.nan for col in factor_cols}
    return {
        col: float(train_ic_weight_map.get(col, 0.0)) / total_weight
        for col in factor_cols
    }


def build_local_packet_rows(
    full_panel_df: pd.DataFrame,
    scoring_panel_df: pd.DataFrame,
    folds: list[dict[str, object]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    detail_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for rebalance_date in pick_target_dates(scoring_panel_df):
        fold = get_fold_for_date(folds, rebalance_date)
        train_start = pd.Timestamp(fold["train_start"])
        test_start = pd.Timestamp(fold["test_start"])
        train_mask = (scoring_panel_df["rebalance_date"] >= train_start) & (
            scoring_panel_df["rebalance_date"] < test_start
        )

        selected_rows, _ = select_factor_rows(scoring_panel_df, universe_rows, fold)
        scenario_map = build_scenario_rows(selected_rows, base_rows, enhanced_rows)
        scenario_rows = scenario_map.get(TARGET_SCENARIO, [])
        if not scenario_rows:
            continue

        scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
            scoring_panel_df, scenario_rows, train_mask
        )
        scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
        scored_df["final_score"] = pd.to_numeric(scored_df[TARGET_COMBO], errors="coerce")
        factor_weight_map = build_factor_weight_map(train_ic_weight_map, factor_groups)

        date_score_df = scored_df[scored_df["rebalance_date"] == rebalance_date].copy()
        date_score_df[TARGET_COMBO] = pd.to_numeric(date_score_df[TARGET_COMBO], errors="coerce")
        date_score_df = date_score_df.dropna(subset=[TARGET_COMBO]).copy()
        date_score_df = date_score_df.sort_values(["final_score", "code"], ascending=[False, True]).copy()
        date_score_df["score_rank_desc"] = np.arange(1, len(date_score_df) + 1)
        date_score_df["bucket"] = assign_groups(date_score_df[TARGET_COMBO], 5)
        date_score_df = date_score_df.dropna(subset=["bucket"]).copy()
        date_score_df["bucket"] = date_score_df["bucket"].astype(int)
        date_score_df["is_top_bucket"] = (date_score_df["bucket"] == 5).astype(int)

        top_count = int(date_score_df["is_top_bucket"].sum())
        target_weight = 1.0 / float(top_count) if top_count > 0 else np.nan
        date_score_df["target_weight"] = np.where(date_score_df["is_top_bucket"] == 1, target_weight, 0.0)

        score_lookup = date_score_df.set_index("code").to_dict("index")
        full_date_df = full_panel_df[full_panel_df["rebalance_date"] == rebalance_date].copy()

        summary_rows.append(
            {
                "rebalance_date": rebalance_date.strftime("%Y-%m-%d"),
                "fold_id": fold["fold_id"],
                "scenario_name": TARGET_SCENARIO,
                "selected_factor_count": int(len(scenario_rows)),
                "local_pool_count": int(len(date_score_df)),
                "top_bucket_count": top_count,
                "target_weight_each": round(float(target_weight), 10) if pd.notna(target_weight) else "",
                "train_start": fold["train_start"],
                "test_start": fold["test_start"],
                "review_start": fold["review_start"],
                "review_end": fold["review_end"],
            }
        )

        for _, row in full_date_df.iterrows():
            code = str(row["code"])
            scored = score_lookup.get(code, {})
            out_row: dict[str, object] = {
                "rebalance_date": rebalance_date.strftime("%Y-%m-%d"),
                "fold_id": fold["fold_id"],
                "scenario_name": TARGET_SCENARIO,
                "code": code,
                "display_name": row.get("display_name", ""),
                "in_local_pool": int(row.get("rebalance_stock_pool_flag", 0)),
                "final_score": scored.get("final_score", np.nan),
                "score_rank_desc": scored.get("score_rank_desc", np.nan),
                "bucket": scored.get("bucket", np.nan),
                "is_top_bucket": scored.get("is_top_bucket", 0),
                "target_weight": scored.get("target_weight", 0.0),
                "next_period_return": scored.get("y_quarter_avg_daily_return_close", np.nan),
                "next_period_year_return": scored.get("y_year_avg_daily_return_close", np.nan),
            }

            for factor_row in scenario_rows:
                factor_name = factor_row["factor_name"]
                adj_col = f"adj__{factor_name}"
                z_col = f"z__{factor_name}"
                norm_weight = factor_weight_map.get(adj_col, np.nan)
                adj_value = scored.get(adj_col, np.nan)
                out_row[f"raw__{factor_name}"] = row.get(factor_name, np.nan)
                out_row[f"z__{factor_name}"] = scored.get(z_col, np.nan)
                out_row[f"adj__{factor_name}"] = adj_value
                out_row[f"weight__{factor_name}"] = norm_weight
                out_row[f"contrib__{factor_name}"] = (
                    float(adj_value) * float(norm_weight)
                    if pd.notna(adj_value) and pd.notna(norm_weight)
                    else np.nan
                )

            detail_rows.append(out_row)

    return detail_rows, summary_rows


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


def write_report(summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Execution-Faithful Validation V1",
        "",
        "Goal:",
        "- build a local truth packet for selected rebalance dates before comparing with JoinQuant",
        "- use this packet to find where local rolling and JoinQuant begin to diverge",
        "",
        "Scope frozen in this first pass:",
        f"- scenario: `{TARGET_SCENARIO}`",
        f"- combo: `{TARGET_COMBO}`",
        f"- target years: `{', '.join(str(y) for y in TARGET_YEARS)}`",
        "",
        "Local outputs:",
        f"- [execution_faithful_validation_v1_local_summary.csv]({OUTPUT_LOCAL_SUMMARY_PATH})",
        f"- [execution_faithful_validation_v1_local_detail.csv]({OUTPUT_LOCAL_DETAIL_PATH})",
        "",
        "Fields prepared for date-by-date reconciliation:",
        "- local pool membership",
        "- raw factor values",
        "- standardized `z__*` values",
        "- direction-adjusted `adj__*` values",
        "- normalized factor weights and score contribution",
        "- final score",
        "- descending score rank",
        "- bucket assignment",
        "- top-bucket inclusion",
        "- equal target weight inside top bucket",
        "- next-period realized return in the local panel",
        "",
        "JoinQuant side should export the same rebalance dates and the same fields in the same order.",
        "",
        "Selected dates:",
    ]

    for row in summary_rows:
        lines.append(
            f"- `{row['rebalance_date']}` | fold=`{row['fold_id']}` | "
            f"factor_count=`{row['selected_factor_count']}` | "
            f"pool_count=`{row['local_pool_count']}` | "
            f"top_count=`{row['top_bucket_count']}` | "
            f"target_weight_each=`{row['target_weight_each']}`"
        )

    lines.extend(
        [
            "",
            "Recommended reconciliation order:",
            "1. pool membership",
            "2. raw factor values",
            "3. `z__*` standardization",
            "4. `adj__*` sign handling",
            "5. final score and rank",
            "6. bucket / top-bucket selection",
            "7. target weight",
            "8. next-period return mapping",
        ]
    )
    OUTPUT_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    full_panel_df = load_full_panel_with_pool_flag()
    scoring_panel_df = load_scoring_panel(full_panel_df)
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    may_dates = get_may_rebalance_dates(scoring_panel_df)
    folds = build_yearly_folds(may_dates)
    detail_rows, summary_rows = build_local_packet_rows(
        full_panel_df,
        scoring_panel_df,
        folds,
        base_rows,
        enhanced_rows,
        universe_rows,
    )
    write_csv(OUTPUT_LOCAL_DETAIL_PATH, detail_rows)
    write_csv(OUTPUT_LOCAL_SUMMARY_PATH, summary_rows)
    write_report(summary_rows)
    print(OUTPUT_LOCAL_DETAIL_PATH)
    print(OUTPUT_LOCAL_SUMMARY_PATH)
    print(OUTPUT_REPORT_PATH)


if __name__ == "__main__":
    main()
