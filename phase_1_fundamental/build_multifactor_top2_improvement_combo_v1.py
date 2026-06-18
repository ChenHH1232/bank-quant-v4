from pathlib import Path

import pandas as pd

from build_multifactor_incremental_improvement_v1 import (
    OUTPUT_RESULTS_PATH as INCREMENTAL_RESULTS_PATH,
    add_combo_scores,
    build_scored_panel,
    evaluate_combo_set,
    load_combined_panel,
    prepare_core_metadata,
    prepare_improvement_metadata,
)


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "multifactor_top2_improvement_combo_v1.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "multifactor_top2_improvement_combo_v1.md"


def pick_top2_candidates() -> list[str]:
    df = pd.read_csv(INCREMENTAL_RESULTS_PATH, encoding="utf-8-sig")
    candidates = df[df["added_factor"].fillna("") != ""].copy()
    candidates = candidates.sort_values(
        ["delta_validation_rank_ic_mean", "delta_validation_top_minus_bottom"],
        ascending=[False, False],
    )
    return candidates["added_factor"].head(2).tolist()


def find_metadata_by_name(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["factor_name"]: row for row in rows}


def evaluate_scenario(panel_df: pd.DataFrame, metadata_rows: list[dict[str, str]], scenario_name: str) -> dict[str, object]:
    scored_df, factor_groups = build_scored_panel(panel_df, metadata_rows)
    scored_df = add_combo_scores(scored_df, metadata_rows, factor_groups)
    combo_metrics = evaluate_combo_set(scored_df)

    best_combo_name = None
    best_combo_metrics = None
    best_sort_key = None
    for combo_name, metrics in combo_metrics.items():
        val_ic = float(metrics["validation_rank_ic_mean"]) if metrics["validation_rank_ic_mean"] != "" else -999.0
        val_spread = float(metrics["validation_top_minus_bottom"]) if metrics["validation_top_minus_bottom"] != "" else -999.0
        sort_key = (val_ic, val_spread)
        if best_sort_key is None or sort_key > best_sort_key:
            best_sort_key = sort_key
            best_combo_name = combo_name
            best_combo_metrics = metrics

    assert best_combo_name is not None
    assert best_combo_metrics is not None

    return {
        "scenario_name": scenario_name,
        "best_combo_name": best_combo_name,
        "validation_rank_ic_mean": best_combo_metrics["validation_rank_ic_mean"],
        "validation_rank_ic_ir": best_combo_metrics["validation_rank_ic_ir"],
        "validation_top_minus_bottom": best_combo_metrics["validation_top_minus_bottom"],
        "train_rank_ic_mean": best_combo_metrics["train_rank_ic_mean"],
        "train_rank_ic_ir": best_combo_metrics["train_rank_ic_ir"],
        "train_top_minus_bottom": best_combo_metrics["train_top_minus_bottom"],
    }


def build_rows() -> list[dict[str, object]]:
    panel_df = load_combined_panel()
    core_metadata = prepare_core_metadata()
    improvement_map = find_metadata_by_name(prepare_improvement_metadata())
    top2 = pick_top2_candidates()

    baseline = evaluate_scenario(panel_df, core_metadata, "baseline_core_v2")
    baseline_ic = float(baseline["validation_rank_ic_mean"])
    baseline_spread = float(baseline["validation_top_minus_bottom"])

    scenarios: list[tuple[str, list[str]]] = [
        ("baseline_core_v2", []),
        (f"baseline_plus__{top2[0]}", [top2[0]]),
        (f"baseline_plus__{top2[1]}", [top2[1]]),
        ("baseline_plus__top2_together", top2),
    ]

    rows: list[dict[str, object]] = []
    for scenario_name, factor_names in scenarios:
        metadata_rows = core_metadata + [improvement_map[name] for name in factor_names]
        result = evaluate_scenario(panel_df, metadata_rows, scenario_name)
        result["added_factors"] = "|".join(factor_names)
        result["improvement_factor_count"] = len(factor_names)
        result["delta_validation_rank_ic_mean"] = round(float(result["validation_rank_ic_mean"]) - baseline_ic, 6)
        result["delta_validation_top_minus_bottom"] = round(float(result["validation_top_minus_bottom"]) - baseline_spread, 8)
        rows.append(result)
    return rows


def write_rows(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    order = {
        "baseline_core_v2": 0,
        rows[1]["scenario_name"]: 1,
        rows[2]["scenario_name"]: 2,
        "baseline_plus__top2_together": 3,
    }
    df["_order"] = df["scenario_name"].map(order)
    df = df.sort_values("_order").drop(columns=["_order"])
    df.to_csv(OUTPUT_RESULTS_PATH, index=False, encoding="utf-8-sig")
    return df


def write_summary(df: pd.DataFrame) -> None:
    baseline = df.iloc[0]
    top1 = df.iloc[1]
    top2 = df.iloc[2]
    together = df.iloc[3]
    lines = [
        "# Multifactor Top2 Improvement Combo V1",
        "",
        f"- Baseline combo: `{baseline['best_combo_name']}` | val_ic=`{baseline['validation_rank_ic_mean']}` | spread=`{baseline['validation_top_minus_bottom']}`",
        f"- Top1 alone: `{top1['added_factors']}` | val_ic=`{top1['validation_rank_ic_mean']}` | delta_ic=`{top1['delta_validation_rank_ic_mean']}`",
        f"- Top2 alone: `{top2['added_factors']}` | val_ic=`{top2['validation_rank_ic_mean']}` | delta_ic=`{top2['delta_validation_rank_ic_mean']}`",
        f"- Together: `{together['added_factors']}` | val_ic=`{together['validation_rank_ic_mean']}` | delta_ic=`{together['delta_validation_rank_ic_mean']}` | delta_spread=`{together['delta_validation_top_minus_bottom']}`",
        "",
        "Outputs:",
        f"- [{OUTPUT_RESULTS_PATH.name}]({OUTPUT_RESULTS_PATH})",
    ]
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    df = write_rows(rows)
    write_summary(df)
    print(OUTPUT_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
