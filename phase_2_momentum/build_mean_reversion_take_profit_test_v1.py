from __future__ import annotations

import ast
import math
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"
CALENDAR_PATH = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1" / "trade_calendar.csv"
ANNUAL_POOL_PATH = SCRIPT_DIR.parent / "phase_1_fundamental" / "joinquant_v4_annual_attribution_v1.csv"
RESULT_PATH = SCRIPT_DIR / "mean_reversion_take_profit_test_v1.csv"
DETAIL_PATH = SCRIPT_DIR / "mean_reversion_take_profit_test_v1_detail.csv"
SUMMARY_PATH = SCRIPT_DIR / "mean_reversion_take_profit_test_v1.md"

WINDOW_START = pd.Timestamp("2021-05-31")
WINDOW_END = pd.Timestamp("2026-05-01")
TRIM_RATIO = 0.5


def load_panel() -> pd.DataFrame:
    cols = [
        "date",
        "code",
        "close",
        "rev_5d",
        "abnormal_volume_ratio",
        "close_to_ma20",
        "mean_reversion_ready_v1",
    ]
    df = pd.read_csv(PANEL_PATH, usecols=cols, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    for col in cols[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[(df["date"] >= WINDOW_START) & (df["date"] < WINDOW_END)].copy()
    df["overheat_score_v1"] = 0.6 * df["rev_5d"] + 0.2 * df["abnormal_volume_ratio"] + 0.2 * df["close_to_ma20"]
    return df


def load_weekly_dates() -> list[pd.Timestamp]:
    df = pd.read_csv(CALENDAR_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df[(df["date"] >= WINDOW_START) & (df["date"] < WINDOW_END)].copy()
    iso = df["date"].dt.isocalendar()
    df["week_key"] = iso["year"].astype(str) + "-" + iso["week"].astype(str).str.zfill(2)
    return [pd.Timestamp(x) for x in df.groupby("week_key", as_index=False).first()["date"].tolist()]


def load_annual_schedule() -> pd.DataFrame:
    df = pd.read_csv(ANNUAL_POOL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_line"] == "primary"].copy()
    df["current_date"] = pd.to_datetime(df["current_date"])
    df = df[(df["current_date"] >= WINDOW_START) & (df["current_date"] < WINDOW_END)].copy()
    df["selected_codes"] = df["long_list"].apply(ast.literal_eval)
    return df.sort_values("current_date").reset_index(drop=True)


def active_pool(schedule_df: pd.DataFrame, current_date: pd.Timestamp) -> list[str]:
    eligible = schedule_df[schedule_df["current_date"] <= current_date]
    if eligible.empty:
        return []
    return list(eligible.iloc[-1]["selected_codes"])


def compute_metrics(period_returns: pd.Series) -> tuple[float, float]:
    sample = period_returns.dropna()
    if sample.empty:
        return math.nan, math.nan
    total_return = float((1.0 + sample).prod() - 1.0)
    equity = (1.0 + sample).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return total_return, float(drawdown.min())


def main() -> None:
    panel_df = load_panel()
    weekly_dates = load_weekly_dates()
    schedule_df = load_annual_schedule()

    detail_rows: list[dict[str, object]] = []
    for idx, current_date in enumerate(weekly_dates[:-1]):
        next_date = weekly_dates[idx + 1]
        approved_codes = active_pool(schedule_df, current_date)
        if not approved_codes:
            continue

        cross = panel_df[(panel_df["date"] == current_date) & (panel_df["code"].isin(approved_codes))].copy()
        next_cross = panel_df[(panel_df["date"] == next_date) & (panel_df["code"].isin(approved_codes))][["code", "close"]].rename(columns={"close": "next_close"})
        merged = cross.merge(next_cross, on="code", how="inner")
        merged = merged[(merged["mean_reversion_ready_v1"] == 1) & merged["close"].notna() & merged["next_close"].notna()]
        if merged.empty:
            continue

        merged["forward_return_1w"] = merged["next_close"] / merged["close"] - 1.0
        baseline_return = float(merged["forward_return_1w"].mean())

        score_series = merged["overheat_score_v1"]
        threshold = float(score_series.quantile(0.80)) if score_series.notna().sum() >= 3 else math.nan
        merged["is_overheat"] = ((merged["overheat_score_v1"] >= threshold) & merged["overheat_score_v1"].notna()).astype(int) if not math.isnan(threshold) else 0
        merged["trimmed_forward_return_1w"] = merged["forward_return_1w"]
        merged.loc[merged["is_overheat"] == 1, "trimmed_forward_return_1w"] = merged.loc[merged["is_overheat"] == 1, "forward_return_1w"] * (1.0 - TRIM_RATIO)
        trimmed_return = float(merged["trimmed_forward_return_1w"].mean())

        detail_rows.append(
            {
                "current_date": current_date,
                "next_date": next_date,
                "approved_count": len(approved_codes),
                "usable_count": int(len(merged)),
                "overheat_count": int(merged["is_overheat"].sum()),
                "overheat_threshold": threshold,
                "baseline_return_1w": baseline_return,
                "trimmed_return_1w": trimmed_return,
                "avg_overheat_score": float(merged["overheat_score_v1"].mean()) if merged["overheat_score_v1"].notna().sum() > 0 else math.nan,
                "overheat_codes": ",".join(merged.loc[merged["is_overheat"] == 1, "code"].tolist()),
            }
        )

    detail_df = pd.DataFrame(detail_rows)
    baseline_total, baseline_dd = compute_metrics(detail_df["baseline_return_1w"])
    trimmed_total, trimmed_dd = compute_metrics(detail_df["trimmed_return_1w"])

    result_df = pd.DataFrame(
        [
            {
                "strategy_name": "baseline_hold",
                "period_count": int(len(detail_df)),
                "avg_overheat_count": round(float(detail_df["overheat_count"].mean()), 6) if not detail_df.empty else math.nan,
                "total_return_proxy": round(baseline_total, 6) if not math.isnan(baseline_total) else math.nan,
                "max_drawdown_proxy": round(baseline_dd, 6) if not math.isnan(baseline_dd) else math.nan,
                "avg_period_return_1w": round(float(detail_df["baseline_return_1w"].mean()), 6) if not detail_df.empty else math.nan,
                "median_period_return_1w": round(float(detail_df["baseline_return_1w"].median()), 6) if not detail_df.empty else math.nan,
            },
            {
                "strategy_name": "partial_take_profit_trim50",
                "period_count": int(len(detail_df)),
                "avg_overheat_count": round(float(detail_df["overheat_count"].mean()), 6) if not detail_df.empty else math.nan,
                "total_return_proxy": round(trimmed_total, 6) if not math.isnan(trimmed_total) else math.nan,
                "max_drawdown_proxy": round(trimmed_dd, 6) if not math.isnan(trimmed_dd) else math.nan,
                "avg_period_return_1w": round(float(detail_df["trimmed_return_1w"].mean()), 6) if not detail_df.empty else math.nan,
                "median_period_return_1w": round(float(detail_df["trimmed_return_1w"].median()), 6) if not detail_df.empty else math.nan,
            },
        ]
    )

    detail_df.to_csv(DETAIL_PATH, index=False, encoding="utf-8-sig")
    result_df.to_csv(RESULT_PATH, index=False, encoding="utf-8-sig")

    lines = [
        "# Mean Reversion Take-Profit Test V1",
        "",
        "Purpose:",
        "- test a minimal partial take-profit overlay inside the annual approved pool",
        "- keep the approved holdings unchanged",
        "- only reduce next-period exposure on names flagged as overheated",
        "",
        "Frozen setup:",
        "- overheat score: `0.6 * rev_5d + 0.2 * abnormal_volume_ratio + 0.2 * close_to_ma20`",
        "- overheat threshold: top 20% within the approved pool on each weekly checkpoint",
        f"- trim ratio: `{TRIM_RATIO}`",
        "",
        "Results:",
    ]
    for _, row in result_df.iterrows():
        lines.append(
            f"- `{row['strategy_name']}` | total_return_proxy=`{row['total_return_proxy']}` | max_drawdown_proxy=`{row['max_drawdown_proxy']}` | avg_period_return_1w=`{row['avg_period_return_1w']}` | median_period_return_1w=`{row['median_period_return_1w']}` | avg_overheat_count=`{row['avg_overheat_count']}`"
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
