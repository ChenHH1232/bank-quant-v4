import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
STANDARDIZED_ROOT = SCRIPT_DIR / "standardized_outputs"
OUTPUT_CSV = SCRIPT_DIR / "quarterly_valid_data_segments.csv"
OUTPUT_MD = SCRIPT_DIR / "quarterly_valid_data_segments.md"

REQUIRED_QUARTERLY_FAMILIES = [
    "income",
    "cash_flow",
    "balance",
    "indicator",
    "parent_balance",
]


@dataclass
class QuarterRecord:
    code: str
    quarter_key: str
    report_period_end: str
    rebalance_reference_date: date | None
    family_pub_dates: dict[str, date]
    latest_bank_indicator_year: str | None
    latest_bank_indicator_pub_date: date | None


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def quarter_sort_key(quarter_key: str) -> tuple[int, int]:
    year_text, quarter_text = quarter_key.lower().split("q")
    return int(year_text), int(quarter_text)


def load_standardized_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def existing_codes(root: Path) -> list[str]:
    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and "_" in path.name
    )


def folder_code_to_symbol(folder_code: str) -> str:
    if "_" not in folder_code:
        return folder_code
    left, right = folder_code.split("_", 1)
    return f"{left}.{right}"


def latest_prior_annual_bank_indicator(
    annual_pub_dates: dict[str, date],
    rebalance_reference_date: date | None,
) -> tuple[str | None, date | None]:
    if rebalance_reference_date is None:
        return None, None
    eligible = [
        (year_key, pub_date)
        for year_key, pub_date in annual_pub_dates.items()
        if pub_date <= rebalance_reference_date
    ]
    if not eligible:
        return None, None
    eligible.sort(key=lambda item: (int(item[0]), item[1]))
    return eligible[-1]


def collect_quarter_records_for_code(code: str) -> list[QuarterRecord]:
    code_dir = STANDARDIZED_ROOT / code
    if not code_dir.exists():
        return []

    quarterly_pub_dates: dict[str, dict[str, date]] = defaultdict(dict)
    report_period_end_map: dict[str, str] = {}
    annual_bank_indicator_pub_dates: dict[str, date] = {}

    for family in REQUIRED_QUARTERLY_FAMILIES:
        path = code_dir / f"{family}_standardized.csv"
        if not path.exists():
            continue
        for row in load_standardized_rows(path):
            quarter_key = (row.get("quarter_key") or "").strip()
            pub_date = parse_date(row.get("pub_date", ""))
            standard_value = (row.get("standard_value") or "").strip()
            missing_reason = (row.get("missing_reason") or "").strip()
            if not quarter_key or pub_date is None:
                continue
            if not standard_value and missing_reason:
                continue
            current = quarterly_pub_dates[quarter_key].get(family)
            if current is None or pub_date > current:
                quarterly_pub_dates[quarter_key][family] = pub_date
                report_period_end_map[quarter_key] = row.get("report_period_end", "")

    bank_indicator_path = code_dir / "bank_indicator_standardized.csv"
    if bank_indicator_path.exists():
        for row in load_standardized_rows(bank_indicator_path):
            year_key = (row.get("year_key") or "").strip()
            pub_date = parse_date(row.get("pub_date", ""))
            standard_value = (row.get("standard_value") or "").strip()
            missing_reason = (row.get("missing_reason") or "").strip()
            if not year_key or pub_date is None:
                continue
            if not standard_value and missing_reason:
                continue
            current = annual_bank_indicator_pub_dates.get(year_key)
            if current is None or pub_date > current:
                annual_bank_indicator_pub_dates[year_key] = pub_date

    records: list[QuarterRecord] = []
    for quarter_key in sorted(quarterly_pub_dates, key=quarter_sort_key):
        family_pub_dates = quarterly_pub_dates[quarter_key]
        rebalance_reference_date = None
        if all(family in family_pub_dates for family in REQUIRED_QUARTERLY_FAMILIES):
            rebalance_reference_date = max(family_pub_dates.values())
        latest_year, latest_pub_date = latest_prior_annual_bank_indicator(
            annual_bank_indicator_pub_dates,
            rebalance_reference_date,
        )
        records.append(
            QuarterRecord(
                code=folder_code_to_symbol(code),
                quarter_key=quarter_key,
                report_period_end=report_period_end_map.get(quarter_key, ""),
                rebalance_reference_date=rebalance_reference_date,
                family_pub_dates=family_pub_dates,
                latest_bank_indicator_year=latest_year,
                latest_bank_indicator_pub_date=latest_pub_date,
            )
        )
    return records


