import csv
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
STANDARDIZED_ROOT = SCRIPT_DIR / "standardized_outputs"
WHITELIST_PATH = SCRIPT_DIR / "model_field_whitelist_v1.csv"
POOL_PATH = SCRIPT_DIR / "dynamic_rebalance_stock_pool.csv"
OUTPUT_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
SUMMARY_PATH = SCRIPT_DIR / "phase1_training_panel.md"
TRADABLE_OUTPUT_PATH = SCRIPT_DIR / "phase1_tradable_rebalance_samples.csv"
TRADABLE_SUMMARY_PATH = SCRIPT_DIR / "phase1_tradable_rebalance_samples.md"
RAW_DOWNLOAD_ROOT = SCRIPT_DIR / "raw_downloads" / "all_banks"


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value or value == "open":
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def folder_name_from_code(code: str) -> str:
    return code.replace(".", "_")


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_whitelist(path: Path) -> dict[str, list[str]]:
    families: dict[str, list[str]] = defaultdict(list)
    for row in load_csv_rows(path):
        families[row["statement_family"]].append(row["field_name"])
    return dict(families)


def build_quarter_lookup(rows: list[dict[str, str]], field_names: set[str]) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for row in rows:
        quarter_key = (row.get("quarter_key") or "").strip()
        field_name = (row.get("standard_field_name") or "").strip()
        value = (row.get("standard_value") or "").strip()
        if not quarter_key or field_name not in field_names or not value:
            continue
        lookup[(quarter_key, field_name)] = value
    return lookup


def build_annual_lookup(rows: list[dict[str, str]], field_names: set[str]) -> dict[str, list[tuple[int, date | None, str, str]]]:
    by_field: dict[str, list[tuple[int, date | None, str, str]]] = defaultdict(list)
    for row in rows:
        year_key = (row.get("year_key") or "").strip()
        field_name = (row.get("standard_field_name") or "").strip()
        value = (row.get("standard_value") or "").strip()
        pub_date = parse_date(row.get("pub_date", ""))
        if not year_key or field_name not in field_names or not value:
            continue
        by_field[field_name].append((int(year_key), pub_date, year_key, value))
    for field_name in by_field:
        by_field[field_name].sort(key=lambda item: (item[0], item[1] or date.min))
    return dict(by_field)


def select_latest_annual_value(
    annual_lookup: dict[str, list[tuple[int, date | None, str, str]]],
    field_name: str,
    rebalance_date: date | None,
) -> tuple[str, str] | None:
    if rebalance_date is None:
        return None
    candidates = annual_lookup.get(field_name, [])
    eligible = [item for item in candidates if item[1] is not None and item[1] <= rebalance_date]
    if not eligible:
        return None
    year_int, _, year_key, value = eligible[-1]
    return year_key, value


def load_family_rows(code: str, family: str) -> list[dict[str, str]]:
    path = STANDARDIZED_ROOT / folder_name_from_code(code) / f"{family}_standardized.csv"
    if not path.exists():
        return []
    return load_csv_rows(path)


def load_price_history(code: str) -> pd.DataFrame:
    code_dir = RAW_DOWNLOAD_ROOT / folder_name_from_code(code)
    price_path = code_dir / "daily_price.csv"
    valuation_path = code_dir / "daily_valuation.csv"
    if not price_path.exists() or not valuation_path.exists():
        return pd.DataFrame(columns=["day", "close"])

    price_df = pd.read_csv(price_path, encoding="utf-8-sig")
    valuation_df = pd.read_csv(valuation_path, encoding="utf-8-sig")
    if price_df.empty or valuation_df.empty or "close" not in price_df.columns or "day" not in valuation_df.columns:
        return pd.DataFrame(columns=["day", "close"])

    valuation_df["day"] = pd.to_datetime(valuation_df["day"]).dt.date
    price_df = price_df.copy()

    if "time" in price_df.columns:
        price_df["day"] = pd.to_datetime(price_df["time"]).dt.date
    elif "day" in price_df.columns:
        price_df["day"] = pd.to_datetime(price_df["day"]).dt.date
    else:
        aligned_days = valuation_df["day"].tolist()[: len(price_df)]
        price_df = price_df.iloc[: len(aligned_days)].copy()
        price_df["day"] = aligned_days

    price_df["close"] = pd.to_numeric(price_df["close"], errors="coerce")
    price_df = price_df.dropna(subset=["day", "close"]).sort_values("day").drop_duplicates(subset=["day"], keep="last")
    return price_df[["day", "close"]].reset_index(drop=True)


def compute_average_daily_return(price_df: pd.DataFrame, start_date: date | None, end_date: date | None) -> str:
    if start_date is None or end_date is None or start_date >= end_date or price_df.empty:
        return ""

    window = price_df[(price_df["day"] > start_date) & (price_df["day"] <= end_date)].copy()
    if window.empty:
        return ""

    window["daily_return"] = window["close"].pct_change()
    daily_returns = window["daily_return"].dropna()
    if daily_returns.empty:
        return ""
    return f"{float(daily_returns.mean()):.10f}"


