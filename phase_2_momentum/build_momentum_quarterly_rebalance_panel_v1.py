from __future__ import annotations

from math import ceil
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DAILY_PANEL_PATH = SCRIPT_DIR / "momentum_factor_panel_v1.csv"
PHASE1_PANEL_PATH = ROOT / "phase_1_fundamental" / "phase1_training_panel.csv"
OUTPUT_PATH = SCRIPT_DIR / "momentum_quarterly_rebalance_panel_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "momentum_quarterly_rebalance_panel_v1.md"


def load_daily_panel() -> pd.DataFrame:
    df = pd.read_csv(DAILY_PANEL_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_rebalance_calendar() -> pd.DataFrame:
    df = pd.read_csv(PHASE1_PANEL_PATH, encoding="utf-8-sig", usecols=["rebalance_date", "quarter_key"])
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    return df.drop_duplicates().sort_values("rebalance_date").reset_index(drop=True)


def build_panel(daily_df: pd.DataFrame, calendar_df: pd.DataFrame) -> pd.DataFrame:
    sampled = daily_df.merge(calendar_df, left_on="date", right_on="rebalance_date", how="inner").copy()
    sampled = sampled.drop(columns=["date"]).sort_values(["code", "rebalance_date"]).reset_index(drop=True)
    sampled["next_rebalance_date"] = sampled.groupby("code")["rebalance_date"].shift(-1)
    sampled["next_rebalance_close"] = sampled.groupby("code")["close"].shift(-1)
    sampled["y_quarter_total_return_close"] = sampled["next_rebalance_close"].div(sampled["close"]) - 1.0

    out_rows: list[dict[str, object]] = []
    daily_groups = {code: grp.sort_values("date").copy() for code, grp in daily_df.groupby("code")}
    for row in sampled.itertuples(index=False):
        avg_daily_return = np.nan
        avg_money_20d = np.nan
        avg_market_cap_20d = np.nan
        trailing_window = daily_groups[row.code][daily_groups[row.code]["date"] <= row.rebalance_date].tail(20)
        if not trailing_window.empty:
            money_values = pd.to_numeric(trailing_window["money"], errors="coerce").dropna()
            market_cap_values = pd.to_numeric(trailing_window["market_cap"], errors="coerce").dropna()
            if not money_values.empty:
                avg_money_20d = float(money_values.mean())
            if not market_cap_values.empty:
                avg_market_cap_20d = float(market_cap_values.mean())
        if pd.notna(row.next_rebalance_date):
            history = daily_groups[row.code]
            window = history[(history["date"] > row.rebalance_date) & (history["date"] <= row.next_rebalance_date)]
            if not window.empty:
                returns = pd.to_numeric(window["daily_return_close"], errors="coerce").dropna()
                if not returns.empty:
                    avg_daily_return = float(returns.mean())
        payload = row._asdict()
        payload["y_quarter_avg_daily_return_close"] = avg_daily_return
        payload["avg_money_20d_pre_rebalance"] = avg_money_20d
        payload["avg_market_cap_20d_pre_rebalance"] = avg_market_cap_20d
        out_rows.append(payload)

    out = pd.DataFrame(out_rows)
    out = out.sort_values(["rebalance_date", "code"]).reset_index(drop=True)

    liq_flags: list[int] = []
    mcap_flags: list[int] = []
    pool_flags: list[int] = []
    for _, group in out.groupby("rebalance_date", sort=False):
        valid_liq = group["avg_money_20d_pre_rebalance"].notna().sum()
        valid_mcap = group["avg_market_cap_20d_pre_rebalance"].notna().sum()
        liq_keep = ceil(valid_liq * 0.8) if valid_liq > 0 else 0
        mcap_keep = ceil(valid_mcap * 0.8) if valid_mcap > 0 else 0
        liq_rank = group["avg_money_20d_pre_rebalance"].rank(method="first", ascending=False, na_option="bottom")
        mcap_rank = group["avg_market_cap_20d_pre_rebalance"].rank(method="first", ascending=False, na_option="bottom")
        liq_flag = ((group["avg_money_20d_pre_rebalance"].notna()) & (liq_rank <= liq_keep)).astype(int)
        mcap_flag = ((group["avg_market_cap_20d_pre_rebalance"].notna()) & (mcap_rank <= mcap_keep)).astype(int)
        pool_flag = ((liq_flag == 1) & (mcap_flag == 1)).astype(int)
        liq_flags.extend(liq_flag.tolist())
        mcap_flags.extend(mcap_flag.tolist())
        pool_flags.extend(pool_flag.tolist())

    out["liquidity_top_80_flag"] = liq_flags
    out["market_cap_top_80_flag"] = mcap_flags
    out["rebalance_stock_pool_flag"] = pool_flags
    return out


def write_summary(df: pd.DataFrame) -> None:
    lines = [
        "# Momentum Quarterly Rebalance Panel V1",
        "",
        "Definition:",
        "- quarterly rebalance dates are inherited from the phase-1 fundamental panel",
        "- momentum signals stay daily-derived, but are sampled only on the shared rebalance calendar",
        "- tradable pool keeps the prior-20-trading-day amount and market-cap double-top-80% rule",
        "",
        f"- rows: `{len(df)}`",
        f"- rebalance dates: `{df['rebalance_date'].nunique()}`",
        f"- in-pool rows: `{int(df['rebalance_stock_pool_flag'].sum())}`",
        "",
        "Output:",
        f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
    ]
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    daily_df = load_daily_panel()
    calendar_df = load_rebalance_calendar()
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
