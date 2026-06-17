import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALID_SEGMENTS_PATH = SCRIPT_DIR / "quarterly_valid_data_segments.csv"
DAILY_MARKET_INPUT_PATH = SCRIPT_DIR / "daily_market_rebalance_input.csv"
OUTPUT_PATH = SCRIPT_DIR / "dynamic_rebalance_stock_pool.csv"
SUMMARY_PATH = SCRIPT_DIR / "dynamic_rebalance_stock_pool.md"

LIQUIDITY_PERCENTILE = 0.80
MARKET_CAP_PERCENTILE = 0.80


@dataclass
class SegmentWindow:
    code: str
    quarter_key: str
    effective_from_date: date
    effective_until_date: date | None


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value or value == "open":
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def load_valid_segment_windows(path: Path) -> list[SegmentWindow]:
    rows: list[SegmentWindow] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["effective_data_flag"] != "1":
                continue
            start_date = parse_date(row["effective_from_date"])
            if start_date is None:
                continue
            rows.append(
                SegmentWindow(
                    code=row["code"],
                    quarter_key=row["quarter_key"],
                    effective_from_date=start_date,
                    effective_until_date=parse_date(row["effective_until_date"]),
                )
            )
    return rows


def active_segment_for_date(
    windows_by_code: dict[str, list[SegmentWindow]],
    code: str,
    rebalance_date: date,
) -> SegmentWindow | None:
    for window in windows_by_code.get(code, []):
        starts_ok = rebalance_date >= window.effective_from_date
        ends_ok = window.effective_until_date is None or rebalance_date <= window.effective_until_date
        if starts_ok and ends_ok:
            return window
    return None


def percentile_cutoff_size(count: int, keep_ratio: float) -> int:
    if count <= 0:
        return 0
    keep_count = int(count * keep_ratio)
    if keep_count * 1.0 < count * keep_ratio:
        keep_count += 1
    return max(1, keep_count)


def write_template_if_missing(path: Path) -> None:
    if path.exists():
        return
    fieldnames = [
        "rebalance_date",
        "quarter_key",
        "code",
        "avg_traded_amount_lookback",
        "market_cap",
        "circulating_market_cap",
        "avg_traded_volume_lookback",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()


def load_daily_market_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_pool_rows() -> list[dict[str, str]]:
    write_template_if_missing(DAILY_MARKET_INPUT_PATH)
    if not DAILY_MARKET_INPUT_PATH.exists():
        return []

    windows = load_valid_segment_windows(VALID_SEGMENTS_PATH)
    windows_by_code: dict[str, list[SegmentWindow]] = defaultdict(list)
    for window in windows:
        windows_by_code[window.code].append(window)

    for code in windows_by_code:
        windows_by_code[code].sort(key=lambda item: item.effective_from_date)

    daily_rows = load_daily_market_rows(DAILY_MARKET_INPUT_PATH)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in daily_rows:
        rebalance_date = (row.get("rebalance_date") or "").strip()
        code = (row.get("code") or "").strip()
        if not rebalance_date or not code:
            continue
        grouped[rebalance_date].append(row)

    output_rows: list[dict[str, str]] = []
    for rebalance_date_text in sorted(grouped):
        rebalance_date = parse_date(rebalance_date_text)
        if rebalance_date is None:
            continue
        cross_section: list[dict[str, str]] = []
        for row in grouped[rebalance_date_text]:
            code = row["code"].strip()
            segment = active_segment_for_date(windows_by_code, code, rebalance_date)
            if segment is None:
                continue
            try:
                liquidity_value = float(row["avg_traded_amount_lookback"])
                market_cap_value = float(row["market_cap"])
            except (KeyError, ValueError):
                continue
            cross_section.append(
                {
                    "rebalance_date": rebalance_date_text,
                    "code": code,
                    "active_quarter_key": segment.quarter_key,
                    "avg_traded_amount_lookback": row["avg_traded_amount_lookback"],
                    "market_cap": row["market_cap"],
                    "circulating_market_cap": row.get("circulating_market_cap", ""),
                    "avg_traded_volume_lookback": row.get("avg_traded_volume_lookback", ""),
                    "_liquidity_value": liquidity_value,
                    "_market_cap_value": market_cap_value,
                }
            )

        liquidity_sorted = sorted(cross_section, key=lambda item: item["_liquidity_value"], reverse=True)
        market_cap_sorted = sorted(cross_section, key=lambda item: item["_market_cap_value"], reverse=True)
        liquidity_keep = percentile_cutoff_size(len(liquidity_sorted), LIQUIDITY_PERCENTILE)
        market_cap_keep = percentile_cutoff_size(len(market_cap_sorted), MARKET_CAP_PERCENTILE)
        liquidity_set = {item["code"] for item in liquidity_sorted[:liquidity_keep]}
        market_cap_set = {item["code"] for item in market_cap_sorted[:market_cap_keep]}

        for item in cross_section:
            item["effective_data_flag"] = "1"
            item["liquidity_top_80_flag"] = "1" if item["code"] in liquidity_set else "0"
            item["market_cap_top_80_flag"] = "1" if item["code"] in market_cap_set else "0"
            item["rebalance_stock_pool_flag"] = (
                "1"
                if item["code"] in liquidity_set and item["code"] in market_cap_set
                else "0"
            )
            output_rows.append(
                {
                    "rebalance_date": item["rebalance_date"],
                    "quarter_key": row.get("quarter_key", ""),
                    "code": item["code"],
                    "active_quarter_key": item["active_quarter_key"],
                    "effective_data_flag": item["effective_data_flag"],
                    "avg_traded_amount_lookback": item["avg_traded_amount_lookback"],
                    "market_cap": item["market_cap"],
                    "circulating_market_cap": item["circulating_market_cap"],
                    "avg_traded_volume_lookback": item["avg_traded_volume_lookback"],
                    "liquidity_top_80_flag": item["liquidity_top_80_flag"],
                    "market_cap_top_80_flag": item["market_cap_top_80_flag"],
                    "rebalance_stock_pool_flag": item["rebalance_stock_pool_flag"],
                }
            )
    return output_rows


def write_output(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "rebalance_date",
        "quarter_key",
        "code",
        "active_quarter_key",
        "effective_data_flag",
        "avg_traded_amount_lookback",
        "market_cap",
        "circulating_market_cap",
        "avg_traded_volume_lookback",
        "liquidity_top_80_flag",
        "market_cap_top_80_flag",
        "rebalance_stock_pool_flag",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]]) -> None:
    rebalance_dates = sorted({row["rebalance_date"] for row in rows})
    lines = [
        "# Dynamic Rebalance Stock Pool Template",
        "",
        "Rule:",
        "- The stock pool must be recomputed independently on each rebalance date.",
        "- A stock can enter, leave, and re-enter the pool across time.",
        "- Only stocks with `effective_data_flag = 1` are allowed into the ranking step.",
        "- The final pool on a rebalance date is the intersection of:",
        "  - top 80% by liquidity",
        "  - top 80% by market cap",
        "",
        "Files:",
        f"- input template: [{DAILY_MARKET_INPUT_PATH.name}]({DAILY_MARKET_INPUT_PATH})",
        f"- output template: [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
        "",
        f"- Rebalance dates currently populated from input: `{len(rebalance_dates)}`",
        f"- Output rows currently generated: `{len(rows)}`",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_pool_rows()
    write_output(rows)
    write_summary(rows)
    print(f"rows={len(rows)}")
    print(DAILY_MARKET_INPUT_PATH)
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