def build_horizon_maps(pool_rows: list[dict[str, str]]) -> tuple[dict[str, str], dict[str, str]]:
    ordered_dates = sorted({(row.get("rebalance_date") or "").strip() for row in pool_rows if row.get("rebalance_date")})
    next_quarter_map: dict[str, str] = {}
    next_year_map: dict[str, str] = {}
    for index, rebalance_date in enumerate(ordered_dates):
        if index + 1 < len(ordered_dates):
            next_quarter_map[rebalance_date] = ordered_dates[index + 1]
        if index + 4 < len(ordered_dates):
            next_year_map[rebalance_date] = ordered_dates[index + 4]
    return next_quarter_map, next_year_map


def build_panel_rows() -> tuple[list[dict[str, str]], dict[str, int]]:
    whitelist = load_whitelist(WHITELIST_PATH)
    pool_rows = load_csv_rows(POOL_PATH)
    codes = sorted({row["code"] for row in pool_rows})
    next_quarter_map, next_year_map = build_horizon_maps(pool_rows)

    code_cache: dict[str, dict[str, object]] = {}
    price_cache: dict[str, pd.DataFrame] = {}
    for code in codes:
        family_cache: dict[str, object] = {}
        for family, fields in whitelist.items():
            rows = load_family_rows(code, family)
            if family == "bank_indicator":
                family_cache[family] = build_annual_lookup(rows, set(fields))
            else:
                family_cache[family] = build_quarter_lookup(rows, set(fields))
        code_cache[code] = family_cache
        price_cache[code] = load_price_history(code)

    panel_rows: list[dict[str, str]] = []
    missing_counter: dict[str, int] = defaultdict(int)

    ordered_fields: list[str] = []
    for family, fields in whitelist.items():
        for field in fields:
            ordered_fields.append(f"{family}__{field}")

    for pool_row in pool_rows:
        code = pool_row["code"]
        rebalance_date = parse_date(pool_row.get("rebalance_date", ""))
        next_quarter_end = parse_date(next_quarter_map.get(pool_row.get("rebalance_date", ""), ""))
        next_year_end = parse_date(next_year_map.get(pool_row.get("rebalance_date", ""), ""))
        active_quarter_key = (pool_row.get("active_quarter_key") or "").strip()

        output_row = {
            "rebalance_date": pool_row.get("rebalance_date", ""),
            "quarter_key": pool_row.get("quarter_key", ""),
            "code": code,
            "active_quarter_key": active_quarter_key,
            "effective_data_flag": pool_row.get("effective_data_flag", ""),
            "rebalance_stock_pool_flag": pool_row.get("rebalance_stock_pool_flag", ""),
            "liquidity_top_80_flag": pool_row.get("liquidity_top_80_flag", ""),
            "market_cap_top_80_flag": pool_row.get("market_cap_top_80_flag", ""),
            "avg_traded_amount_lookback": pool_row.get("avg_traded_amount_lookback", ""),
            "avg_traded_volume_lookback": pool_row.get("avg_traded_volume_lookback", ""),
            "market_cap": pool_row.get("market_cap", ""),
            "circulating_market_cap": pool_row.get("circulating_market_cap", ""),
            "y_quarter_avg_daily_return_close": compute_average_daily_return(
                price_cache[code], rebalance_date, next_quarter_end
            ),
            "y_quarter_end_date": next_quarter_map.get(pool_row.get("rebalance_date", ""), ""),
            "y_year_avg_daily_return_close": compute_average_daily_return(
                price_cache[code], rebalance_date, next_year_end
            ),
            "y_year_end_date": next_year_map.get(pool_row.get("rebalance_date", ""), ""),
        }

        family_cache = code_cache[code]
        for family, fields in whitelist.items():
            if family == "bank_indicator":
                annual_lookup = family_cache[family]
                for field in fields:
                    key = f"{family}__{field}"
                    selected = select_latest_annual_value(annual_lookup, field, rebalance_date)
                    if selected is None:
                        output_row[key] = ""
                        output_row[f"{key}__source_year"] = ""
                        missing_counter[key] += 1
                    else:
                        source_year, value = selected
                        output_row[key] = value
                        output_row[f"{key}__source_year"] = source_year
            else:
                quarter_lookup = family_cache[family]
                for field in fields:
                    key = f"{family}__{field}"
                    value = quarter_lookup.get((active_quarter_key, field), "")
                    output_row[key] = value
                    if not value:
                        missing_counter[key] += 1

        panel_rows.append(output_row)

    return panel_rows, dict(missing_counter)


