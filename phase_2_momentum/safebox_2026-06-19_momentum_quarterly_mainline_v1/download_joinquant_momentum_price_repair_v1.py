from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from jqdatasdk import auth, get_price, get_query_count, get_trade_days


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DEFAULT_START = "2014-01-01"
DEFAULT_END = "2026-05-01"
DEFAULT_UNIVERSE_PATH = ROOT / "phase_1_fundamental" / "raw_downloads" / "all_banks" / "bank_universe.csv"
DEFAULT_OUTPUT_ROOT = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1"
DEFAULT_SUMMARY_PATH = DEFAULT_OUTPUT_ROOT / "run_summary.json"
DEFAULT_TRADE_CALENDAR_PATH = DEFAULT_OUTPUT_ROOT / "trade_calendar.csv"
DEFAULT_MANIFEST_PATH = DEFAULT_OUTPUT_ROOT / "manifest.json"

PRICE_FIELDS = ["open", "close", "high", "low", "volume", "money"]


@dataclass
class DownloadResult:
    code: str
    listed_start: str
    effective_start: str
    end_date: str
    rows: int
    first_date: str
    last_date: str
    status: str
    detail: str
    output_file: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download JoinQuant daily price data with explicit date column for the V4 momentum branch."
    )
    parser.add_argument("--username", default=os.getenv("JQ_USERNAME"))
    parser.add_argument("--password", default=os.getenv("JQ_PASSWORD"))
    parser.add_argument("--start-date", default=DEFAULT_START)
    parser.add_argument("--end-date", default=DEFAULT_END)
    parser.add_argument("--universe-path", default=str(DEFAULT_UNIVERSE_PATH))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--limit", type=int, default=0, help="Optional test limit. 0 means full universe.")
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument(
        "--fq",
        default="pre",
        choices=["pre", "post", "none"],
        help="JoinQuant price adjustment mode. 'none' maps to fq=None.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip stock files that already exist in the output directory.",
    )
    return parser


def normalize_fq(value: str) -> str | None:
    return None if value == "none" else value


def load_universe(path: Path, limit: int) -> list[dict[str, str]]:
    df = pd.read_csv(path, dtype=str)
    records = df.to_dict("records")
    if limit > 0:
        return records[:limit]
    return records


def effective_start(global_start: str, listed_start: str) -> str:
    return max(global_start, listed_start)


def ensure_date_column(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "code"] + PRICE_FIELDS)

    out = df.copy()
    index_name = out.index.name or "date"
    out = out.reset_index()
    if index_name != "date":
        out = out.rename(columns={index_name: "date"})
    if "date" not in out.columns:
        first_col = out.columns[0]
        out = out.rename(columns={first_col: "date"})
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    return out


def fetch_one_price(code: str, start_date: str, end_date: str, fq: str | None) -> pd.DataFrame:
    df = get_price(
        code,
        start_date=start_date,
        end_date=end_date,
        frequency="daily",
        fields=PRICE_FIELDS,
        skip_paused=False,
        fq=fq,
        panel=False,
        fill_paused=False,
    )
    normalized = ensure_date_column(pd.DataFrame() if df is None else df)
    if normalized.empty:
        normalized["code"] = pd.Series(dtype=str)
        return normalized[["date", "code"] + PRICE_FIELDS]
    normalized["code"] = code
    return normalized[["date", "code"] + PRICE_FIELDS]


def fetch_trade_calendar(start_date: str, end_date: str) -> pd.DataFrame:
    days = get_trade_days(start_date=start_date, end_date=end_date)
    df = pd.DataFrame({"date": [pd.Timestamp(day).strftime("%Y-%m-%d") for day in days]})
    df["seq"] = range(1, len(df) + 1)
    return df


def safe_save(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def query_count_text() -> dict[str, object]:
    try:
        return get_query_count()
    except Exception as exc:
        return {"error": repr(exc)}


def write_manifest(path: Path, start_date: str, end_date: str, fq: str | None, universe_path: Path) -> None:
    payload = {
        "dataset": "momentum_price_repair_v1",
        "source": "JoinQuant get_price + get_trade_days",
        "start_date": start_date,
        "end_date": end_date,
        "price_fields": PRICE_FIELDS,
        "fq": fq,
        "universe_path": str(universe_path),
        "notes": [
            "This dataset is a non-destructive repaired price layer for momentum research.",
            "Files preserve explicit trading dates and do not overwrite legacy phase_1 daily_price.csv outputs.",
            "Trade calendar is saved separately for annual rebalance alignment and rolling-window construction.",
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = build_parser().parse_args()
    if not args.username or not args.password:
        raise RuntimeError("Missing JoinQuant credentials. Pass --username/--password or set JQ_USERNAME/JQ_PASSWORD.")

    universe_path = Path(args.universe_path)
    output_root = Path(args.output_root)
    summary_path = output_root / DEFAULT_SUMMARY_PATH.name
    trade_calendar_path = output_root / DEFAULT_TRADE_CALENDAR_PATH.name
    manifest_path = output_root / DEFAULT_MANIFEST_PATH.name
    fq = normalize_fq(args.fq)

    auth(args.username, args.password)

    universe = load_universe(universe_path, args.limit)
    trade_calendar = fetch_trade_calendar(args.start_date, args.end_date)
    safe_save(trade_calendar, trade_calendar_path)
    write_manifest(manifest_path, args.start_date, args.end_date, fq, universe_path)

    results: list[dict[str, object]] = []
    for idx, item in enumerate(universe, start=1):
        code = item["code"]
        listed_start = item["start_date"]
        start_date = effective_start(args.start_date, listed_start)
        bank_dir = output_root / code.replace(".", "_")
        output_file = bank_dir / "daily_price_with_date.csv"

        if args.skip_existing and output_file.exists():
            existing = pd.read_csv(output_file, dtype=str)
            results.append(
                DownloadResult(
                    code=code,
                    listed_start=listed_start,
                    effective_start=start_date,
                    end_date=args.end_date,
                    rows=len(existing),
                    first_date=str(existing["date"].iloc[0]) if not existing.empty else "",
                    last_date=str(existing["date"].iloc[-1]) if not existing.empty else "",
                    status="SKIPPED_EXISTING",
                    detail="File already exists and --skip-existing is enabled.",
                    output_file=str(output_file),
                ).__dict__
            )
            continue

        try:
            df = fetch_one_price(code, start_date, args.end_date, fq)
            safe_save(df, output_file)
            results.append(
                DownloadResult(
                    code=code,
                    listed_start=listed_start,
                    effective_start=start_date,
                    end_date=args.end_date,
                    rows=len(df),
                    first_date=str(df["date"].iloc[0]) if not df.empty else "",
                    last_date=str(df["date"].iloc[-1]) if not df.empty else "",
                    status="OK" if not df.empty else "DATA_NOT_FOUND",
                    detail="Saved repaired daily price with explicit date column.",
                    output_file=str(output_file),
                ).__dict__
            )
        except Exception as exc:
            results.append(
                DownloadResult(
                    code=code,
                    listed_start=listed_start,
                    effective_start=start_date,
                    end_date=args.end_date,
                    rows=0,
                    first_date="",
                    last_date="",
                    status="ERROR",
                    detail=repr(exc),
                    output_file=str(output_file),
                ).__dict__
            )

        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

        if idx % 5 == 0 or idx == len(universe):
            progress = {
                "completed": idx,
                "total": len(universe),
                "last_code": code,
                "query_count": query_count_text(),
            }
            print(json.dumps(progress, ensure_ascii=False))

    output_root.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {trade_calendar_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
