import csv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
OUTPUT_PATH = SCRIPT_DIR / "single_factor_manifest_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "single_factor_manifest_v1.md"

EXCLUDED_COLUMNS = {
    "rebalance_date",
    "quarter_key",
    "code",
    "active_quarter_key",
    "effective_data_flag",
    "rebalance_stock_pool_flag",
    "liquidity_top_80_flag",
    "market_cap_top_80_flag",
    "avg_traded_amount_lookback",
    "avg_traded_volume_lookback",
    "market_cap",
    "circulating_market_cap",
    "y_quarter_avg_daily_return_close",
    "y_quarter_end_date",
    "y_year_avg_daily_return_close",
    "y_year_end_date",
}


def infer_family(column_name: str) -> str:
    if "__" not in column_name:
        return "other"
    return column_name.split("__", 1)[0]


def infer_target_label(column_name: str) -> str:
    if column_name.startswith("bank_indicator__") and not column_name.endswith("__source_year"):
        return "y_year_avg_daily_return_close"
    return "y_quarter_avg_daily_return_close"


def is_factor_column(column_name: str) -> bool:
    if column_name in EXCLUDED_COLUMNS:
        return False
    if column_name.endswith("__source_year"):
        return False
    return "__" in column_name


def load_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def build_rows(header: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for column_name in header:
        if not is_factor_column(column_name):
            continue
        rows.append(
            {
                "factor_name": column_name,
                "factor_family": infer_family(column_name),
                "target_label": infer_target_label(column_name),
                "train_start": "2014-05-01",
                "train_end": "2019-05-01",
                "validation_start": "2019-05-01",
                "validation_end": "2021-05-01",
                "sample_filter": "rebalance_stock_pool_flag=1",
                "primary_group_count": "5",
                "robustness_group_count": "3",
                "status": "pending",
            }
        )
    return rows


def write_rows(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "factor_name",
        "factor_family",
        "target_label",
        "train_start",
        "train_end",
        "validation_start",
        "validation_end",
        "sample_filter",
        "primary_group_count",
        "robustness_group_count",
        "status",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]]) -> None:
    family_counts: dict[str, int] = {}
    for row in rows:
        family = row["factor_family"]
        family_counts[family] = family_counts.get(family, 0) + 1

    lines = [
        "# Single-Factor Manifest V1",
        "",
        "Scope:",
        "- built from `phase1_training_panel.csv`",
        "- includes only modeled factor columns",
        "- excludes helper columns, pool flags, identifiers, and target columns",
        "",
        "Window:",
        "- training: `2014-05-01` to `2019-05-01`",
        "- validation: `2019-05-01` to `2021-05-01`",
        "",
        f"- Total candidate factors: `{len(rows)}`",
        "",
        "Family counts:",
    ]
    for family, count in sorted(family_counts.items()):
        lines.append(f"- `{family}`: `{count}`")
    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    header = load_header(PANEL_PATH)
    rows = build_rows(header)
    write_rows(rows)
    write_summary(rows)
    print(f"factors={len(rows)}")
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
