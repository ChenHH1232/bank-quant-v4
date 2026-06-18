from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
PRIMARY_POSITION_EXPORT_PATH = Path(r"C:\Users\Administrator\AppData\Local\Temp\position.csv")
PRIMARY_NAV_OUTPUT_PATH = ROOT / "joinquant_v4_primary_daily_nav_from_position_v1.csv"


def main() -> None:
    nav_df = load_nav_from_position_export(PRIMARY_POSITION_EXPORT_PATH, line_name="primary")
    nav_df.to_csv(PRIMARY_NAV_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"wrote {PRIMARY_NAV_OUTPUT_PATH}")
    print(f"rows={len(nav_df)} first_date={nav_df.iloc[0]['date']} last_date={nav_df.iloc[-1]['date']}")


def load_nav_from_position_export(path: Path, line_name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing position export: {path}")

    asset_by_date: dict[str, float] = {}
    with path.open("r", encoding="gbk", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) == 17:
                date_value = row[0].strip()
                total_asset_raw = row[15].strip()
            elif len(row) == 16:
                date_value = row[0].strip()
                total_asset_raw = row[14].strip()
            else:
                continue

            if not date_value or not total_asset_raw:
                continue
            asset_by_date.setdefault(date_value, float(total_asset_raw))

    if not asset_by_date:
        raise ValueError("no usable total asset values found in position export")

    dates = sorted(asset_by_date.keys())
    start_asset = asset_by_date[dates[0]]
    rows = []
    for date_value in dates:
        total_asset = asset_by_date[date_value]
        rows.append(
            {
                "date": date_value,
                "line": line_name,
                "total_asset": total_asset,
                "nav": total_asset / start_asset if start_asset else None,
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()
