import csv
from pathlib import Path

import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import load_factor_universe


SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_v1_results.csv"
SELECTION_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_v1_factor_selection.csv"
OUTPUT_CSV_PATH = SCRIPT_DIR / "formal_annual_backtest_summary_v1.csv"
OUTPUT_MD_PATH = SCRIPT_DIR / "formal_annual_backtest_summary_v1.md"

BENCHMARK_SCENARIO = "base_core_7"
PRIMARY_SCENARIO = "base_plus_top2_9"
PRIMARY_COMBO = "combo__ic_weight_train"


def join_names(names: list[str]) -> str:
    return "|".join(sorted(names))


def load_factor_sets() -> dict[str, dict[str, list[str]]]:
    df = pd.read_csv(SELECTION_PATH, encoding="utf-8-sig")
    df["keep_flag"] = pd.to_numeric(df["keep_flag"], errors="coerce").fillna(0).astype(int)
    kept = df[df["keep_flag"] == 1].copy()
    base_rows, enhanced_rows, _ = load_factor_universe()
    base_allowed = {row["factor_name"] for row in base_rows}
    enhanced_allowed = {row["factor_name"] for row in enhanced_rows}

    factor_sets: dict[str, dict[str, list[str]]] = {}
    for fold_id, fold_df in kept.groupby("fold_id"):
        kept_names = set(fold_df["factor_name"].drop_duplicates().tolist())
        base_names = sorted(kept_names & base_allowed)
        primary_names = sorted(kept_names & enhanced_allowed)
        improvement_names = sorted([name for name in primary_names if name not in base_allowed])
        factor_sets[str(fold_id)] = {
            "base_names": base_names,
            "improvement_names": improvement_names,
            "all_names": primary_names,
        }
    return factor_sets


