from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "phase_1_fundamental" / "raw_downloads" / "all_banks"
UNIVERSE_PATH = RAW_ROOT / "bank_universe.csv"
OUTPUT_CSV = ROOT / "phase_2_momentum" / "momentum_v1_local_coverage_check.csv"
OUTPUT_MD = ROOT / "phase_2_momentum" / "momentum_v1_local_coverage_check.md"


@dataclass
class CoverageRow:
    code: str
    listed_start: str
    folder: str
    price_exists: bool
    valuation_exists: bool
    price_rows: int
    valuation_rows: int
    price_has_date: bool
    valuation_has_date: bool
    price_row_match_valuation: bool
    valuation_first_date: str
    valuation_last_date: str
    price_header: str
    valuation_header: str
    status: str


def read_csv_header_and_rows(path: Path) -> tuple[list[str], int]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        return [], 0
    return rows[0], max(len(rows) - 1, 0)


def read_valuation_dates(path: Path) -> tuple[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        first_date = ""
        last_date = ""
        for row in reader:
            day_value = (row.get("day") or row.get("date") or "").strip()
            if day_value and not first_date:
                first_date = day_value
            if day_value:
                last_date = day_value
    return first_date, last_date


def has_date_field(header: list[str]) -> bool:
    normalized = {item.strip().lower() for item in header}
    return any(name in normalized for name in ("date", "day", "datetime", "time"))


def status_from_row(
    price_exists: bool,
    valuation_exists: bool,
    price_has_date: bool,
    valuation_has_date: bool,
) -> str:
    if not price_exists or not valuation_exists:
        return "missing_file"
    if not price_has_date:
        return "blocked_price_missing_date"
    if not valuation_has_date:
        return "blocked_valuation_missing_date"
    return "ready_local_base"


def load_universe() -> list[dict[str, str]]:
    with UNIVERSE_PATH.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def build_rows() -> list[CoverageRow]:
    output: list[CoverageRow] = []
    for item in load_universe():
        code = item["code"]
        folder = code.replace(".", "_")
        bank_dir = RAW_ROOT / folder
        price_path = bank_dir / "daily_price.csv"
        valuation_path = bank_dir / "daily_valuation.csv"

        price_exists = price_path.exists()
        valuation_exists = valuation_path.exists()

        price_header: list[str] = []
        valuation_header: list[str] = []
        price_rows = 0
        valuation_rows = 0
        valuation_first_date = ""
        valuation_last_date = ""

        if price_exists:
            price_header, price_rows = read_csv_header_and_rows(price_path)
        if valuation_exists:
            valuation_header, valuation_rows = read_csv_header_and_rows(valuation_path)
            valuation_first_date, valuation_last_date = read_valuation_dates(valuation_path)

        price_has_date = has_date_field(price_header)
        valuation_has_date = has_date_field(valuation_header)

        output.append(
            CoverageRow(
                code=code,
                listed_start=item["start_date"],
                folder=folder,
                price_exists=price_exists,
                valuation_exists=valuation_exists,
                price_rows=price_rows,
                valuation_rows=valuation_rows,
                price_has_date=price_has_date,
                valuation_has_date=valuation_has_date,
                price_row_match_valuation=(price_rows == valuation_rows),
                valuation_first_date=valuation_first_date,
                valuation_last_date=valuation_last_date,
                price_header=",".join(price_header),
                valuation_header=",".join(valuation_header),
                status=status_from_row(
                    price_exists=price_exists,
                    valuation_exists=valuation_exists,
                    price_has_date=price_has_date,
                    valuation_has_date=valuation_has_date,
                ),
            )
        )
    return output


def write_csv(rows: list[CoverageRow]) -> None:
    fieldnames = list(CoverageRow.__dataclass_fields__.keys())
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_md(rows: list[CoverageRow]) -> None:
    total = len(rows)
    price_exists_all = sum(1 for row in rows if row.price_exists)
    valuation_exists_all = sum(1 for row in rows if row.valuation_exists)
    price_has_date_count = sum(1 for row in rows if row.price_has_date)
    valuation_has_date_count = sum(1 for row in rows if row.valuation_has_date)
    blocked_rows = [row for row in rows if row.status != "ready_local_base"]
    min_valuation_date = min(
        (row.valuation_first_date for row in rows if row.valuation_first_date),
        default="",
    )
    max_valuation_date = max(
        (row.valuation_last_date for row in rows if row.valuation_last_date),
        default="",
    )

    lines = [
        "# Momentum V1 Local Coverage Check",
        "",
        "## Scope",
        "",
        "- Universe: `phase_1_fundamental/raw_downloads/all_banks/bank_universe.csv`",
        "- Expected research window: `2014-01-01` to `2026-05-01`",
        "- Backtest launch window to support first annual rebalance: `2021-05-31` onward",
        "",
        "## Summary",
        "",
        f"- Bank count: `{total}`",
        f"- `daily_price.csv` exists: `{price_exists_all}/{total}`",
        f"- `daily_valuation.csv` exists: `{valuation_exists_all}/{total}`",
        f"- Price files with a date field: `{price_has_date_count}/{total}`",
        f"- Valuation files with a date field: `{valuation_has_date_count}/{total}`",
        f"- Valuation date span observed locally: `{min_valuation_date}` to `{max_valuation_date}`",
        "",
        "## Conclusion",
        "",
        "- Local valuation layer is structurally usable for momentum support fields such as `turnover_ratio`, `market_cap`, `circulating_market_cap`, `pe_ratio`, and `pb_ratio`.",
        "- Local price layer is not yet directly usable for momentum because all `daily_price.csv` files are missing a transaction date column.",
        "- Because momentum formation relies on exact trading-date alignment, the price layer should be re-downloaded or repaired from an authoritative source such as JoinQuant before formal factor construction.",
        "",
        "## Blocking Items",
        "",
        f"- Non-ready rows: `{len(blocked_rows)}/{total}`",
        "- Current blocking status is driven by `blocked_price_missing_date` for the whole universe.",
        "- If we later need adjusted returns, the repaired price layer should also confirm whether it is pre-adjusted, post-adjusted, or raw.",
        "",
        "## Output",
        "",
        f"- Detailed coverage table: `{OUTPUT_CSV.name}`",
    ]

    with OUTPUT_MD.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    write_md(rows)
    print(f"wrote {OUTPUT_CSV}")
    print(f"wrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()
