import argparse
import csv
import os
from pathlib import Path

import pandas as pd
from jqdatasdk import auth, bank_indicator, get_fundamentals, query


SCRIPT_DIR = Path(__file__).resolve().parent
TARGET_BANKS_PATH = SCRIPT_DIR / "bank_indicator_2013_backfill_banks.csv"
OUTPUT_DIR = SCRIPT_DIR / "backfill_2013_joinquant"
OUTPUT_CSV = OUTPUT_DIR / "joinquant_bank_indicator_2013_backfill.csv"
OUTPUT_MD = OUTPUT_DIR / "joinquant_bank_indicator_2013_backfill.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download the 2013 annual JoinQuant bank_indicator rows for the legacy bank subset."
    )
    parser.add_argument("--username", default=os.getenv("JQ_USERNAME"))
    parser.add_argument("--password", default=os.getenv("JQ_PASSWORD"))
    parser.add_argument("--year", default="2013")
    return parser


def load_target_banks(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def fetch_one(code: str, year: str) -> pd.DataFrame:
    q = query(bank_indicator).filter(bank_indicator.code == code)
    df = get_fundamentals(q, statDate=year)
    return pd.DataFrame() if df is None else df


def main() -> None:
    args = build_parser().parse_args()
    if not args.username or not args.password:
        raise RuntimeError("Missing JoinQuant credentials. Pass --username/--password or set JQ_USERNAME/JQ_PASSWORD.")

    auth(args.username, args.password)
    banks = load_target_banks(TARGET_BANKS_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, str]] = []

    for row in banks:
        code = row["code"]
        local_code = row["local_code"]
        df = fetch_one(code, args.year)
        if df.empty:
            summary_rows.append(
                {
                    "local_code": local_code,
                    "code": code,
                    "requested_year": args.year,
                    "status": "DATA_NOT_FOUND",
                    "rows": "0",
                }
            )
            continue

        df = df.copy()
        df["local_code"] = local_code
        df["requested_year"] = args.year
        frames.append(df)
        per_code_path = OUTPUT_DIR / f"{local_code}_{args.year}_bank_indicator.csv"
        df.to_csv(per_code_path, index=False, encoding="utf-8-sig")
        summary_rows.append(
            {
                "local_code": local_code,
                "code": code,
                "requested_year": args.year,
                "status": "OK",
                "rows": str(len(df)),
            }
        )

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame().to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    summary_df = pd.DataFrame(summary_rows)
    summary_csv = OUTPUT_DIR / "joinquant_bank_indicator_2013_backfill_status.csv"
    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")

    ok_count = int((summary_df["status"] == "OK").sum()) if not summary_df.empty else 0
    lines = [
        "# JoinQuant 2013 Bank Indicator Backfill",
        "",
        f"- Requested year: `{args.year}`",
        f"- Target banks: `{len(banks)}`",
        f"- Success count: `{ok_count}`",
        "",
        "Outputs:",
        f"- [joinquant_bank_indicator_2013_backfill.csv]({OUTPUT_CSV})",
        f"- [joinquant_bank_indicator_2013_backfill_status.csv]({summary_csv})",
    ]
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(OUTPUT_CSV)
    print(summary_csv)
    print(OUTPUT_MD)


if __name__ == "__main__":
    main()