def build_summary_rows() -> list[dict[str, object]]:
    results_df = pd.read_csv(RESULTS_PATH, encoding="utf-8-sig")
    factor_sets = load_factor_sets()

    filtered = results_df[results_df["combo_name"] == PRIMARY_COMBO].copy()
    filtered = filtered[filtered["scenario_name"].isin([BENCHMARK_SCENARIO, PRIMARY_SCENARIO])]

    rows: list[dict[str, object]] = []
    for fold_id in sorted(filtered["fold_id"].unique()):
        fold_df = filtered[filtered["fold_id"] == fold_id].copy()
        benchmark = fold_df[fold_df["scenario_name"] == BENCHMARK_SCENARIO].iloc[0]
        primary = fold_df[fold_df["scenario_name"] == PRIMARY_SCENARIO].iloc[0]
        factor_set = factor_sets.get(str(fold_id), {"base_names": [], "improvement_names": [], "all_names": []})

        benchmark_ic = float(benchmark["review_rank_ic_mean"])
        primary_ic = float(primary["review_rank_ic_mean"])
        benchmark_spread = float(benchmark["review_top_minus_bottom"])
        primary_spread = float(primary["review_top_minus_bottom"])

        rows.append(
            {
                "fold_id": fold_id,
                "review_start": str(primary["review_start"]),
                "review_end": str(primary["review_end"]),
                "benchmark_scenario": BENCHMARK_SCENARIO,
                "benchmark_combo": PRIMARY_COMBO,
                "benchmark_review_ic": round(benchmark_ic, 6),
                "benchmark_review_spread": round(benchmark_spread, 10),
                "benchmark_positive_ic_ratio": round(float(benchmark["review_positive_ic_ratio"]), 6),
                "benchmark_selected_count": int(benchmark["selected_factor_count"]),
                "primary_scenario": PRIMARY_SCENARIO,
                "primary_combo": PRIMARY_COMBO,
                "primary_review_ic": round(primary_ic, 6),
                "primary_review_spread": round(primary_spread, 10),
                "primary_positive_ic_ratio": round(float(primary["review_positive_ic_ratio"]), 6),
                "primary_selected_count": int(primary["selected_factor_count"]),
                "delta_review_ic": round(primary_ic - benchmark_ic, 6),
                "delta_review_spread": round(primary_spread - benchmark_spread, 10),
                "base_factor_count": len(factor_set["base_names"]),
                "improvement_factor_count": len(factor_set["improvement_names"]),
                "base_factor_names": join_names(factor_set["base_names"]),
                "improvement_factor_names": join_names(factor_set["improvement_names"]),
                "primary_factor_names": join_names(factor_set["all_names"]),
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_CSV_PATH.write_text("", encoding="utf-8")
        return
    with OUTPUT_CSV_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_MD_PATH.write_text("# Formal Annual Backtest Summary V1\n\n- no rows", encoding="utf-8")
        return

    df = pd.DataFrame(rows)
    mean_benchmark_ic = df["benchmark_review_ic"].mean()
    mean_primary_ic = df["primary_review_ic"].mean()
    mean_benchmark_spread = df["benchmark_review_spread"].mean()
    mean_primary_spread = df["primary_review_spread"].mean()
    primary_win_ic = int((df["delta_review_ic"] > 0).sum())
    primary_win_spread = int((df["delta_review_spread"] > 0).sum())

    lines = [
        "# Formal Annual Backtest Summary V1",
        "",
        "This summary freezes the formal annual backtest comparison onto the annual rule draft's primary and benchmark lines.",
        "",
        f"- benchmark line: `{BENCHMARK_SCENARIO} + {PRIMARY_COMBO}`",
        f"- primary line: `{PRIMARY_SCENARIO} + {PRIMARY_COMBO}`",
        f"- fold count: `{len(rows)}`",
        f"- mean benchmark review IC: `{round(float(mean_benchmark_ic), 6)}`",
        f"- mean primary review IC: `{round(float(mean_primary_ic), 6)}`",
        f"- mean benchmark top-bottom spread: `{round(float(mean_benchmark_spread), 10)}`",
        f"- mean primary top-bottom spread: `{round(float(mean_primary_spread), 10)}`",
        f"- primary wins on review IC: `{primary_win_ic}/{len(rows)}`",
        f"- primary wins on top-bottom spread: `{primary_win_spread}/{len(rows)}`",
        "",
        "Annual fold comparison:",
    ]

    for row in rows:
        lines.extend(
            [
                f"- `{row['fold_id']}` | review=`{row['review_start']}` to `{row['review_end']}`",
                f"  benchmark_ic=`{row['benchmark_review_ic']}` | primary_ic=`{row['primary_review_ic']}` | delta_ic=`{row['delta_review_ic']}`",
                f"  benchmark_spread=`{row['benchmark_review_spread']}` | primary_spread=`{row['primary_review_spread']}` | delta_spread=`{row['delta_review_spread']}`",
                f"  base_count=`{row['base_factor_count']}` | improvement_count=`{row['improvement_factor_count']}` | primary_selected_count=`{row['primary_selected_count']}`",
                f"  base_factors=`{row['base_factor_names'] or 'none'}`",
                f"  improvement_factors=`{row['improvement_factor_names'] or 'none'}`",
            ]
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "- the primary 7+2 shell is kept as the formal main line because it preserves room for yearly improvement supplementation",
            "- the base-only benchmark remains necessary because average review IC is still slightly stronger on the benchmark line in the current sample",
            "- annual comparison should therefore focus on whether the primary line wins often enough on spread and future extensions, not only on the full-period mean IC",
            "",
            "Outputs:",
            f"- [{OUTPUT_CSV_PATH.name}]({OUTPUT_CSV_PATH})",
        ]
    )
    OUTPUT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_summary_rows()
    write_csv(rows)
    write_md(rows)
    print(OUTPUT_CSV_PATH)
    print(OUTPUT_MD_PATH)


if __name__ == "__main__":
    main()
