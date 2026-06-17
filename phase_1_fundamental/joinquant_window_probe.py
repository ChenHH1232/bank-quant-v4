import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from jqdatasdk import (
    auth,
    balance,
    bank_indicator,
    cash_flow,
    finance,
    get_fundamentals,
    get_valuation,
    get_price,
    income,
    indicator,
    query,
)


DEFAULT_START = "2014-01-01"
DEFAULT_END = "2026-05-01"
DAILY_VALUATION_FIELDS = [
    "day",
    "code",
    "turnover_ratio",
    "turnover_ratio_f",
    "market_cap",
    "circulating_market_cap",
    "pe_ratio",
    "pb_ratio",
]
DAILY_VALUATION_FALLBACK_FIELDS = [
    "day",
    "code",
    "turnover_ratio",
    "market_cap",
    "circulating_market_cap",
    "pe_ratio",
    "pb_ratio",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe JoinQuant data availability for one stock across the full V4 window."
    )
    parser.add_argument("--username", default=os.getenv("JQ_USERNAME"))
    parser.add_argument("--password", default=os.getenv("JQ_PASSWORD"))
    parser.add_argument("--code", default="000001.XSHE", help="Security code, default is Ping An Bank.")
    parser.add_argument("--start-date", default=DEFAULT_START)
    parser.add_argument("--end-date", default=DEFAULT_END)
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "probe_outputs"),
        help="Directory to save CSV and summary outputs.",
    )
    return parser


def year_range(start_date: str, end_date: str) -> list[int]:
    start_year = datetime.fromisoformat(start_date).year
    end_year = datetime.fromisoformat(end_date).year
    return list(range(start_year, end_year + 1))


def quarter_labels(start_date: str, end_date: str) -> list[str]:
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    labels: list[str] = []
    for year in range(start.year, end.year + 1):
        for quarter in range(1, 5):
            labels.append(f"{year}q{quarter}")
    return labels


def result_record(name: str, status: str, rows: int, detail: str = "") -> dict[str, object]:
    return {
        "dataset": name,
        "status": status,
        "rows": rows,
        "detail": detail,
    }


