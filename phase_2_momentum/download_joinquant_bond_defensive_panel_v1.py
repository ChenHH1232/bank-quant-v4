from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
from jqdatasdk import auth, get_price, get_trade_days, get_query_count


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
TRAINING_PANEL_PATH = ROOT_DIR / "phase_1_fundamental" / "phase1_training_panel.csv"
OUTPUT_CSV = SCRIPT_DIR / "bond_defensive_panel_v1.csv"
OUTPUT_MD = SCRIPT_DIR / "bond_defensive_panel_v1.md"

DEFAULT_BOND_CODE = "511010.XSHG"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download JoinQuant bond ETF forward-return panel aligned to bank rebalance dates.")
    parser.add_argument("--username", default=os.getenv("JQ_USERNAME"), help="JoinQuant username")
    parser.add_argument("--password", default=os.getenv("JQ_PASSWORD"), help="JoinQuant password")
    parser.add_argument("--bond-code", default=DEFAULT_BOND_CODE, help="Bond ETF code, default 511010.XSHG")
    parser.add_argument(
        "--rebalance-end",
        default=None,
        help="Optional inclusive rebalance-date cutoff in YYYY-MM-DD format. Default keeps the full available panel.",
    )
    parser.add_argument(
        "--output-csv",
        default=str(OUTPUT_CSV),
        help="Output CSV path. Default writes to bond_defensive_panel_v1.csv",
    )
    parser.add_argument(
        "--output-md",
        default=str(OUTPUT_MD),
        help="Output markdown summary path. Default writes to bond_defensive_panel_v1.md",
    )
    return parser.parse_args()


def load_rebalance_windows(rebalance_end: str | None) -> pd.DataFrame:
    df = pd.read_csv(
        TRAINING_PANEL_PATH,
        usecols=["rebalance_date", "y_quarter_end_date"],
        encoding="utf-8-sig",
    )
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["y_quarter_end_date"] = pd.to_datetime(df["y_quarter_end_date"])
    df = df.dropna().drop_duplicates().sort_values("rebalance_date").copy()
    if rebalance_end:
        cutoff = pd.Timestamp(rebalance_end)
        df = df[df["rebalance_date"] <= cutoff].copy()
    return df.reset_index(drop=True)


def mean_daily_close_return(price_df: pd.DataFrame) -> float | None:
    if price_df is None or len(price_df) < 2:
        return None
    close_returns = pd.to_numeric(price_df["close"], errors="coerce").pct_change().dropna()
    if close_returns.empty:
        return None
    return float(close_returns.mean())


def build_panel(bond_code: str, windows_df: pd.DataFrame) -> pd.DataFrame:
    if windows_df.empty:
        return pd.DataFrame()

    start_date = windows_df["rebalance_date"].min().strftime("%Y-%m-%d")
    end_date = windows_df["y_quarter_end_date"].max().strftime("%Y-%m-%d")

    price_df = get_price(
        bond_code,
        start_date=start_date,
        end_date=end_date,
        frequency="daily",
        fields=["close"],
        skip_paused=False,
        fq=None,
        panel=False,
    )
    if price_df is None or len(price_df) == 0:
        return pd.DataFrame()

    raw = price_df.copy()
    if not isinstance(raw, pd.DataFrame):
        raw = pd.DataFrame(raw)
    if "time" not in raw.columns and "day" not in raw.columns and raw.index.name is not None:
        raw = raw.reset_index()
    elif "time" not in raw.columns and "day" not in raw.columns and isinstance(raw.index, pd.DatetimeIndex):
        raw = raw.reset_index().rename(columns={"index": "date"})
    if "time" in raw.columns:
        raw["date"] = pd.to_datetime(raw["time"])
    elif "day" in raw.columns:
        raw["date"] = pd.to_datetime(raw["day"])
    elif "date" in raw.columns:
        raw["date"] = pd.to_datetime(raw["date"])
    else:
        raise ValueError("Unknown get_price output columns: %s" % list(raw.columns))
    raw["close"] = pd.to_numeric(raw["close"], errors="coerce")
    raw = raw.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)

    rows: list[dict[str, object]] = []
    for row in windows_df.itertuples(index=False):
        rebalance_date = pd.Timestamp(row.rebalance_date)
        quarter_end_date = pd.Timestamp(row.y_quarter_end_date)
        trade_days = get_trade_days(start_date=rebalance_date, end_date=quarter_end_date)
        if trade_days is None or len(trade_days) < 2:
            continue

        one_window = raw[(raw["date"] >= rebalance_date) & (raw["date"] <= quarter_end_date)].copy()
        avg_daily_return = mean_daily_close_return(one_window)
        if avg_daily_return is None:
            continue

        start_close = float(one_window.iloc[0]["close"])
        end_close = float(one_window.iloc[-1]["close"])
        period_total_return = end_close / start_close - 1.0

        rows.append(
            {
                "rebalance_date": rebalance_date.strftime("%Y-%m-%d"),
                "quarter_end_date": quarter_end_date.strftime("%Y-%m-%d"),
                "bond_code": bond_code,
                "trade_day_count": int(len(trade_days)),
                "start_close": round(start_close, 8),
                "end_close": round(end_close, 8),
                "period_total_return": round(float(period_total_return), 10),
                # Assumption: align the bond sleeve with the bank panel's
                # `y_quarter_avg_daily_return_close` label via arithmetic mean
                # of daily close-to-close returns over the forward window.
                "bond_forward_return": round(float(avg_daily_return), 10),
            }
        )

    return pd.DataFrame(rows)


def write_summary(panel_df: pd.DataFrame, bond_code: str, output_csv: Path, output_md: Path) -> None:
    lines = [
        "# Bond Defensive Panel V1",
        "",
        f"- bond code: `{bond_code}`",
        f"- source: `JoinQuant get_price`",
        "- return assumption: arithmetic mean of daily close-to-close returns over each forward quarter window",
        f"- row count: `{len(panel_df)}`",
    ]
    if not panel_df.empty:
        lines.extend(
            [
                f"- first rebalance date: `{panel_df['rebalance_date'].min()}`",
                f"- last rebalance date: `{panel_df['rebalance_date'].max()}`",
                f"- mean bond forward return: `{panel_df['bond_forward_return'].mean():.10f}`",
                f"- min bond forward return: `{panel_df['bond_forward_return'].min():.10f}`",
                f"- max bond forward return: `{panel_df['bond_forward_return'].max():.10f}`",
                "",
                f"- [{output_csv.name}]({output_csv})",
            ]
        )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if not args.username or not args.password:
        raise RuntimeError("Missing JoinQuant credentials. Pass --username/--password or set JQ_USERNAME/JQ_PASSWORD.")

    output_csv = Path(args.output_csv).resolve()
    output_md = Path(args.output_md).resolve()
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    auth(args.username, args.password)
    windows_df = load_rebalance_windows(args.rebalance_end)
    panel_df = build_panel(args.bond_code, windows_df)
    if panel_df.empty:
        raise RuntimeError("Downloaded bond panel is empty.")
    panel_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_summary(panel_df, args.bond_code, output_csv, output_md)
    print("query_count=%s" % str(get_query_count()))
    print(output_csv)
    print(output_md)


if __name__ == "__main__":
    main()
