from __future__ import annotations

from math import ceil
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
DAILY_PANEL_PATH = SCRIPT_DIR / "momentum_factor_panel_v2.csv"
TRADE_CALENDAR_PATH = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1" / "trade_calendar.csv"
OUTPUT_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
SUMMARY_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.md"

POOL_KEEP_RATIO = 0.60


def load_daily_panel() -> pd.DataFrame:
    df = pd.read_csv(DAILY_PANEL_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_monthly_calendar() -> pd.DataFrame:
    df = pd.read_csv(TRADE_CALENDAR_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["month_key"] = df["date"].dt.strftime("%Y-%m")
    out = df.groupby("month_key", as_index=False).first()[["month_key", "date"]].copy()
    out = out.rename(columns={"date": "rebalance_date"})
    return out.sort_values("rebalance_date").reset_index(drop=True)


def build_panel(daily_df: pd.DataFrame, calendar_df: pd.DataFrame) -> pd.DataFrame:
    sampled = daily_df.merge(calendar_df, left_on="date", right_on="rebalance_date", how="inner").copy()
    sampled = sampled.drop(columns=["date"]).sort_values(["code", "rebalance_date"]).reset_index(drop=True)
    sampled["next_rebalance_date"] = sampled.groupby("code")["rebalance_date"].shift(-1)
    sampled["next_rebalance_close"] = sampled.groupby("code")["close"].shift(-1)
    sampled["y_month_total_return_close"] = sampled["next_rebalance_close"].div(sampled["close"]) - 1.0

    out_rows: list[dict[str, object]] = []
    daily_groups = {code: grp.sort_values("date").copy() for code, grp in daily_df.groupby("code")}
    for row in sampled.itertuples(index=False):
        avg_daily_return = np.nan
        avg_money_20d = np.nan
        avg_market_cap_20d = np.nan

        history = daily_groups[row.code]
        trailing_window = history[history["date"] <= row.rebalance_date].tail(20)
        if not trailing_window.empty:
            money_values = pd.to_numeric(trailing_window["money"], errors="coerce").dropna()
            market_cap_values = pd.to_numeric(trailing_window["market_cap"], errors="coerce").dropna()
            if not money_values.empty:
                avg_money_20d = float(money_values.mean())
            if not market_cap_values.empty:
                avg_market_cap_20d = float(market_cap_values.mean())

        if pd.notna(row.next_rebalance_date):
            next_window = history[(history["date"] > row.rebalance_date) & (history["date"] <= row.next_rebalance_date)]
            if not next_window.empty:
                returns = pd.to_numeric(next_window["daily_return_close"], errors="coerce").dropna()
                if not returns.empty:
                    avg_daily_return = float(returns.mean())

        payload = row._asdict()
        payload["avg_money_20d_pre_rebalance"] = avg_money_20d
        payload["avg_market_cap_20d_pre_rebalance"] = avg_market_cap_20d
        payload["y_month_avg_daily_return_close"] = avg_daily_return
        out_rows.append(payload)

    out = pd.DataFrame(out_rows).sort_values(["rebalance_date", "code"]).reset_index(drop=True)
    out["monthly_momentum_ready_v2"] = (
        out["mom_3_1"].notna()
        & out["mom_6_1"].notna()
        & out["mom_12_1"].notna()
        & out["avg_money_20d_pre_rebalance"].notna()
        & out["avg_market_cap_20d_pre_rebalance"].notna()
        & (pd.to_numeric(out["listed_trading_days"], errors="coerce") >= 240)
    ).astype(int)

    liq_flags: list[int] = []
    mcap_flags: list[int] = []
    pool_flags: list[int] = []
    for _, group in out.groupby("rebalance_date", sort=False):
        ready_group = group["monthly_momentum_ready_v2"] == 1
        valid_liq = int((ready_group & group["avg_money_20d_pre_rebalance"].notna()).sum())
        valid_mcap = int((ready_group & group["avg_market_cap_20d_pre_rebalance"].notna()).sum())
        liq_keep = ceil(valid_liq * POOL_KEEP_RATIO) if valid_liq > 0 else 0
        mcap_keep = ceil(valid_mcap * POOL_KEEP_RATIO) if valid_mcap > 0 else 0

        liq_rank = group.loc[ready_group, "avg_money_20d_pre_rebalance"].rank(method="first", ascending=False)
        mcap_rank = group.loc[ready_group, "avg_market_cap_20d_pre_rebalance"].rank(method="first", ascending=False)

        liq_flag = pd.Series(index=group.index, data=0)
        mcap_flag = pd.Series(index=group.index, data=0)
        if liq_keep > 0:
            liq_flag.loc[liq_rank.index] = (liq_rank <= liq_keep).astype(int)
        if mcap_keep > 0:
            mcap_flag.loc[mcap_rank.index] = (mcap_rank <= mcap_keep).astype(int)

        pool_flag = ((liq_flag == 1) & (mcap_flag == 1) & ready_group).astype(int)
        liq_flags.extend(liq_flag.astype(int).tolist())
        mcap_flags.extend(mcap_flag.astype(int).tolist())
        pool_flags.extend(pool_flag.astype(int).tolist())

    out["liquidity_top_60_flag"] = liq_flags
    out["market_cap_top_60_flag"] = mcap_flags
    out["rebalance_stock_pool_flag_v2"] = pool_flags
    return out


def write_summary(df: pd.DataFrame) -> None:
    lines = [
        "# Momentum Monthly Rebalance Panel V2",
        "",
        "Definition:",
        "- monthly rebalance date = first actual trading day of each month",
        "- momentum layer keeps daily-derived bank signals but samples on the monthly calendar",
        "- monthly pool uses prior-20-trading-day average amount top 60% intersect average market-cap top 60%",
        "- v2 research fields focus on `mom_3_1`, `mom_6_1`, `mom_12_1` style monthly momentum",
        "",
        f"- rows: `{len(df)}`",
        f"- rebalance dates: `{df['rebalance_date'].nunique()}`",
        f"- ready rows: `{int(df['monthly_momentum_ready_v2'].sum())}`",
        f"- in-pool rows: `{int(df['rebalance_stock_pool_flag_v2'].sum())}`",
        "",
        "Output:",
        f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
    ]
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    daily_df = load_daily_panel()
    calendar_df = load_monthly_calendar()
    out = build_panel(daily_df, calendar_df)
    save_df = out.copy()
    for col in ["rebalance_date", "next_rebalance_date"]:
        save_df[col] = pd.to_datetime(save_df[col]).dt.strftime("%Y-%m-%d")
    save_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    write_summary(out)
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
