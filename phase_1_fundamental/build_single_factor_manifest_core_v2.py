import csv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CORE_POOL_PATH = SCRIPT_DIR / "final_core_factor_pool_v2.csv"
OUTPUT_PATH = SCRIPT_DIR / "single_factor_manifest_core_v2.csv"
SUMMARY_PATH = SCRIPT_DIR / "single_factor_manifest_core_v2.md"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def infer_target_label(factor_name: str) -> str:
    if factor_name.startswith("bank_indicator__"):
        return "y_year_avg_daily_return_close"
    return "y_quarter_avg_daily_return_close"


def main() -> None:
    pool_rows = load_rows(CORE_POOL_PATH)
    output_rows: list[dict[str, str]] = []
    for row in pool_rows:
        if row["status"] not in {"core_keep", "secondary_candidate", "watch_only"}:
            continue
        factor_name = row["factor_name"]
        output_rows.append(
            {
                "factor_name": factor_name,
                "factor_family": row["factor_family"],
                "target_label": infer_target_label(factor_name),
                "source_type": row["source_type"],
                "pool_status": row["status"],
                "train_start": "2014-05-01",
                "train_end": "2019-05-01",
                "validation_start": "2019-05-01",
                "validation_end": "2021-05-01",
                "sample_filter": "rebalance_stock_pool_flag=1",
            }
        )

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    lines = [
        "# Single-Factor Manifest Core V2",
        "",
        f"- Factors in core-v2 retest scope: `{len(output_rows)}`",
        "",
        "Output:",
        f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"factors={len(output_rows)}")
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