def effective_reason(record: QuarterRecord) -> str:
    missing_families = [
        family for family in REQUIRED_QUARTERLY_FAMILIES if family not in record.family_pub_dates
    ]
    if missing_families:
        return f"missing_quarterly_families:{','.join(missing_families)}"
    if record.latest_bank_indicator_pub_date is None:
        return "no_prior_annual_bank_indicator"
    return "ok"


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for code in existing_codes(STANDARDIZED_ROOT):
        records = collect_quarter_records_for_code(code)
        for index, record in enumerate(records):
            next_record = records[index + 1] if index + 1 < len(records) else None
            flag = effective_reason(record) == "ok"
            effective_from = (
                (record.rebalance_reference_date + timedelta(days=1)).isoformat()
                if record.rebalance_reference_date is not None and flag
                else ""
            )
            effective_until = ""
            if flag and next_record and next_record.rebalance_reference_date is not None:
                effective_until = (next_record.rebalance_reference_date).isoformat()
            elif flag:
                effective_until = "open"

            rows.append(
                {
                    "code": record.code,
                    "quarter_key": record.quarter_key,
                    "report_period_end": record.report_period_end,
                    "income_pub_date": record.family_pub_dates.get("income", "").isoformat()
                    if isinstance(record.family_pub_dates.get("income"), date)
                    else "",
                    "cash_flow_pub_date": record.family_pub_dates.get("cash_flow", "").isoformat()
                    if isinstance(record.family_pub_dates.get("cash_flow"), date)
                    else "",
                    "balance_pub_date": record.family_pub_dates.get("balance", "").isoformat()
                    if isinstance(record.family_pub_dates.get("balance"), date)
                    else "",
                    "indicator_pub_date": record.family_pub_dates.get("indicator", "").isoformat()
                    if isinstance(record.family_pub_dates.get("indicator"), date)
                    else "",
                    "parent_balance_pub_date": record.family_pub_dates.get("parent_balance", "").isoformat()
                    if isinstance(record.family_pub_dates.get("parent_balance"), date)
                    else "",
                    "rebalance_reference_date": record.rebalance_reference_date.isoformat()
                    if record.rebalance_reference_date is not None
                    else "",
                    "latest_bank_indicator_year": record.latest_bank_indicator_year or "",
                    "latest_bank_indicator_pub_date": record.latest_bank_indicator_pub_date.isoformat()
                    if record.latest_bank_indicator_pub_date is not None
                    else "",
                    "effective_data_flag": "1" if flag else "0",
                    "effective_from_date": effective_from,
                    "effective_until_date": effective_until,
                    "effective_reason": effective_reason(record),
                }
            )
    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "code",
        "quarter_key",
        "report_period_end",
        "income_pub_date",
        "cash_flow_pub_date",
        "balance_pub_date",
        "indicator_pub_date",
        "parent_balance_pub_date",
        "rebalance_reference_date",
        "latest_bank_indicator_year",
        "latest_bank_indicator_pub_date",
        "effective_data_flag",
        "effective_from_date",
        "effective_until_date",
        "effective_reason",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]]) -> None:
    total_rows = len(rows)
    valid_rows = sum(1 for row in rows if row["effective_data_flag"] == "1")
    invalid_rows = total_rows - valid_rows
    unique_codes = len({row["code"] for row in rows})
    unique_valid_codes = len({row["code"] for row in rows if row["effective_data_flag"] == "1"})
    reason_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        if row["effective_data_flag"] == "0":
            reason_counts[row["effective_reason"]] += 1

    lines = [
        "# Quarterly Valid Data Segments",
        "",
        "Rule:",
        "- A quarter is valid only after all five mandatory quarterly statement families are available.",
        "- The effective start date is the day after the latest mandatory quarterly publish date for that quarter.",
        "- A quarter also needs at least one annual `bank_indicator` snapshot published on or before that quarter's rebalance reference date.",
        "- This file labels data availability only; the future top-80% liquidity and market-cap stock-pool filter is a later overlay at rebalance time.",
        "",
        f"- Banks covered: `{unique_codes}`",
        f"- Banks with at least one valid quarter: `{unique_valid_codes}`",
        f"- Quarter rows: `{total_rows}`",
        f"- Valid quarter rows: `{valid_rows}`",
        f"- Invalid quarter rows: `{invalid_rows}`",
        "",
        "Invalid reason counts:",
    ]
    for reason, count in sorted(reason_counts.items()):
        lines.append(f"- `{reason}`: `{count}`")
    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_CSV.name}]({OUTPUT_CSV})",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    write_summary(rows)
    print(f"rows={len(rows)}")
    print(f"valid_rows={sum(1 for row in rows if row['effective_data_flag'] == '1')}")
    print(OUTPUT_CSV)
    print(OUTPUT_MD)


if __name__ == "__main__":
    main()
