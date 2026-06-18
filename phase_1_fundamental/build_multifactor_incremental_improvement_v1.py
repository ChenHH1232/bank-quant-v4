import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_multifactor_combo_core_v2 import (
    TRAIN_END,
    TRAIN_START,
    VALIDATION_END,
    VALIDATION_START,
    assign_groups,
    evaluate_combo,
    load_panel,
    load_rows,
    preprocess_factor,
)


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
CORE_RESULTS_PATH = SCRIPT_DIR / "single_factor_test_results_core_v2.csv"
CORE_POOL_PATH = SCRIPT_DIR / "final_core_factor_pool_v2_trimmed.csv"
IMPROVEMENT_PANEL_PATH = SCRIPT_DIR / "improvement_factor_panel_v1.csv"
IMPROVEMENT_RESULTS_PATH = SCRIPT_DIR / "improvement_factor_test_results_v1.csv"
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "multifactor_incremental_improvement_v1.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "multifactor_incremental_improvement_v1.md"


def prepare_core_metadata() -> list[dict[str, str]]:
    pool_rows = load_rows(CORE_POOL_PATH)
    result_rows = {row["factor_name"]: row for row in load_rows(CORE_RESULTS_PATH)}
    metadata: list[dict[str, str]] = []
    for row in pool_rows:
        if row["final_status"] != "keep_final":
            continue
        factor_name = row["factor_name"]
        result_row = result_rows[factor_name]
        metadata.append(
            {
                "factor_name": factor_name,
                "factor_family": row["factor_family"],
                "target_label": result_row["target_label"],
                "direction": result_row["direction"],
                "validation_rank_ic_mean": result_row["validation_rank_ic_mean"],
                "source_group": "core",
            }
        )
    return metadata


def prepare_improvement_metadata() -> list[dict[str, str]]:
    rows = load_rows(IMPROVEMENT_RESULTS_PATH)
    metadata: list[dict[str, str]] = []
    for row in rows:
        if row["final_status"] != "A":
            continue
        metadata.append(
            {
                "factor_name": row["factor_name"],
                "factor_family": row["factor_family"],
                "target_label": row["target_label"],
                "direction": row["direction"],
                "validation_rank_ic_mean": row["validation_rank_ic_mean"],
                "source_group": "improvement",
            }
        )
    return metadata


def load_combined_panel() -> pd.DataFrame:
    base_df = load_panel(BASE_PANEL_PATH)
    improvement_df = pd.read_csv(IMPROVEMENT_PANEL_PATH, encoding="utf-8-sig")
    improvement_df["rebalance_date"] = pd.to_datetime(improvement_df["rebalance_date"])
    merge_cols = [col for col in improvement_df.columns if col.startswith("improve__")]
    combined = base_df.merge(
        improvement_df[["rebalance_date", "code"] + merge_cols],
        how="left",
        on=["rebalance_date", "code"],
    )
    return combined


def build_scored_panel(panel_df: pd.DataFrame, metadata_rows: list[dict[str, str]]) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    df = panel_df.copy()
    train_mask = (df["rebalance_date"] >= TRAIN_START) & (df["rebalance_date"] < TRAIN_END)

    quarter_factors: list[str] = []
    year_factors: list[str] = []
    for row in metadata_rows:
        factor_name = row["factor_name"]
        z_col = f"z__{factor_name}"
        adj_col = f"adj__{factor_name}"
        df[z_col] = preprocess_factor(df, train_mask, factor_name)
        multiplier = 1.0 if row["direction"] == "larger_better" else -1.0
        df[adj_col] = df[z_col] * multiplier
        if row["target_label"] == "y_year_avg_daily_return_close":
            year_factors.append(adj_col)
        else:
            quarter_factors.append(adj_col)

    return df, {
        "quarter_factors": quarter_factors,
        "year_factors": year_factors,
        "all_factors": quarter_factors + year_factors,
    }


