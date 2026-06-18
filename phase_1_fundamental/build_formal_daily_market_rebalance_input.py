import csv
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
VALID_SEGMENTS_PATH = SCRIPT_DIR / "quarterly_valid_data_segments.csv"
RAW_DOWNLOAD_ROOT = SCRIPT_DIR / "raw_downloads" / "all_banks"
OUTPUT_PATH = SCRIPT_DIR / "daily_market_rebalance_input.csv"
SUMMARY_PATH = SCRIPT_DIR / "daily_market_rebalance_input.md"

LIQUIDITY_LOOKBACK_DAYS = 20


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value or value == "open":
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def folder_name_from_code(code: str) -> str:
    return code.replace(".", "_")


def build_global_rebalance_calendar(path: Path) -> list[dict[str, str]]:
    by_quarter: dict[str, list[date]] = defaultdict(list)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["effective_data_flag"] != "1":
                continue
            quarter_key = (row.get("quarter_key") or "").strip()
            effective_from_date = parse_date(row.get("effective_from_date", ""))
            if not quarter_key or effective_from_date is None:
                continue
            # The global rebalance date must be a date when every included stock
            # is already inside its valid-data window. Using the raw reference
            # date would exclude the latest reporter because its effective window
            # starts on the next day.
            by_quarter[quarter_key].append(effective_from_date)

    rows: list[dict[str, str]] = []
    for quarter_key in sorted(by_quarter):
        global_rebalance_date = max(by_quarter[quarter_key])
        rows.append(
            {
                "quarter_key": quarter_key,
                "global_rebalance_date": global_rebalance_date.isoformat(),
            }
        )
    return rows


def load_valid_segment_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def valid_on_global_rebalance(row: dict[str, str], global_rebalance_date: date) -> bool:
    if row["effective_data_flag"] != "1":
        return False
    start_date = parse_date(row.get("effective_from_date", ""))
    end_date = parse_date(row.get("effective_until_date", ""))
    if start_date is None:
        return False
    if global_rebalance_date < start_date:
        return False
    if end_date is not None and global_rebalance_date > end_date:
        return False
    return True


def load_daily_inputs_for_code(code: str) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    code_dir = RAW_DOWNLOAD_ROOT / folder_name_from_code(code)
    valuation_path = code_dir / "daily_valuation.csv"
    price_path = code_dir / "daily_price.csv"
    if not valuation_path.exists() or not price_path.exists():
        return None

    valuation_df = pd.read_csv(valuation_path, encoding="utf-8-sig")
    price_df = pd.read_csv(price_path, encoding="utf-8-sig")

    if "day" not in valuation_df.columns:
        return None

    valuation_df["day"] = pd.to_datetime(valuation_df["day"]).dt.date
    if "money" not in price_df.columns:
        return None

    if "time" in price_df.columns:
        price_df["day"] = pd.to_datetime(price_df["time"]).dt.date
    elif "day" in price_df.columns:
        price_df["day"] = pd.to_datetime(price_df["day"]).dt.date
    else:
        price_df = price_df.copy()
        price_df["day"] = valuation_df["day"][: len(price_df)]

    return valuation_df, price_df


def build_snapshot_row(
    code: str,
    quarter_key: str,
    rebalance_date: date,
    valuation_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> dict[str, str] | None:
    valuation_match = valuation_df[valuation_df["day"] == rebalance_date]
    actual_rebalance_date = rebalance_date
    if valuation_match.empty:
        future_matches = valuation_df[valuation_df["day"] >= rebalance_date].sort_values("day")
        if future_matches.empty:
            return None
        valuation_match = future_matches.head(1)
        actual_rebalance_date = valuation_match.iloc[-1]["day"]

    price_window = price_df[price_df["day"] < actual_rebalance_date].sort_values("day").tail(LIQUIDITY_LOOKBACK_DAYS)
    if price_window.empty:
        return None

    valuation_row = valuation_match.iloc[-1]
    avg_traded_amount = float(price_window["money"].mean())
    avg_traded_volume = float(price_window["volume"].mean()) if "volume" in price_window.columns else 0.0

    return {
        "rebalance_date": actual_rebalance_date.isoformat(),
        "quarter_key": quarter_key,
        "code": code,
        "avg_traded_amount_lookback": f"{avg_traded_amount:.6f}",
        "avg_traded_volume_lookback": f"{avg_traded_volume:.6f}",
        "market_cap": str(valuation_row.get("market_cap", "")),
        "circulating_market_cap": str(valuation_row.get("circulating_market_cap", "")),
        "turnover_ratio": str(valuation_row.get("turnover_ratio", "")),
    }


def main() -> None:
    calendar_rows = build_global_rebalance_calendar(VALID_SEGMENTS_PATH)
    valid_rows = load_valid_segment_rows(VALID_SEGMENTS_PATH)
    by_quarter: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in valid_rows:
        by_quarter[row["quarter_key"]].append(row)

    loaded_inputs: dict[str, tuple[pd.DataFrame, pd.DataFrame] | None] = {}
    output_rows: list[dict[str, str]] = []

    for item in calendar_rows:
        quarter_key = item["quarter_key"]
        global_rebalance_date = parse_date(item["global_rebalance_date"])
        if global_rebalance_date is None:
            continue

        for row in by_quarter.get(quarter_key, []):
            code = row["code"]
            if not valid_on_global_rebalance(row, global_rebalance_date):
                continue
            if code not in loaded_inputs:
                loaded_inputs[code] = load_daily_inputs_for_code(code)
            pair = loaded_inputs[code]
            if pair is None:
                continue
            valuation_df, price_df = pair
            snapshot_row = build_snapshot_row(code, quarter_key, global_rebalance_date, valuation_df, price_df)
            if snapshot_row is not None:
                output_rows.append(snapshot_row)

    fieldnames = [
        "rebalance_date",
        "quarter_key",
        "code",
        "avg_traded_amount_lookback",
        "avg_traded_volume_lookback",
        "market_cap",
        "circulating_market_cap",
        "turnover_ratio",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    unique_rebalance_dates = sorted({row["rebalance_date"] for row in output_rows})
    lines = [
        "# Daily Market Rebalance Input",
        "",
        "Source:",
        "- built from JoinQuant raw downloads in `raw_downloads/all_banks`",
        "- one global rebalance date per quarter",
        "- liquidity uses pre-rebalance rolling average traded amount over the last 20 trading days",
        "- market cap uses the rebalance-date daily valuation snapshot",
        "",
        f"- Rebalance dates: `{len(unique_rebalance_dates)}`",
        f"- Snapshot rows: `{len(output_rows)}`",
        "",
        "Output:",
        f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"rebalance_dates={len(unique_rebalance_dates)}")
    print(f"rows={len(output_rows)}")
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
