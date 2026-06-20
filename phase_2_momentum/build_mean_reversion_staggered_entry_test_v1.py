from __future__ import annotations

import ast
import math
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"
CALENDAR_PATH = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1" / "trade_calendar.csv"
ANNUAL_POOL_PATH = SCRIPT_DIR.parent / "phase_1_fundamental" / "joinquant_v4_annual_attribution_v1.csv"
RESULT_PATH = SCRIPT_DIR / "mean_reversion_staggered_entry_test_v1.csv"
DETAIL_PATH = SCRIPT_DIR / "mean_reversion_staggered_entry_test_v1_detail.csv"
SUMMARY_PATH = SCRIPT_DIR / "mean_reversion_staggered_entry_test_v1.md"

WINDOW_START = pd.Timestamp("2021-05-31")
WINDOW_END = pd.Timestamp("2026-05-01")
SEARCH_WEEKS = 4
HOLD_WEEKS = 12
IMMEDIATE_WEIGHT = 0.5
TIMED_WEIGHT = 0.5


def load_panel() -> pd.DataFrame:
    cols = ["date", "code", "close", "rev_5d", "abnormal_volume_ratio", "mean_reversion_ready_v1"]
    df = pd.read_csv(PANEL_PATH, usecols=cols, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    for col in cols[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["rev5_abnvol"] = -0.7 * df["rev_5d"] + 0.3 * df["abnormal_volume_ratio"]
    return df[(df["date"] >= WINDOW_START) & (df["date"] < WINDOW_END)].copy()


def load_weekly_dates() -> list[pd.Timestamp]:
    df = pd.read_csv(CALENDAR_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df[(df["date"] >= WINDOW_START) & (df["date"] < WINDOW_END)].copy()
    iso = df["date"].dt.isocalendar()
    df["week_key"] = iso["year"].astype(str) + "-" + iso["week"].astype(str).str.zfill(2)
    return [pd.Timestamp(x) for x in df.groupby("week_key", as_index=False).first()["date"].tolist()]


def load_rebalance_schedule() -> pd.DataFrame:
    df = pd.read_csv(ANNUAL_POOL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_line"] == "primary"].copy()
    df["current_date"] = pd.to_datetime(df["current_date"])
    df = df[(df["current_date"] >= WINDOW_START) & (df["current_date"] < WINDOW_END)].copy()
    df["selected_codes"] = df["long_list"].apply(ast.literal_eval)
    return df.sort_values("current_date").reset_index(drop=True)


def next_week_index(weekly_dates: list[pd.Timestamp], current_date: pd.Timestamp) -> int | None:
    for idx, date_value in enumerate(weekly_dates):
        if date_value >= current_date:
            return idx
    return None


def basket_return(panel_df: pd.DataFrame, codes: list[str], buy_date: pd.Timestamp, sell_date: pd.Timestamp) -> float:
    buy = panel_df[(panel_df["date"] == buy_date) & (panel_df["code"].isin(codes))][["code", "close"]]
    sell = panel_df[(panel_df["date"] == sell_date) & (panel_df["code"].isin(codes))][["code", "close"]].rename(columns={"close": "sell_close"})
    merged = buy.merge(sell, on="code", how="inner")
    if merged.empty:
        return math.nan
    merged["ret"] = merged["sell_close"] / merged["close"] - 1.0
    return float(merged["ret"].mean())


def basket_signal(panel_df: pd.DataFrame, codes: list[str], signal_date: pd.Timestamp) -> float:
    cross = panel_df[(panel_df["date"] == signal_date) & (panel_df["code"].isin(codes))].copy()
    cross = cross[(cross["mean_reversion_ready_v1"] == 1) & cross["rev5_abnvol"].notna()]
    if cross.empty:
        return math.nan
    return float(cross["rev5_abnvol"].mean())


def compute_metrics(returns: pd.Series) -> tuple[float, float]:
    sample = returns.dropna()
    if sample.empty:
        return math.nan, math.nan
    total_return = float((1.0 + sample).prod() - 1.0)
    equity = (1.0 + sample).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return total_return, float(drawdown.min())


def main() -> None:
    panel_df = load_panel()
    weekly_dates = load_weekly_dates()
    schedule_df = load_rebalance_schedule()

    detail_rows: list[dict[str, object]] = []
    for _, row in schedule_df.iterrows():
        rebalance_date = pd.Timestamp(row["current_date"])
        codes = list(row["selected_codes"])
        start_idx = next_week_index(weekly_dates, rebalance_date)
        if start_idx is None:
            continue
        end_hold_idx = start_idx + HOLD_WEEKS
        if end_hold_idx >= len(weekly_dates):
            continue

        immediate_buy_date = weekly_dates[start_idx]
        immediate_sell_date = weekly_dates[end_hold_idx]
        immediate_return = basket_return(panel_df, codes, immediate_buy_date, immediate_sell_date)

        search_slice = weekly_dates[start_idx : min(start_idx + SEARCH_WEEKS, len(weekly_dates))]
        candidate_rows = []
        for candidate_date in search_slice:
            signal_value = basket_signal(panel_df, codes, candidate_date)
            candidate_rows.append({"candidate_date": candidate_date, "signal_value": signal_value})
        candidate_df = pd.DataFrame(candidate_rows).dropna(subset=["signal_value"]).sort_values(["signal_value", "candidate_date"])
        if candidate_df.empty:
            timed_buy_date = immediate_buy_date
            timed_signal = math.nan
        else:
            timed_buy_date = pd.Timestamp(candidate_df.iloc[0]["candidate_date"])
            timed_signal = float(candidate_df.iloc[0]["signal_value"])

        timed_sell_idx = next_week_index(weekly_dates, timed_buy_date)
        if timed_sell_idx is None:
            continue
        timed_sell_idx += HOLD_WEEKS
        if timed_sell_idx >= len(weekly_dates):
            continue
        timed_sell_date = weekly_dates[timed_sell_idx]
        timed_return = basket_return(panel_df, codes, timed_buy_date, timed_sell_date)

        staggered_return = math.nan
        if not math.isnan(immediate_return) and not math.isnan(timed_return):
            staggered_return = IMMEDIATE_WEIGHT * immediate_return + TIMED_WEIGHT * timed_return

        detail_rows.append(
            {
                "rebalance_date": rebalance_date,
                "approved_count": len(codes),
                "immediate_buy_date": immediate_buy_date,
                "timed_buy_date": timed_buy_date,
                "timing_signal_value": timed_signal,
                "immediate_return_12w": immediate_return,
                "timed_return_12w": timed_return,
                "staggered_return_12w": staggered_return,
                "timing_delay_weeks": int((timed_buy_date - immediate_buy_date).days / 7),
                "selected_codes": ",".join(codes),
            }
        )

    detail_df = pd.DataFrame(detail_rows)
    rows = []
    for strategy_name, col_name, avg_delay in [
        ("immediate_entry", "immediate_return_12w", 0.0),
        ("timed_entry_rev5_abnvol", "timed_return_12w", round(float(detail_df["timing_delay_weeks"].mean()), 6) if not detail_df.empty else math.nan),
        ("staggered_entry_50_50", "staggered_return_12w", round(float(detail_df["timing_delay_weeks"].mean()) * TIMED_WEIGHT, 6) if not detail_df.empty else math.nan),
    ]:
        total_return, max_dd = compute_metrics(detail_df[col_name])
        rows.append(
            {
                "strategy_name": strategy_name,
                "case_count": int(len(detail_df)),
                "avg_delay_weeks_proxy": avg_delay,
                "total_return_proxy": round(total_return, 6) if not math.isnan(total_return) else math.nan,
                "max_drawdown_proxy": round(max_dd, 6) if not math.isnan(max_dd) else math.nan,
                "avg_case_return_12w": round(float(detail_df[col_name].mean()), 6) if not detail_df.empty else math.nan,
                "median_case_return_12w": round(float(detail_df[col_name].median()), 6) if not detail_df.empty else math.nan,
            }
        )
    result_df = pd.DataFrame(rows)
    detail_df.to_csv(DETAIL_PATH, index=False, encoding="utf-8-sig")
    result_df.to_csv(RESULT_PATH, index=False, encoding="utf-8-sig")

    lines = [
        "# Mean Reversion Staggered Entry Test V1",
        "",
        "Purpose:",
        "- compare immediate entry, full delayed entry, and 50/50 staggered entry",
        "- keep the annual approved basket unchanged",
        "- only change when the second half of the basket gets deployed",
        "",
        "Frozen setup:",
        f"- search window: `{SEARCH_WEEKS}` weekly checkpoints",
        f"- holding horizon per leg proxy: `{HOLD_WEEKS}` weeks",
        f"- immediate leg weight: `{IMMEDIATE_WEIGHT}`",
        f"- delayed leg weight: `{TIMED_WEIGHT}`",
        "",
        "Results:",
    ]
    for _, row in result_df.iterrows():
        lines.append(
            f"- `{row['strategy_name']}` | total_return_proxy=`{row['total_return_proxy']}` | max_drawdown_proxy=`{row['max_drawdown_proxy']}` | avg_case_return_12w=`{row['avg_case_return_12w']}` | median_case_return_12w=`{row['median_case_return_12w']}` | avg_delay_weeks_proxy=`{row['avg_delay_weeks_proxy']}`"
        )
    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{RESULT_PATH.name}]({RESULT_PATH})",
            f"- [{DETAIL_PATH.name}]({DETAIL_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(RESULT_PATH)
    print(DETAIL_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