def add_combo_scores(df: pd.DataFrame, metadata_rows: list[dict[str, str]], factor_groups: dict[str, list[str]]) -> pd.DataFrame:
    df = df.copy()
    all_factors = factor_groups["all_factors"]
    quarter_factors = factor_groups["quarter_factors"]
    year_factors = factor_groups["year_factors"]

    ic_weight_map = {
        f"adj__{row['factor_name']}": abs(float(row["validation_rank_ic_mean"])) for row in metadata_rows
    }

    df["combo__equal_weight"] = df[all_factors].mean(axis=1, skipna=True)

    ic_total = sum(ic_weight_map[col] for col in all_factors if col in ic_weight_map)
    if ic_total > 0:
        weighted_sum = None
        for col in all_factors:
            part = df[col] * (ic_weight_map[col] / ic_total)
            weighted_sum = part if weighted_sum is None else weighted_sum + part
        df["combo__ic_weight"] = weighted_sum
    else:
        df["combo__ic_weight"] = np.nan

    quarterly_mean = df[quarter_factors].mean(axis=1, skipna=True) if quarter_factors else np.nan
    annual_mean = df[year_factors].mean(axis=1, skipna=True) if year_factors else np.nan
    if quarter_factors and year_factors:
        df["combo__quarterly_plus_annual"] = (quarterly_mean * 0.67) + (annual_mean * 0.33)
    elif quarter_factors:
        df["combo__quarterly_plus_annual"] = quarterly_mean
    else:
        df["combo__quarterly_plus_annual"] = annual_mean
    return df


def evaluate_combo_set(scored_df: pd.DataFrame) -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    for combo_name in ["combo__equal_weight", "combo__ic_weight", "combo__quarterly_plus_annual"]:
        train_metrics = evaluate_combo(scored_df, combo_name, "y_quarter_avg_daily_return_close", TRAIN_START, TRAIN_END)
        validation_metrics = evaluate_combo(scored_df, combo_name, "y_quarter_avg_daily_return_close", VALIDATION_START, VALIDATION_END)
        output[combo_name] = {
            "train_rank_ic_mean": train_metrics["rank_ic_mean"],
            "train_rank_ic_ir": train_metrics["rank_ic_ir"],
            "train_top_minus_bottom": train_metrics["top_minus_bottom"],
            "validation_rank_ic_mean": validation_metrics["rank_ic_mean"],
            "validation_rank_ic_ir": validation_metrics["rank_ic_ir"],
            "validation_top_minus_bottom": validation_metrics["top_minus_bottom"],
        }
    return output


