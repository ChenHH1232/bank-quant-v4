import csv
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
IMPROVEMENT_RESULTS_PATH = SCRIPT_DIR / "improvement_factor_test_results_v1.csv"
OUTPUT_CSV_PATH = SCRIPT_DIR / "controlled_improvement_pool_v1.csv"
OUTPUT_MD_PATH = SCRIPT_DIR / "controlled_improvement_pool_v1.md"

SELECTED_FACTORS = [
    "improve__annual_delta__bank_indicator__Nonperforming_loan_rate",
    "improve__snapshot_delta__derived__investment_income_to_operating_revenue",
    "improve__annual_delta__bank_indicator__capital_adequacy_ratio",
    "improve__season_yoy_delta__derived__staff_cash_to_operating_revenue",
    "improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual",
    "improve__snapshot_delta__indicator__eps",
]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows() -> list[dict[str, object]]:
    result_map = {row["factor_name"]: row for row in load_rows(IMPROVEMENT_RESULTS_PATH)}
    rows: list[dict[str, object]] = []
    for rank, factor_name in enumerate(SELECTED_FACTORS, start=1):
        row = result_map.get(factor_name)
        if row is None:
            raise KeyError(f"Missing improvement result for {factor_name}")
        rows.append(
            {
                "pool_rank": rank,
                "factor_name": factor_name,
                "factor_family": row["factor_family"],
                "target_label": row["target_label"],
                "direction": row["direction"],
                "validation_rank_ic_mean": row["validation_rank_ic_mean"],
                "validation_positive_ic_ratio": row["validation_positive_ic_ratio"],
                "validation_top_minus_bottom": row["validation_top_minus_bottom"],
                "final_status": row["final_status"],
                "pool_role": "controlled_improvement_candidate",
            }
        )
    return rows


def write_summary(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Controlled Improvement Pool V1",
        "",
        "This pool expands the current enhancement layer from the original top2 into a controlled top6 candidate set.",
        "",
        "Selection logic:",
        "- keep the current top2 enhancement factors",
        "- add high-conviction improvement candidates with acceptable validation IC and clear economic interpretation",
        "- do not open the full improvement universe yet",
        "",
        f"- candidate count: `{len(rows)}`",
        "",
        "Candidates:",
    ]
    for row in rows:
        lines.append(
            f"- `{row['factor_name']}` | val_ic=`{row['validation_rank_ic_mean']}` | "
            f"val_pos_ic_ratio=`{row['validation_positive_ic_ratio']}` | "
            f"val_spread=`{row['validation_top_minus_bottom']}`"
        )
    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_CSV_PATH.name}]({OUTPUT_CSV_PATH})",
        ]
    )
    OUTPUT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    pd.DataFrame(rows).to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")
    write_summary(rows)
    print(OUTPUT_CSV_PATH)
    print(OUTPUT_MD_PATH)


if __name__ == "__main__":
    main()
