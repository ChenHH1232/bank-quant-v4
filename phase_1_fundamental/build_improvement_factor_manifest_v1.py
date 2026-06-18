import csv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CORE_MANIFEST_PATH = SCRIPT_DIR / "single_factor_manifest_core_v2.csv"
OUTPUT_PATH = SCRIPT_DIR / "improvement_factor_manifest_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "improvement_factor_manifest_v1.md"

QUARTER_TARGET = "y_quarter_avg_daily_return_close"
YEAR_TARGET = "y_year_avg_daily_return_close"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows(core_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in core_rows:
        factor_name = row["factor_name"]
        factor_family = row["factor_family"]
        target_label = row["target_label"]
        source_type = row["source_type"]
        pool_status = row["pool_status"]

        if target_label == QUARTER_TARGET:
            for variant_name, variant_label in [
                ("snapshot_delta", "上一次可用值变化"),
                ("season_yoy_delta", "去年同季变化"),
            ]:
                output.append(
                    {
                        "factor_name": f"improve__{variant_name}__{factor_name}",
                        "base_factor_name": factor_name,
                        "factor_family": f"improvement_{factor_family}",
                        "improvement_variant": variant_name,
                        "improvement_variant_cn": variant_label,
                        "target_label": target_label,
                        "source_type": source_type,
                        "pool_status": pool_status,
                        "train_start": row["train_start"],
                        "train_end": row["train_end"],
                        "validation_start": row["validation_start"],
                        "validation_end": row["validation_end"],
                        "sample_filter": row["sample_filter"],
                    }
                )
        elif target_label == YEAR_TARGET:
            output.append(
                {
                    "factor_name": f"improve__annual_delta__{factor_name}",
                    "base_factor_name": factor_name,
                    "factor_family": f"improvement_{factor_family}",
                    "improvement_variant": "annual_delta",
                    "improvement_variant_cn": "上一年变化",
                    "target_label": target_label,
                    "source_type": source_type,
                    "pool_status": pool_status,
                    "train_start": row["train_start"],
                    "train_end": row["train_end"],
                    "validation_start": row["validation_start"],
                    "validation_end": row["validation_end"],
                    "sample_filter": row["sample_filter"],
                }
            )
    return output


def write_rows(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "factor_name",
        "base_factor_name",
        "factor_family",
        "improvement_variant",
        "improvement_variant_cn",
        "target_label",
        "source_type",
        "pool_status",
        "train_start",
        "train_end",
        "validation_start",
        "validation_end",
        "sample_filter",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]]) -> None:
    quarter_count = sum(1 for row in rows if row["target_label"] == QUARTER_TARGET)
    annual_count = sum(1 for row in rows if row["target_label"] == YEAR_TARGET)
    lines = [
        "# Improvement Factor Manifest V1",
        "",
        f"- Total improvement candidates: `{len(rows)}`",
        f"- Quarterly-style improvement candidates: `{quarter_count}`",
        f"- Annual bank-indicator improvement candidates: `{annual_count}`",
        "",
        "Improvement rules:",
        "- `snapshot_delta`: current value minus previous available rebalance snapshot for the same stock",
        "- `season_yoy_delta`: current value minus prior-year same-season snapshot for the same stock",
        "- `annual_delta`: current annual bank-indicator value minus previous source-year value for the same stock",
        "",
        "Output:",
        f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    core_rows = load_rows(CORE_MANIFEST_PATH)
    rows = build_rows(core_rows)
    write_rows(rows)
    write_summary(rows)
    print(f"improvement_candidates={len(rows)}")
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
