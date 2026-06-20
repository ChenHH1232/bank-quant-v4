from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"
CALENDAR_PATH = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1" / "trade_calendar.csv"
DETAIL_PATH = SCRIPT_DIR / "mean_reversion_execution_comparison_v1_detail.csv"
RESULTS_PATH = SCRIPT_DIR / "mean_reversion_execution_comparison_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "mean_reversion_execution_comparison_v1.md"

VALIDATION_START = pd.Timestamp("2019-01-01")
REVIEW_END = pd.Timestamp("2021-01-01")
TOP_N = 5


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    numeric_cols = [
        "close",
        "rev_5d",
        "abnormal_volume_ratio",
        "avg_money_20d",
        "avg_mcap_20d",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_calendar() -> pd.DataFrame:
    df = pd.read_csv(CALENDAR_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def add_signal_and_pool_flag(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["rev5_abnvol"] = -0.7 * out["rev_5d"] + 0.3 * out["abnormal_volume_ratio"]

    out["liq_cut"] = out.groupby("date")["avg_money_20d"].transform(lambda s: s.quantile(0.20))
    out["mcap_cut"] = out.groupby("date")["avg_mcap_20d"].transform(lambda s: s.quantile(0.20))
    out["pool_flag_v1"] = (
        (out["mean_reversion_ready_v1"] == 1)
        & out["avg_money_20d"].notna()
        & out["avg_mcap_20d"].notna()
        & (out["avg_money_20d"] >= out["liq_cut"])
        & (out["avg_mcap_20d"] >= out["mcap_cut"])
    ).astype(int)
    return out.drop(columns=["liq_cut", "mcap_cut"])


def build_weekly_rebalance_dates(calendar_df: pd.DataFrame) -> pd.DatetimeIndex:
    weekly = calendar_df.copy()
    iso = weekly["date"].dt.isocalendar()
    weekly["week_key"] = iso["year"].astype(str) + "-" + iso["week"].astype(str).str.zfill(2)
    picked = weekly.groupby("week_key", as_index=False).first()["date"]
    return pd.DatetimeIndex(picked.tolist())


def compute_period_metrics(period_returns: pd.Series, period_dates: pd.Series, next_period_dates: pd.Series) -> tuple[float, float, float]:
    if period_returns.empty:
        return math.nan, math.nan, math.nan
    equity = (1.0 + period_returns).cumprod()
    total_return = float(equity.iloc[-1] - 1.0)
    start_date = pd.to_datetime(period_dates.iloc[0])
    end_date = pd.to_datetime(next_period_dates.iloc[-1])
    elapsed_days = max((end_date - start_date).days, 1)
    annualized = float((1.0 + total_return) ** (365.25 / elapsed_days) - 1.0)
    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1.0
    max_drawdown = float(drawdown.min())
    return total_return, annualized, max_drawdown


def compute_subperiod_return(detail_df: pd.DataFrame, start_date: str, end_date: str) -> float:
    mask = (detail_df["rebalance_date"] >= pd.Timestamp(start_date)) & (detail_df["rebalance_date"] < pd.Timestamp(end_date))
    sample = detail_df.loc[mask, "period_return"].dropna()
    if sample.empty:
        return math.nan
    return float((1.0 + sample).prod() - 1.0)


def backtest_schedule(panel_df: pd.DataFrame, rebalance_dates: pd.DatetimeIndex, schedule_name: str) -> tuple[pd.DataFrame, dict[str, object]]:
    working = panel_df[(panel_df["date"] >= VALIDATION_START) & (panel_df["date"] < REVIEW_END)].copy()
    working = working.sort_values(["date", "code"]).reset_index(drop=True)

    valid_rebalance_dates = [date for date in rebalance_dates if VALIDATION_START <= date < REVIEW_END]
    trade_dates = sorted(working["date"].unique().tolist())
    trade_date_set = set(trade_dates)
    valid_rebalance_dates = [date for date in valid_rebalance_dates if date in trade_date_set]

    detail_rows: list[dict[str, object]] = []
    holdings_history: list[list[str]] = []

    for idx, rebalance_date in enumerate(valid_rebalance_dates):
        if idx + 1 >= len(valid_rebalance_dates):
            break
        next_rebalance_date = valid_rebalance_dates[idx + 1]

        cross = working[(working["date"] == rebalance_date) & (working["pool_flag_v1"] == 1)].copy()
        cross = cross.dropna(subset=["rev5_abnvol", "close"])
        cross = cross.sort_values(["rev5_abnvol", "code"], ascending=[True, True]).reset_index(drop=True)
        selected = cross.head(TOP_N).copy()
        holdings = selected["code"].tolist()
        holdings_history.append(holdings)

        if selected.empty:
            detail_rows.append(
                {
                    "schedule": schedule_name,
                    "rebalance_date": rebalance_date,
                    "next_rebalance_date": next_rebalance_date,
                    "hold_count": 0,
                    "turnover_ratio": math.nan,
                    "period_return": math.nan,
                    "selected_codes": "",
                }
            )
            continue

        next_cross = working[working["date"] == next_rebalance_date][["code", "close"]].rename(columns={"close": "next_close"})
        merged = selected[["code", "close", "rev5_abnvol"]].merge(next_cross, on="code", how="left")
        merged = merged.dropna(subset=["next_close"])
        merged["period_return"] = merged["next_close"] / merged["close"] - 1.0
        period_return = float(merged["period_return"].mean()) if not merged.empty else math.nan

        previous_holdings = set(holdings_history[-2]) if len(holdings_history) >= 2 else set()
        current_holdings = set(holdings)
        turnover_ratio = math.nan
        if current_holdings:
            kept = len(previous_holdings & current_holdings)
            turnover_ratio = 1.0 - kept / len(current_holdings)

        detail_rows.append(
            {
                "schedule": schedule_name,
                "rebalance_date": rebalance_date,
                "next_rebalance_date": next_rebalance_date,
                "hold_count": int(len(merged)),
                "turnover_ratio": turnover_ratio,
                "period_return": period_return,
                "selected_codes": ",".join(holdings),
            }
        )

    detail_df = pd.DataFrame(detail_rows)
    daily_proxy = detail_df.dropna(subset=["period_return"]).copy()
    daily_proxy["period_return"] = pd.to_numeric(daily_proxy["period_return"], errors="coerce")

    total_return, annualized, max_drawdown = compute_period_metrics(
        daily_proxy["period_return"],
        daily_proxy["rebalance_date"],
        daily_proxy["next_rebalance_date"],
    )

    metrics = {
        "schedule": schedule_name,
        "rebalance_count": int(detail_df["rebalance_date"].nunique()),
        "traded_periods": int(daily_proxy["rebalance_date"].nunique()),
        "avg_hold_count": round(float(detail_df["hold_count"].mean()), 4) if not detail_df.empty else math.nan,
        "avg_turnover_ratio": round(float(detail_df["turnover_ratio"].dropna().mean()), 6) if detail_df["turnover_ratio"].dropna().shape[0] > 0 else math.nan,
        "total_return": round(total_return, 6) if not math.isnan(total_return) else math.nan,
        "annualized_return_proxy": round(annualized, 6) if not math.isnan(annualized) else math.nan,
        "max_drawdown_proxy": round(max_drawdown, 6) if not math.isnan(max_drawdown) else math.nan,
        "return_2019": round(compute_subperiod_return(detail_df, "2019-01-01", "2020-01-01"), 6),
        "return_2020": round(compute_subperiod_return(detail_df, "2020-01-01", "2021-01-01"), 6),
    }
    return detail_df, metrics


def write_summary(result_df: pd.DataFrame, detail_df: pd.DataFrame) -> None:
    lines = [
        "# Mean Reversion Execution Comparison V1",
        "",
        "Purpose:",
        "- compare `daily execution` and `weekly execution` for the frozen standalone mean-reversion V1 spec",
        "- keep the signal fixed as `rev5_abnvol`",
        "- keep equal-weight holding count fixed at `5`",
        "- keep liquidity and market-cap gate as cross-sectional bottom-20% exclusion on each trade date",
        "",
        "Window:",
        "- evaluation: `2019-01-01` to `2020-12-31`",
        "- this keeps the execution-rhythm comparison inside the pre-2021 research reserve",
        "",
        "Results:",
    ]

    ranked = result_df.sort_values("total_return", ascending=False).reset_index(drop=True)
    for _, row in ranked.iterrows():
        lines.append(
            f"- `{row['schedule']}` | total_return=`{row['total_return']}` | annualized_proxy=`{row['annualized_return_proxy']}` | max_drawdown_proxy=`{row['max_drawdown_proxy']}` | return_2019=`{row['return_2019']}` | return_2020=`{row['return_2020']}` | avg_turnover=`{row['avg_turnover_ratio']}` | traded_periods=`{row['traded_periods']}`"
        )

    if not ranked.empty:
        best = ranked.iloc[0]["schedule"]
        lines.extend(
            [
                "",
                "Current read:",
                f"- the stronger first-pass execution rhythm is `{best}` on this fixed signal spec",
                "- this result should be treated as execution evidence, not as permission to retune the signal on later out-of-sample windows",
            ]
        )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{RESULTS_PATH.name}]({RESULTS_PATH})",
            f"- [{DETAIL_PATH.name}]({DETAIL_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = add_signal_and_pool_flag(load_panel())
    calendar_df = load_calendar()

    daily_rebalance_dates = pd.DatetimeIndex(calendar_df["date"].tolist())
    weekly_rebalance_dates = build_weekly_rebalance_dates(calendar_df)

    daily_detail, daily_metrics = backtest_schedule(panel_df, daily_rebalance_dates, "daily")
    weekly_detail, weekly_metrics = backtest_schedule(panel_df, weekly_rebalance_dates, "weekly")

    detail_df = pd.concat([daily_detail, weekly_detail], ignore_index=True)
    result_df = pd.DataFrame([daily_metrics, weekly_metrics])

    detail_df.to_csv(DETAIL_PATH, index=False, encoding="utf-8-sig")
    result_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8-sig")
    write_summary(result_df, detail_df)

    print(RESULTS_PATH)
    print(DETAIL_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
