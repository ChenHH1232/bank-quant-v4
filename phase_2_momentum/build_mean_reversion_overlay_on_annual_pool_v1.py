from __future__ import annotations

import ast
import math
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"
CALENDAR_PATH = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1" / "trade_calendar.csv"
ANNUAL_POOL_PATH = SCRIPT_DIR.parent / "phase_1_fundamental" / "joinquant_v4_annual_attribution_v1.csv"
DETAIL_PATH = SCRIPT_DIR / "mean_reversion_overlay_on_annual_pool_v1_detail.csv"
RESULT_PATH = SCRIPT_DIR / "mean_reversion_overlay_on_annual_pool_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "mean_reversion_overlay_on_annual_pool_v1.md"

WINDOW_START = pd.Timestamp("2021-05-31")
WINDOW_END = pd.Timestamp("2026-05-01")
OVERLAY_TOP_N = 5


def load_panel() -> pd.DataFrame:
    cols = [
        "date",
        "code",
        "close",
        "rev_5d",
        "abnormal_volume_ratio",
        "avg_money_20d",
        "avg_mcap_20d",
        "mean_reversion_ready_v1",
    ]
    df = pd.read_csv(PANEL_PATH, usecols=cols, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    for col in cols[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["rev5_abnvol"] = -0.7 * df["rev_5d"] + 0.3 * df["abnormal_volume_ratio"]
    return df


def load_calendar() -> pd.DatetimeIndex:
    df = pd.read_csv(CALENDAR_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df[(df["date"] >= WINDOW_START) & (df["date"] < WINDOW_END)].copy()
    iso = df["date"].dt.isocalendar()
    df["week_key"] = iso["year"].astype(str) + "-" + iso["week"].astype(str).str.zfill(2)
    weekly = df.groupby("week_key", as_index=False).first()["date"]
    return pd.DatetimeIndex(weekly.tolist())


def load_annual_pool_schedule() -> pd.DataFrame:
    df = pd.read_csv(ANNUAL_POOL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_line"] == "primary"].copy()
    df["current_date"] = pd.to_datetime(df["current_date"])
    df = df[(df["current_date"] >= WINDOW_START) & (df["current_date"] < WINDOW_END)].copy()
    df["selected_codes"] = df["long_list"].apply(ast.literal_eval)
    return df.sort_values("current_date").reset_index(drop=True)


def build_pool_flag(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
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


def active_pool_for_date(schedule_df: pd.DataFrame, current_date: pd.Timestamp) -> list[str]:
    eligible = schedule_df[schedule_df["current_date"] <= current_date]
    if eligible.empty:
        return []
    return list(eligible.iloc[-1]["selected_codes"])


def compute_equity_metrics(period_returns: pd.Series, rebalance_dates: pd.Series, next_dates: pd.Series) -> tuple[float, float, float]:
    sample = period_returns.dropna()
    if sample.empty:
        return math.nan, math.nan, math.nan
    equity = (1.0 + sample).cumprod()
    total_return = float(equity.iloc[-1] - 1.0)
    start_date = pd.to_datetime(rebalance_dates.iloc[0])
    end_date = pd.to_datetime(next_dates.iloc[-1])
    elapsed_days = max((end_date - start_date).days, 1)
    annualized = float((1.0 + total_return) ** (365.25 / elapsed_days) - 1.0)
    drawdown = equity / equity.cummax() - 1.0
    return total_return, annualized, float(drawdown.min())


def compute_subperiod_return(detail_df: pd.DataFrame, strategy_name: str, start_date: str, end_date: str) -> float:
    sample = detail_df[
        (detail_df["strategy_name"] == strategy_name)
        & (detail_df["rebalance_date"] >= pd.Timestamp(start_date))
        & (detail_df["rebalance_date"] < pd.Timestamp(end_date))
    ]["period_return"].dropna()
    if sample.empty:
        return math.nan
    return float((1.0 + sample).prod() - 1.0)


def run_overlay_backtest(panel_df: pd.DataFrame, weekly_dates: pd.DatetimeIndex, schedule_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel_df = panel_df[(panel_df["date"] >= WINDOW_START) & (panel_df["date"] < WINDOW_END)].copy()
    detail_rows: list[dict[str, object]] = []

    for idx, rebalance_date in enumerate(weekly_dates):
        if idx + 1 >= len(weekly_dates):
            break
        next_date = weekly_dates[idx + 1]
        approved_codes = active_pool_for_date(schedule_df, rebalance_date)
        if not approved_codes:
            continue

        cross = panel_df[(panel_df["date"] == rebalance_date) & (panel_df["code"].isin(approved_codes))].copy()
        next_cross = panel_df[(panel_df["date"] == next_date) & (panel_df["code"].isin(approved_codes))][["code", "close"]].rename(columns={"close": "next_close"})
        if cross.empty or next_cross.empty:
            continue

        baseline = cross[["code", "close"]].merge(next_cross, on="code", how="inner")
        baseline["period_return"] = baseline["next_close"] / baseline["close"] - 1.0
        baseline_return = float(baseline["period_return"].mean()) if not baseline.empty else math.nan

        overlay_cross = cross[(cross["pool_flag_v1"] == 1) & cross["rev5_abnvol"].notna()].copy()
        overlay_cross = overlay_cross.sort_values(["rev5_abnvol", "code"], ascending=[True, True]).reset_index(drop=True)
        overlay_selected = overlay_cross.head(min(OVERLAY_TOP_N, len(overlay_cross))).copy()
        overlay_merged = overlay_selected[["code", "close"]].merge(next_cross, on="code", how="inner")
        overlay_merged["period_return"] = overlay_merged["next_close"] / overlay_merged["close"] - 1.0
        overlay_return = float(overlay_merged["period_return"].mean()) if not overlay_merged.empty else math.nan

        detail_rows.append(
            {
                "rebalance_date": rebalance_date,
                "next_rebalance_date": next_date,
                "approved_pool_count": len(approved_codes),
                "overlay_eligible_count": int(len(overlay_cross)),
                "baseline_hold_count": int(len(baseline)),
                "overlay_hold_count": int(len(overlay_merged)),
                "baseline_period_return": baseline_return,
                "overlay_period_return": overlay_return,
                "baseline_codes": ",".join(sorted(baseline["code"].tolist())),
                "overlay_codes": ",".join(overlay_selected["code"].tolist()),
            }
        )

    detail_df = pd.DataFrame(detail_rows)
    long_df = pd.concat(
        [
            detail_df[["rebalance_date", "next_rebalance_date", "baseline_period_return"]]
            .rename(columns={"baseline_period_return": "period_return"})
            .assign(strategy_name="annual_pool_baseline"),
            detail_df[["rebalance_date", "next_rebalance_date", "overlay_period_return"]]
            .rename(columns={"overlay_period_return": "period_return"})
            .assign(strategy_name="annual_pool_overlay_rev5_abnvol"),
        ],
        ignore_index=True,
    )
    long_df = long_df.dropna(subset=["period_return"]).reset_index(drop=True)

    metrics_rows: list[dict[str, object]] = []
    for strategy_name, group in long_df.groupby("strategy_name"):
        total_return, annualized, max_drawdown = compute_equity_metrics(
            group["period_return"], group["rebalance_date"], group["next_rebalance_date"]
        )
        metrics_rows.append(
            {
                "strategy_name": strategy_name,
                "traded_periods": int(len(group)),
                "total_return": round(total_return, 6) if not math.isnan(total_return) else math.nan,
                "annualized_return_proxy": round(annualized, 6) if not math.isnan(annualized) else math.nan,
                "max_drawdown_proxy": round(max_drawdown, 6) if not math.isnan(max_drawdown) else math.nan,
                "return_2021_2022": round(compute_subperiod_return(long_df, strategy_name, "2021-05-31", "2023-01-01"), 6),
                "return_2023_2024": round(compute_subperiod_return(long_df, strategy_name, "2023-01-01", "2025-01-01"), 6),
                "return_2025_2026": round(compute_subperiod_return(long_df, strategy_name, "2025-01-01", "2026-05-01"), 6),
                "avg_overlay_eligible_count": round(float(detail_df["overlay_eligible_count"].mean()), 4) if not detail_df.empty else math.nan,
                "avg_approved_pool_count": round(float(detail_df["approved_pool_count"].mean()), 4) if not detail_df.empty else math.nan,
            }
        )

    return detail_df, pd.DataFrame(metrics_rows)


def write_summary(result_df: pd.DataFrame) -> None:
    ranked = result_df.sort_values("total_return", ascending=False).reset_index(drop=True)
    lines = [
        "# Mean Reversion Overlay On Annual Pool V1",
        "",
        "Purpose:",
        "- test whether the frozen weekly mean-reversion layer can improve execution inside the real annual approved pool",
        "- use the actual `primary` annual holding schedule exported from JoinQuant attribution logs",
        "- treat this as post-2021 acceptance observation, not parameter-tuning evidence",
        "",
        "Setup:",
        "- upper approved pool source: `phase_1_fundamental/joinquant_v4_annual_attribution_v1.csv`",
        "- upper pool line: `primary`",
        "- tactical signal: `rev5_abnvol`",
        "- tactical frequency: weekly",
        f"- tactical top N inside approved pool: `{OVERLAY_TOP_N}`",
        "- baseline: equal-weight hold the full approved pool until the next weekly checkpoint",
        "",
        "Window:",
        "- acceptance observation: `2021-05-31` to `2026-04-30`",
        "",
        "Results:",
    ]

    for _, row in ranked.iterrows():
        lines.append(
            f"- `{row['strategy_name']}` | total_return=`{row['total_return']}` | annualized_proxy=`{row['annualized_return_proxy']}` | max_drawdown_proxy=`{row['max_drawdown_proxy']}` | 2021_2022=`{row['return_2021_2022']}` | 2023_2024=`{row['return_2023_2024']}` | 2025_2026=`{row['return_2025_2026']}` | traded_periods=`{row['traded_periods']}`"
        )

    if len(ranked) >= 2:
        best = ranked.iloc[0]["strategy_name"]
        lines.extend(
            [
                "",
                "Current read:",
                f"- on the frozen acceptance window, `{best}` is the stronger execution path inside the annual approved pool",
                "- because this uses the post-2021 window, it should guide deployment interpretation only and should not be used to retune the signal coefficients",
            ]
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


def main() -> None:
    panel_df = build_pool_flag(load_panel())
    weekly_dates = load_calendar()
    schedule_df = load_annual_pool_schedule()
    detail_df, result_df = run_overlay_backtest(panel_df, weekly_dates, schedule_df)
    detail_df.to_csv(DETAIL_PATH, index=False, encoding="utf-8-sig")
    result_df.to_csv(RESULT_PATH, index=False, encoding="utf-8-sig")
    write_summary(result_df)
    print(RESULT_PATH)
    print(DETAIL_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