def build_rows() -> list[dict[str, object]]:
    panel_df = load_combined_panel()
    core_metadata = prepare_core_metadata()
    improvement_metadata = prepare_improvement_metadata()

    baseline_scored, baseline_groups = build_scored_panel(panel_df, core_metadata)
    baseline_scored = add_combo_scores(baseline_scored, core_metadata, baseline_groups)
    baseline_metrics = evaluate_combo_set(baseline_scored)

    rows: list[dict[str, object]] = []
    baseline_primary = baseline_metrics["combo__quarterly_plus_annual"]
    rows.append(
        {
            "scenario_name": "baseline_core_v2",
            "added_factor": "",
            "added_factor_family": "",
            "validation_rank_ic_mean": baseline_primary["validation_rank_ic_mean"],
            "validation_rank_ic_ir": baseline_primary["validation_rank_ic_ir"],
            "validation_top_minus_bottom": baseline_primary["validation_top_minus_bottom"],
            "train_rank_ic_mean": baseline_primary["train_rank_ic_mean"],
            "train_rank_ic_ir": baseline_primary["train_rank_ic_ir"],
            "train_top_minus_bottom": baseline_primary["train_top_minus_bottom"],
            "delta_validation_rank_ic_mean": 0.0,
            "delta_validation_top_minus_bottom": 0.0,
            "best_combo_name": "combo__quarterly_plus_annual",
            "comparison_note": "baseline",
        }
    )

    for candidate in improvement_metadata:
        scenario_metadata = core_metadata + [candidate]
        scored_df, factor_groups = build_scored_panel(panel_df, scenario_metadata)
        scored_df = add_combo_scores(scored_df, scenario_metadata, factor_groups)
        scenario_metrics = evaluate_combo_set(scored_df)

        best_combo_name = None
        best_combo_metrics = None
        best_sort_key = None
        for combo_name, metrics in scenario_metrics.items():
            val_ic = float(metrics["validation_rank_ic_mean"]) if metrics["validation_rank_ic_mean"] != "" else -999.0
            val_spread = float(metrics["validation_top_minus_bottom"]) if metrics["validation_top_minus_bottom"] != "" else -999.0
            sort_key = (val_ic, val_spread)
            if best_sort_key is None or sort_key > best_sort_key:
                best_sort_key = sort_key
                best_combo_name = combo_name
                best_combo_metrics = metrics

        assert best_combo_name is not None
        assert best_combo_metrics is not None

        rows.append(
            {
                "scenario_name": f"baseline_plus__{candidate['factor_name']}",
                "added_factor": candidate["factor_name"],
                "added_factor_family": candidate["factor_family"],
                "validation_rank_ic_mean": best_combo_metrics["validation_rank_ic_mean"],
                "validation_rank_ic_ir": best_combo_metrics["validation_rank_ic_ir"],
                "validation_top_minus_bottom": best_combo_metrics["validation_top_minus_bottom"],
                "train_rank_ic_mean": best_combo_metrics["train_rank_ic_mean"],
                "train_rank_ic_ir": best_combo_metrics["train_rank_ic_ir"],
                "train_top_minus_bottom": best_combo_metrics["train_top_minus_bottom"],
                "delta_validation_rank_ic_mean": round(
                    float(best_combo_metrics["validation_rank_ic_mean"]) - float(baseline_primary["validation_rank_ic_mean"]), 6
                ),
                "delta_validation_top_minus_bottom": round(
                    float(best_combo_metrics["validation_top_minus_bottom"]) - float(baseline_primary["validation_top_minus_bottom"]), 8
                ),
                "best_combo_name": best_combo_name,
                "comparison_note": "best combo selected by validation IC then spread",
            }
        )
    return rows


def write_rows(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df = df.sort_values(
        ["delta_validation_rank_ic_mean", "delta_validation_top_minus_bottom"],
        ascending=[False, False],
    )
    df.to_csv(OUTPUT_RESULTS_PATH, index=False, encoding="utf-8-sig")
    return df


def write_summary(df: pd.DataFrame) -> None:
    baseline = df[df["scenario_name"] == "baseline_core_v2"].iloc[0]
    candidates = df[df["scenario_name"] != "baseline_core_v2"].copy()
    positive = candidates[
        (pd.to_numeric(candidates["delta_validation_rank_ic_mean"], errors="coerce") > 0)
        | (pd.to_numeric(candidates["delta_validation_top_minus_bottom"], errors="coerce") > 0)
    ].copy()

    lines = [
        "# Multifactor Incremental Improvement V1",
        "",
        "Baseline reference:",
        f"- combo: `{baseline['best_combo_name']}`",
        f"- validation ic: `{baseline['validation_rank_ic_mean']}`",
        f"- validation top-bottom: `{baseline['validation_top_minus_bottom']}`",
        "",
        f"- Improvement candidates tested: `{len(candidates)}`",
        f"- Positive delta candidates: `{len(positive)}`",
        "",
        "Top candidates by validation delta:",
    ]
    top_rows = candidates.head(10)
    for _, row in top_rows.iterrows():
        lines.append(
            f"- `{row['added_factor']}` | best_combo=`{row['best_combo_name']}` | "
            f"delta_ic=`{row['delta_validation_rank_ic_mean']}` | "
            f"delta_spread=`{row['delta_validation_top_minus_bottom']}`"
        )
    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_RESULTS_PATH.name}]({OUTPUT_RESULTS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    df = write_rows(rows)
    write_summary(df)
    print(OUTPUT_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
