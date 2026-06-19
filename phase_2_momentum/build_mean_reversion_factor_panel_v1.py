from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR / "momentum_factor_panel_v2.csv"
OUTPUT_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.md"

TRADING_DAYS_5D = 5
TRADING_DAYS_10D = 10
TRADING_DAYS_20D = 20
MIN_LISTING_TRADING_DAYS = 240


def build_panel() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["code", "date"]).reset_index(drop=True)

    out_frames: list[pd.DataFrame] = []
    for _, group in df.groupby("code", sort=False):
        one = group.copy()
        close = pd.to_numeric(one["close"], errors="coerce")
        high = pd.to_numeric(one["high"], errors="coerce")
        money = pd.to_numeric(one["money"], errors="coerce")
        turnover = pd.to_numeric(one["turnover_ratio"], errors="coerce")
        mcap = pd.to_numeric(one["market_cap"], errors="coerce")
        daily_ret = pd.to_numeric(one["daily_return_close"], errors="coerce")

        one["rev_5d"] = close.div(close.shift(TRADING_DAYS_5D)) - 1.0
        one["rev_10d"] = close.div(close.shift(TRADING_DAYS_10D)) - 1.0
        one["rev_20d"] = close.div(close.shift(TRADING_DAYS_20D)) - 1.0

        ma20 = close.rolling(TRADING_DAYS_20D, min_periods=TRADING_DAYS_20D).mean()
        one["close_to_ma20"] = close.div(ma20) - 1.0

        rolling_high20 = high.rolling(TRADING_DAYS_20D, min_periods=TRADING_DAYS_20D).max()
        one["intramonth_drawdown_20d"] = close.div(rolling_high20) - 1.0

        one["avg_money_20d"] = money.rolling(TRADING_DAYS_20D, min_periods=TRADING_DAYS_20D).mean()
        one["avg_turnover_20d"] = turnover.rolling(TRADING_DAYS_20D, min_periods=TRADING_DAYS_20D).mean()
        one["avg_mcap_20d"] = mcap.rolling(TRADING_DAYS_20D, min_periods=TRADING_DAYS_20D).mean()
        one["volatility_20d"] = daily_ret.rolling(TRADING_DAYS_20D, min_periods=TRADING_DAYS_20D).std(ddof=0)
        one["down_day_ratio_20d"] = (daily_ret < 0).astype(float).rolling(TRADING_DAYS_20D, min_periods=TRADING_DAYS_20D).mean()
        one["abnormal_volume_ratio"] = money.div(one["avg_money_20d"])

        one["price_history_5d_ready"] = one["rev_5d"].notna().astype(int)
        one["price_history_10d_ready"] = one["rev_10d"].notna().astype(int)
        one["price_history_20d_ready"] = one["rev_20d"].notna().astype(int)

        out_frames.append(one)

    out = pd.concat(out_frames, ignore_index=True)
    out = out.sort_values(["date", "code"]).reset_index(drop=True)

    out["excess_rev_5d"] = out.groupby("date")["rev_5d"].transform(lambda s: s - s.median())
    out["excess_rev_10d"] = out.groupby("date")["rev_10d"].transform(lambda s: s - s.median())

    listed_trading_days = pd.to_numeric(out["listed_trading_days"], errors="coerce")
    out["mean_reversion_ready_v1"] = (
        out["rev_5d"].notna()
        & out["rev_10d"].notna()
        & out["rev_20d"].notna()
        & out["close_to_ma20"].notna()
        & out["avg_money_20d"].notna()
        & out["avg_turnover_20d"].notna()
        & out["avg_mcap_20d"].notna()
        & (listed_trading_days >= MIN_LISTING_TRADING_DAYS)
    ).astype(int)

    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    return out


def write_summary(df: pd.DataFrame) -> None:
    lines = [
        "# Mean Reversion Factor Panel V1",
        "",
        "Definition:",
        "- reuses `momentum_factor_panel_v2.csv` as the daily base panel",
        "- adds short-window reversal, oversold, and 20-day liquidity/size controls for mean-reversion research",
        "",
        f"- rows: `{len(df)}`",
        f"- stocks: `{df['code'].nunique()}`",
        f"- date span: `{df['date'].min()}` to `{df['date'].max()}`",
        f"- ready rows: `{int(df['mean_reversion_ready_v1'].sum())}`",
        "",
        "Non-null coverage:",
        f"- `rev_5d`: `{int(df['rev_5d'].notna().sum())}`",
        f"- `rev_10d`: `{int(df['rev_10d'].notna().sum())}`",
        f"- `rev_20d`: `{int(df['rev_20d'].notna().sum())}`",
        f"- `close_to_ma20`: `{int(df['close_to_ma20'].notna().sum())}`",
        f"- `intramonth_drawdown_20d`: `{int(df['intramonth_drawdown_20d'].notna().sum())}`",
        "",
        "Output:",
        f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
    ]
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    out = build_panel()
    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    write_summary(out)
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
