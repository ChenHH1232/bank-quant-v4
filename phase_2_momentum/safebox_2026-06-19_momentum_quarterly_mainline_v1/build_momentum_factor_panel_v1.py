from __future__ import annotations

from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
UNIVERSE_PATH = ROOT / "phase_1_fundamental" / "raw_downloads" / "all_banks" / "bank_universe.csv"
PRICE_ROOT = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1"
VALUATION_ROOT = ROOT / "phase_1_fundamental" / "raw_downloads" / "all_banks"
TRADE_CALENDAR_PATH = PRICE_ROOT / "trade_calendar.csv"

OUTPUT_PATH = SCRIPT_DIR / "momentum_factor_panel_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "momentum_factor_panel_v1.md"

TRADING_DAYS_1M = 20
TRADING_DAYS_3M = 60
TRADING_DAYS_6M = 120
TRADING_DAYS_12M = 240


def folder_name_from_code(code: str) -> str:
    return code.replace(".", "_")


def load_universe() -> pd.DataFrame:
    df = pd.read_csv(UNIVERSE_PATH, encoding="utf-8-sig", dtype=str)
    df["start_date"] = pd.to_datetime(df["start_date"])
    return df[["code", "display_name", "start_date", "end_date"]].copy()


def load_trade_calendar() -> pd.DataFrame:
    df = pd.read_csv(TRADE_CALENDAR_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df["trade_seq"] = pd.to_numeric(df["seq"], errors="coerce").astype("Int64")
    return df[["date", "trade_seq"]].copy()


def load_price_frame(code: str) -> pd.DataFrame:
    path = PRICE_ROOT / folder_name_from_code(code) / "daily_price_with_date.csv"
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    for column in ["open", "close", "high", "low", "volume", "money"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def load_valuation_frame(code: str) -> pd.DataFrame:
    path = VALUATION_ROOT / folder_name_from_code(code) / "daily_valuation.csv"
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["day"])
    keep = ["date", "turnover_ratio", "market_cap", "circulating_market_cap", "pe_ratio", "pb_ratio"]
    out = df[keep].copy()
    for column in keep[1:]:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    return out


def build_one_code_frame(code: str, display_name: str, listed_start: pd.Timestamp, trade_calendar: pd.DataFrame) -> pd.DataFrame:
    price_df = load_price_frame(code)
    valuation_df = load_valuation_frame(code)

    df = price_df.merge(valuation_df, on="date", how="left")
    df = df.merge(trade_calendar, on="date", how="left")
    df = df.sort_values("date").reset_index(drop=True)

    df["code"] = code
    df["display_name"] = display_name
    df["listed_start"] = listed_start.strftime("%Y-%m-%d")
    df["listed_days"] = (df["date"] - listed_start).dt.days
    df["listed_trading_days"] = range(1, len(df) + 1)

    close = df["close"]
    df["daily_return_close"] = close.pct_change()
    df["mom_1m"] = close.div(close.shift(TRADING_DAYS_1M)) - 1.0
    df["mom_3m"] = close.div(close.shift(TRADING_DAYS_3M)) - 1.0
    df["mom_6m"] = close.div(close.shift(TRADING_DAYS_6M)) - 1.0
    df["mom_12m"] = close.div(close.shift(TRADING_DAYS_12M)) - 1.0
    df["mom_12_1"] = close.shift(TRADING_DAYS_1M).div(close.shift(TRADING_DAYS_12M)) - 1.0
    df["mom_6_1"] = close.shift(TRADING_DAYS_1M).div(close.shift(TRADING_DAYS_6M)) - 1.0

    df["liq_money_1m"] = df["money"].rolling(TRADING_DAYS_1M, min_periods=TRADING_DAYS_1M).mean()
    df["liq_turnover_1m"] = (
        df["turnover_ratio"].rolling(TRADING_DAYS_1M, min_periods=TRADING_DAYS_1M).mean()
    )

    df["price_history_1m_ready"] = df["mom_1m"].notna().astype(int)
    df["price_history_3m_ready"] = df["mom_3m"].notna().astype(int)
    df["price_history_6m_ready"] = df["mom_6m"].notna().astype(int)
    df["price_history_12m_ready"] = df["mom_12m"].notna().astype(int)
    df["price_history_12_1_ready"] = df["mom_12_1"].notna().astype(int)
    df["liquidity_1m_ready"] = (df["liq_money_1m"].notna() & df["liq_turnover_1m"].notna()).astype(int)
    df["momentum_core_ready_v1"] = (
        df["mom_1m"].notna()
        & df["mom_3m"].notna()
        & df["mom_6m"].notna()
        & df["mom_12m"].notna()
        & df["mom_12_1"].notna()
        & df["mom_6_1"].notna()
        & df["liq_money_1m"].notna()
        & df["liq_turnover_1m"].notna()
    ).astype(int)

    ordered_columns = [
        "date",
        "trade_seq",
        "code",
        "display_name",
        "listed_start",
        "listed_days",
        "listed_trading_days",
        "open",
        "close",
        "high",
        "low",
        "volume",
        "money",
        "turnover_ratio",
        "market_cap",
        "circulating_market_cap",
        "pe_ratio",
        "pb_ratio",
        "daily_return_close",
        "mom_1m",
        "mom_3m",
        "mom_6m",
        "mom_12m",
        "mom_12_1",
        "mom_6_1",
        "liq_money_1m",
        "liq_turnover_1m",
        "price_history_1m_ready",
        "price_history_3m_ready",
        "price_history_6m_ready",
        "price_history_12m_ready",
        "price_history_12_1_ready",
        "liquidity_1m_ready",
        "momentum_core_ready_v1",
    ]
    return df[ordered_columns].copy()


def build_panel() -> pd.DataFrame:
    universe_df = load_universe()
    trade_calendar = load_trade_calendar()

    frames: list[pd.DataFrame] = []
    for row in universe_df.itertuples(index=False):
        frames.append(
            build_one_code_frame(
                code=row.code,
                display_name=row.display_name,
                listed_start=row.start_date,
                trade_calendar=trade_calendar,
            )
        )

    out = pd.concat(frames, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    return out.sort_values(["date", "code"]).reset_index(drop=True)


def write_summary(df: pd.DataFrame) -> None:
    date_min = df["date"].min()
    date_max = df["date"].max()
    code_count = df["code"].nunique()
    total_rows = len(df)
    ready_rows = int(df["momentum_core_ready_v1"].sum())
    may_ready_rows = int(
        df[(pd.to_datetime(df["date"]).dt.month == 5) & (df["momentum_core_ready_v1"] == 1)].shape[0]
    )

    factor_columns = [
        "mom_1m",
        "mom_3m",
        "mom_6m",
        "mom_12m",
        "mom_12_1",
        "mom_6_1",
        "liq_money_1m",
        "liq_turnover_1m",
    ]
    lines = [
        "# Momentum Factor Panel V1",
        "",
        "Definition:",
        "- one row per `date x code` on the repaired JoinQuant daily price layer",
        "- merged with daily valuation support fields from the existing phase-1 raw layer",
        "- momentum fields use fixed trading-day windows: `20/60/120/240`",
        "- `mom_12_1` and `mom_6_1` skip the most recent `20` trading days",
        "- intended usage: later annual rebalancing should read the latest available row before execution to avoid look-ahead",
        "",
        f"- Rows: `{total_rows}`",
        f"- Stocks: `{code_count}`",
        f"- Date span: `{date_min}` to `{date_max}`",
        f"- Core-ready rows: `{ready_rows}`",
        f"- May core-ready rows: `{may_ready_rows}`",
        "",
        "Non-null coverage:",
    ]

    for column in factor_columns:
        lines.append(f"- `{column}`: `{int(df[column].notna().sum())}`")

    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = build_panel()
    panel_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    write_summary(panel_df)
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
