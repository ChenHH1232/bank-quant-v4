import argparse
import os
from pathlib import Path

import pandas as pd
from jqdatasdk import auth, bank_indicator, balance, cash_flow, get_fundamentals, income, indicator, query


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe JoinQuant annual fundamentals for a single stock and year."
    )
    parser.add_argument("--username", default=os.getenv("JQ_USERNAME"))
    parser.add_argument("--password", default=os.getenv("JQ_PASSWORD"))
    parser.add_argument("--code", default="000001.XSHE", help="Security code, default is Ping An Bank.")
    parser.add_argument("--year", default="2020", help="Annual statDate, e.g. 2020.")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "probe_outputs"),
        help="Directory to save CSV probe results.",
    )
    return parser


def fetch_one(table, code: str, year: str) -> pd.DataFrame:
    q = query(table).filter(table.code == code)
    return get_fundamentals(q, statDate=year)


def main() -> None:
    args = build_parser().parse_args()
    if not args.username or not args.password:
        raise RuntimeError("Missing JoinQuant credentials. Pass --username/--password or set JQ_USERNAME/JQ_PASSWORD.")

    auth(args.username, args.password)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tables = {
        "balance": balance,
        "income": income,
        "cash_flow": cash_flow,
        "indicator": indicator,
        "bank_indicator": bank_indicator,
    }

    for name, table in tables.items():
        df = fetch_one(table, args.code, args.year)
        csv_path = output_dir / f"{args.code}_{args.year}_{name}.csv"
        if df is None:
            print(f"{name}: None")
            continue
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"{name}: shape={df.shape} saved={csv_path}")


if __name__ == "__main__":
    main()