def safe_save(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def fetch_daily_price(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = get_price(
        code,
        start_date=start_date,
        end_date=end_date,
        frequency="daily",
        fields=["open", "close", "high", "low", "volume", "money"],
        panel=False,
        fill_paused=False,
    )
    return pd.DataFrame() if df is None else df.reset_index(drop=True)


def fetch_daily_valuation(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    try:
        df = get_valuation(
            code,
            start_date=start_date,
            end_date=end_date,
            fields=DAILY_VALUATION_FIELDS,
        )
        result = pd.DataFrame() if df is None else df.reset_index(drop=True)
        if not result.empty:
            result["field_set"] = ",".join(DAILY_VALUATION_FIELDS)
        return result
    except Exception as first_exc:
        if "turnover_ratio_f" not in repr(first_exc):
            raise
        df = get_valuation(
            code,
            start_date=start_date,
            end_date=end_date,
            fields=DAILY_VALUATION_FALLBACK_FIELDS,
        )
        result = pd.DataFrame() if df is None else df.reset_index(drop=True)
        if not result.empty:
            result["field_set"] = ",".join(DAILY_VALUATION_FALLBACK_FIELDS)
        return result


def fetch_annual_table(table, code: str, years: list[int]) -> tuple[pd.DataFrame, list[int]]:
    frames: list[pd.DataFrame] = []
    missing_years: list[int] = []
    for year in years:
        try:
            q = query(table).filter(table.code == code)
            df = get_fundamentals(q, statDate=str(year))
            if df is None or df.empty:
                missing_years.append(year)
                continue
            df = df.copy()
            df["requested_year"] = year
            frames.append(df)
        except Exception:
            missing_years.append(year)
    if frames:
        return pd.concat(frames, ignore_index=True), missing_years
    return pd.DataFrame(), missing_years


def fetch_quarterly_table(table, code: str, quarter_keys: list[str]) -> tuple[pd.DataFrame, list[str]]:
    frames: list[pd.DataFrame] = []
    missing_keys: list[str] = []
    for key in quarter_keys:
        try:
            q = query(table).filter(table.code == code)
            df = get_fundamentals(q, statDate=key)
            if df is None or df.empty:
                missing_keys.append(key)
                continue
            df = df.copy()
            df["requested_period"] = key
            frames.append(df)
        except Exception:
            missing_keys.append(key)
    if frames:
        return pd.concat(frames, ignore_index=True), missing_keys
    return pd.DataFrame(), missing_keys


def fetch_finance_table(table, code: str, start_date: str, end_date: str) -> pd.DataFrame:
    q = query(table).filter(
        table.code == code,
        table.report_date >= start_date,
        table.report_date <= end_date,
    )
    df = finance.run_query(q)
    return pd.DataFrame() if df is None else df


def filter_finance_current_period(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "report_type" not in df.columns:
        return df
    # report_type=0 is the current reporting period row;
    # report_type=1 is the comparative previous-period row bundled in the same report.
    return df[df["report_type"] == 0].copy()


def main() -> None:
    args = build_parser().parse_args()
    if not args.username or not args.password:
        raise RuntimeError("Missing JoinQuant credentials. Pass --username/--password or set JQ_USERNAME/JQ_PASSWORD.")

    auth(args.username, args.password)

    output_dir = Path(args.output_dir) / args.code.replace(".", "_")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: list[dict[str, object]] = []
    years = year_range(args.start_date, args.end_date)
    quarter_keys = quarter_labels(args.start_date, args.end_date)

    # Daily price layer for later y construction.
    try:
        daily_df = fetch_daily_price(args.code, args.start_date, args.end_date)
        if daily_df.empty:
            summary.append(result_record("daily_price", "DATA_NOT_FOUND", 0, "No daily price rows returned."))
        else:
            safe_save(daily_df, output_dir / "daily_price.csv")
            summary.append(result_record("daily_price", "OK", len(daily_df), "Saved daily price window."))
    except Exception as exc:
        summary.append(result_record("daily_price", "DATA_NOT_FOUND", 0, repr(exc)))

    # Daily valuation / liquidity-support layer for later market-cap and liquidity screens.
    try:
        valuation_df = fetch_daily_valuation(args.code, args.start_date, args.end_date)
        if valuation_df.empty:
            summary.append(
                result_record(
                    "daily_valuation",
                    "DATA_NOT_FOUND",
                    0,
                    "No daily valuation rows returned.",
                )
            )
        else:
            safe_save(valuation_df, output_dir / "daily_valuation.csv")
            summary.append(
                result_record(
                    "daily_valuation",
                    "OK",
                    len(valuation_df),
                    "Saved daily valuation / market-cap window.",
                )
            )
    except Exception as exc:
        summary.append(result_record("daily_valuation", "DATA_NOT_FOUND", 0, repr(exc)))

    quarterly_tables = {
        "balance": balance,
        "income": income,
        "cash_flow": cash_flow,
        "indicator": indicator,
    }
    for name, table in quarterly_tables.items():
        df, missing_keys = fetch_quarterly_table(table, args.code, quarter_keys)
        if df.empty:
            summary.append(
                result_record(
                    name,
                    "DATA_NOT_FOUND",
                    0,
                    f"No rows returned. missing_periods={missing_keys}",
                )
            )
            continue
        safe_save(df, output_dir / f"{name}.csv")
        summary.append(
            result_record(
                name,
                "OK_WITH_GAPS" if missing_keys else "OK",
                len(df),
                f"missing_periods={missing_keys}" if missing_keys else "",
            )
        )

    annual_tables = {
        "bank_indicator": bank_indicator,
    }
    for name, table in annual_tables.items():
        df, missing_years = fetch_annual_table(table, args.code, years)
        if df.empty:
            summary.append(
                result_record(
                    name,
                    "DATA_NOT_FOUND",
                    0,
                    f"No rows returned. missing_years={missing_years}",
                )
            )
            continue
        safe_save(df, output_dir / f"{name}.csv")
        summary.append(
            result_record(
                name,
                "OK_WITH_GAPS" if missing_years else "OK",
                len(df),
                f"missing_years={missing_years}" if missing_years else "",
            )
        )

    finance_tables = {
        "finance_income_statement": finance.FINANCE_INCOME_STATEMENT,
        "finance_cashflow_statement": finance.FINANCE_CASHFLOW_STATEMENT,
        "finance_balance_sheet_parent": finance.FINANCE_BALANCE_SHEET_PARENT,
    }
    for name, table in finance_tables.items():
        try:
            df = fetch_finance_table(table, args.code, args.start_date, args.end_date)
            if df.empty:
                summary.append(result_record(name, "DATA_NOT_FOUND", 0, "No rows returned in window."))
                continue
            safe_save(df, output_dir / f"{name}_raw.csv")
            filtered_df = filter_finance_current_period(df)
            safe_save(filtered_df, output_dir / f"{name}_current_only.csv")
            detail = f"raw_rows={len(df)}, current_only_rows={len(filtered_df)}"
            if "report_type" in df.columns:
                counts = df["report_type"].value_counts(dropna=False).to_dict()
                detail += f", report_type_counts={counts}"
            summary.append(result_record(name, "OK", len(filtered_df), detail))
        except Exception as exc:
            summary.append(result_record(name, "DATA_NOT_FOUND", 0, repr(exc)))

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