def write_panel(rows: list[dict[str, str]]) -> None:
    if not rows:
        OUTPUT_PATH.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]], missing_counter: dict[str, int]) -> None:
    total_rows = len(rows)
    in_pool_rows = sum(1 for row in rows if row["rebalance_stock_pool_flag"] == "1")
    unique_dates = len({row["rebalance_date"] for row in rows})
    quarter_y_ready = sum(1 for row in rows if row["y_quarter_avg_daily_return_close"])
    year_y_ready = sum(1 for row in rows if row["y_year_avg_daily_return_close"])
    lines = [
        "# Phase 1 Training Panel",
        "",
        "Definition:",
        "- one row per `rebalance_date x code`",
        "- already joined with:",
        "  - disclosed-data validity",
        "  - dynamic rebalance stock-pool flags",
        "  - whitelisted fundamental fields",
        "  - forward y labels based on close-to-close daily return averages",
        "",
        "Y definition:",
        "- `y_quarter_avg_daily_return_close`: mean daily close-to-close return from after current rebalance date to next rebalance date",
        "- `y_year_avg_daily_return_close`: mean daily close-to-close return from after current rebalance date to the rebalance date four quarters later",
        "- annual bank indicators are still aligned from the latest published annual snapshot available on the rebalance date",
        "",
        f"- Rows: `{total_rows}`",
        f"- Rebalance dates: `{unique_dates}`",
        f"- In-pool rows: `{in_pool_rows}`",
        f"- Quarter-y ready rows: `{quarter_y_ready}`",
        f"- Year-y ready rows: `{year_y_ready}`",
        "",
        "Largest remaining field-missing counts:",
    ]
    for field_name, count in sorted(missing_counter.items(), key=lambda item: (-item[1], item[0]))[:15]:
        lines.append(f"- `{field_name}`: `{count}`")
    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_tradable_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    tradable_rows: list[dict[str, str]] = []
    for row in rows:
        if row.get("rebalance_stock_pool_flag") != "1":
            continue
        tradable_rows.append(
            {
                "rebalance_date": row.get("rebalance_date", ""),
                "quarter_key": row.get("quarter_key", ""),
                "code": row.get("code", ""),
                "active_quarter_key": row.get("active_quarter_key", ""),
                "avg_traded_amount_lookback": row.get("avg_traded_amount_lookback", ""),
                "avg_traded_volume_lookback": row.get("avg_traded_volume_lookback", ""),
                "market_cap": row.get("market_cap", ""),
                "circulating_market_cap": row.get("circulating_market_cap", ""),
                "y_quarter_avg_daily_return_close": row.get("y_quarter_avg_daily_return_close", ""),
                "y_quarter_end_date": row.get("y_quarter_end_date", ""),
                "y_year_avg_daily_return_close": row.get("y_year_avg_daily_return_close", ""),
                "y_year_end_date": row.get("y_year_end_date", ""),
            }
        )
    return tradable_rows


def write_tradable_output(rows: list[dict[str, str]]) -> None:
    if not rows:
        TRADABLE_OUTPUT_PATH.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with TRADABLE_OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tradable_summary(rows: list[dict[str, str]]) -> None:
    quarter_y_ready = sum(1 for row in rows if row["y_quarter_avg_daily_return_close"])
    year_y_ready = sum(1 for row in rows if row["y_year_avg_daily_return_close"])
    unique_dates = len({row["rebalance_date"] for row in rows})
    lines = [
        "# Phase 1 Tradable Rebalance Samples",
        "",
        "Definition:",
        "- filtered from `phase1_training_panel.csv`",
        "- only rows with `rebalance_stock_pool_flag = 1`",
        "- intended as the direct per-rebalance tradable sample list",
        "",
        f"- Tradable rows: `{len(rows)}`",
        f"- Rebalance dates: `{unique_dates}`",
        f"- Quarter-y ready rows: `{quarter_y_ready}`",
        f"- Year-y ready rows: `{year_y_ready}`",
        "",
        "Output:",
        f"- [{TRADABLE_OUTPUT_PATH.name}]({TRADABLE_OUTPUT_PATH})",
    ]
    TRADABLE_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, missing_counter = build_panel_rows()
    write_panel(rows)
    write_summary(rows, missing_counter)
    tradable_rows = build_tradable_rows(rows)
    write_tradable_output(tradable_rows)
    write_tradable_summary(tradable_rows)
    print(f"rows={len(rows)}")
    print(f"in_pool_rows={sum(1 for row in rows if row['rebalance_stock_pool_flag'] == '1')}")
    print(f"quarter_y_ready={sum(1 for row in rows if row['y_quarter_avg_daily_return_close'])}")
    print(f"year_y_ready={sum(1 for row in rows if row['y_year_avg_daily_return_close'])}")
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)
    print(TRADABLE_OUTPUT_PATH)
    print(TRADABLE_SUMMARY_PATH)


if __name__ == "__main__":
    main()
