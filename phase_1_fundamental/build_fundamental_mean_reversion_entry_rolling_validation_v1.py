from __future__ import annotations

import csv
import math
from pathlib import Path

import pandas as pd

from build_annual_factor_refresh_5y2y1y_memory_carry_v1 import (
    build_yearly_folds,
    select_factor_rows,
)
from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_ENHANCED,
    add_combo_scores,
    build_scenario_rows,
    build_scored_panel,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
)
from build_pre2021_rolling_validation_v1 import assign_groups


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
MEAN_REV_PANEL_PATH = ROOT_DIR / "phase_2_momentum" / "mean_reversion_factor_panel_v1.csv"

OUTPUT_DETAIL_PATH = SCRIPT_DIR / "fundamental_mean_reversion_entry_rolling_validation_v1_detail.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "fundamental_mean_reversion_entry_rolling_validation_v1_summary.csv"
OUTPUT_NOTE_PATH = SCRIPT_DIR / "fundamental_mean_reversion_entry_rolling_validation_v1.md"

TARGET_SCENARIO = SCENARIO_ENHANCED
TARGET_COMBO = "combo__ic_weight_train"
GROUP_COUNT = 5
HOLD_BUCKET = 5
SEARCH_TRADING_DAYS = 20
REV_SIGNAL_QUANTILE = 0.30
IMMEDIATE_WEIGHT = 0.5
DELAYED_WEIGHT = 0.5


def load_daily_panel() -> pd.DataFrame:
    usecols = ["date", "code", "close", "rev_5d", "abnormal_volume_ratio", "mean_reversion_ready_v1"]
    df = pd.read_csv(MEAN_REV_PANEL_PATH, usecols=usecols, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    for col in ["close", "rev_5d", "abnormal_volume_ratio", "mean_reversion_ready_v1"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["rev5_abnvol"] = -0.7 * df["rev_5d"] + 0.3 * df["abnormal_volume_ratio"]
    return df.sort_values(["date", "code"]).reset_index(drop=True)


def get_trade_dates(daily_df: pd.DataFrame) -> list[pd.Timestamp]:
    return sorted(pd.to_datetime(daily_df["date"].drop_duplicates()).tolist())


def first_trade_on_or_after(trade_dates: list[pd.Timestamp], target_date: pd.Timestamp) -> pd.Timestamp | None:
    for date_value in trade_dates:
        if date_value >= target_date:
            return pd.Timestamp(date_value)
    return None


def nth_trade_on_or_after(
    trade_dates: list[pd.Timestamp],
    start_date: pd.Timestamp,
    offset: int,
) -> pd.Timestamp | None:
    base_date = first_trade_on_or_after(trade_dates, start_date)
    if base_date is None:
        return None
    base_idx = trade_dates.index(base_date)
    target_idx = base_idx + offset
    if target_idx >= len(trade_dates):
        return None
    return pd.Timestamp(trade_dates[target_idx])


def basket_signal(daily_df: pd.DataFrame, codes: list[str], signal_date: pd.Timestamp) -> float:
    cross = daily_df[(daily_df["date"] == signal_date) & (daily_df["code"].isin(codes))].copy()
    cross = cross[(cross["mean_reversion_ready_v1"] == 1) & cross["rev5_abnvol"].notna()]
    if cross.empty:
        return math.nan
    return float(pd.to_numeric(cross["rev5_abnvol"], errors="coerce").mean())


def basket_return(daily_df: pd.DataFrame, codes: list[str], buy_date: pd.Timestamp, sell_date: pd.Timestamp) -> float:
    buy = daily_df[(daily_df["date"] == buy_date) & (daily_df["code"].isin(codes))][["code", "close"]].copy()
    sell = (
        daily_df[(daily_df["date"] == sell_date) & (daily_df["code"].isin(codes))][["code", "close"]]
        .rename(columns={"close": "sell_close"})
        .copy()
    )
    merged = buy.merge(sell, on="code", how="inner")
    if merged.empty:
        return math.nan
    merged["ret"] = pd.to_numeric(merged["sell_close"], errors="coerce") / pd.to_numeric(
        merged["close"], errors="coerce"
    ) - 1.0
    return float(merged["ret"].mean())


def compute_drawdown(return_series: pd.Series) -> float:
    sample = pd.to_numeric(return_series, errors="coerce").dropna()
    if sample.empty:
        return math.nan
    equity = (1.0 + sample).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return float(drawdown.min())


def build_window_holdings(
    panel_df: pd.DataFrame,
    scored_df: pd.DataFrame,
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    window_df = scored_df[(scored_df["rebalance_date"] >= window_start) & (scored_df["rebalance_date"] < window_end)].copy()
    rebalance_dates = sorted(pd.to_datetime(window_df["rebalance_date"].drop_duplicates()).tolist())
    for idx, rebalance_date in enumerate(rebalance_dates):
        group = window_df[window_df["rebalance_date"] == rebalance_date].copy()
        group = group.dropna(subset=[TARGET_COMBO]).copy()
        if len(group) < GROUP_COUNT:
            continue
        group["bucket"] = assign_groups(group[TARGET_COMBO], GROUP_COUNT)
        group = group.dropna(subset=["bucket"]).copy()
        long_df = group[group["bucket"] == HOLD_BUCKET].copy()
        if long_df.empty:
            continue
        next_rebalance_date = rebalance_dates[idx + 1] if idx + 1 < len(rebalance_dates) else None
        rows.append(
            {
                "rebalance_date": pd.Timestamp(rebalance_date),
                "next_rebalance_date": pd.Timestamp(next_rebalance_date) if next_rebalance_date is not None else pd.NaT,
                "selected_codes": sorted(long_df["code"].astype(str).tolist()),
                "selected_count": int(len(long_df)),
            }
        )
    return rows


def collect_train_signal_values(
    holdings_rows: list[dict[str, object]],
    daily_df: pd.DataFrame,
    trade_dates: list[pd.Timestamp],
) -> list[float]:
    signal_values: list[float] = []
    for row in holdings_rows:
        rebalance_date = pd.Timestamp(row["rebalance_date"])
        codes = list(row["selected_codes"])
        start_trade = first_trade_on_or_after(trade_dates, rebalance_date)
        if start_trade is None:
            continue
        for offset in range(SEARCH_TRADING_DAYS):
            signal_date = nth_trade_on_or_after(trade_dates, start_trade, offset)
            if signal_date is None:
                break
            signal_value = basket_signal(daily_df, codes, signal_date)
            if not math.isnan(signal_value):
                signal_values.append(signal_value)
    return signal_values


def choose_reversion_entry_date(
    codes: list[str],
    immediate_date: pd.Timestamp,
    forced_date: pd.Timestamp,
    threshold: float,
    daily_df: pd.DataFrame,
    trade_dates: list[pd.Timestamp],
) -> tuple[pd.Timestamp, float, int]:
    start_idx = trade_dates.index(immediate_date)
    end_idx = trade_dates.index(forced_date)
    for idx in range(start_idx, end_idx + 1):
        signal_date = pd.Timestamp(trade_dates[idx])
        signal_value = basket_signal(daily_df, codes, signal_date)
        if not math.isnan(signal_value) and signal_value <= threshold:
            return signal_date, signal_value, idx - start_idx
    forced_signal = basket_signal(daily_df, codes, forced_date)
    return forced_date, forced_signal, end_idx - start_idx


def summarize_strategy(
    window_df: pd.DataFrame,
    return_col: str,
    delay_col: str,
    cash_col: str,
) -> dict[str, object]:
    sample = window_df.copy()
    sample[return_col] = pd.to_numeric(sample[return_col], errors="coerce")
    sample = sample.dropna(subset=[return_col]).copy()
    if sample.empty:
        return {
            "period_count": 0,
            "cum_return": math.nan,
            "mean_return": math.nan,
            "max_drawdown": math.nan,
            "positive_period_ratio": math.nan,
            "mean_delay_days": math.nan,
            "mean_cash_days": math.nan,
        }
    return {
        "period_count": int(len(sample)),
        "cum_return": float((1.0 + sample[return_col]).prod() - 1.0),
        "mean_return": float(sample[return_col].mean()),
        "max_drawdown": compute_drawdown(sample[return_col]),
        "positive_period_ratio": float((sample[return_col] > 0).mean()),
        "mean_delay_days": float(pd.to_numeric(sample[delay_col], errors="coerce").mean()),
        "mean_cash_days": float(pd.to_numeric(sample[cash_col], errors="coerce").mean()),
    }


def build_detail_rows() -> list[dict[str, object]]:
    panel_df = load_panel()
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)

    daily_df = load_daily_panel()
    trade_dates = get_trade_dates(daily_df)

    detail_rows: list[dict[str, object]] = []
    previous_base_core_names: set[str] = set()

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        test_start = pd.Timestamp(fold["test_start"])
        review_start = pd.Timestamp(fold["review_start"])
        review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)
        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

        selected_rows, _, previous_base_core_names = select_factor_rows(
            panel_df,
            universe_rows,
            fold,
            previous_base_core_names,
        )
        scenario_map = build_scenario_rows(selected_rows, base_rows, enhanced_rows)
        scenario_rows = scenario_map.get(TARGET_SCENARIO, [])
        if not scenario_rows:
            continue

        scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, scenario_rows, train_mask)
        scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)

        train_holdings = build_window_holdings(scored_df, scored_df, train_start, test_start)
        train_signal_values = collect_train_signal_values(train_holdings, daily_df, trade_dates)
        if not train_signal_values:
            continue
        reversion_threshold = float(pd.Series(train_signal_values).quantile(REV_SIGNAL_QUANTILE))

        window_specs = [
            ("test", test_start, review_start),
            ("review", review_start, review_end),
        ]
        for window_label, window_start, window_end in window_specs:
            holdings_rows = build_window_holdings(scored_df, scored_df, window_start, window_end)
            for holding_row in holdings_rows:
                rebalance_date = pd.Timestamp(holding_row["rebalance_date"])
                next_rebalance_date = pd.Timestamp(holding_row["next_rebalance_date"]) if pd.notna(
                    holding_row["next_rebalance_date"]
                ) else pd.NaT
                if pd.isna(next_rebalance_date):
                    continue
                codes = list(holding_row["selected_codes"])

                immediate_date = first_trade_on_or_after(trade_dates, rebalance_date)
                forced_date = nth_trade_on_or_after(trade_dates, rebalance_date, SEARCH_TRADING_DAYS - 1)
                sell_date = first_trade_on_or_after(trade_dates, next_rebalance_date)
                if immediate_date is None or forced_date is None or sell_date is None:
                    continue
                if forced_date >= sell_date:
                    continue

                full_return = basket_return(daily_df, codes, immediate_date, sell_date)
                immediate_half_return = basket_return(daily_df, codes, immediate_date, sell_date)
                time_half_return = basket_return(daily_df, codes, forced_date, sell_date)

                reversion_date, reversion_signal_value, reversion_delay_days = choose_reversion_entry_date(
                    codes,
                    immediate_date,
                    forced_date,
                    reversion_threshold,
                    daily_df,
                    trade_dates,
                )
                reversion_half_return = basket_return(daily_df, codes, reversion_date, sell_date)

                split_time_return = math.nan
                if not math.isnan(immediate_half_return) and not math.isnan(time_half_return):
                    split_time_return = IMMEDIATE_WEIGHT * immediate_half_return + DELAYED_WEIGHT * time_half_return

                split_reversion_return = math.nan
                if not math.isnan(immediate_half_return) and not math.isnan(reversion_half_return):
                    split_reversion_return = (
                        IMMEDIATE_WEIGHT * immediate_half_return + DELAYED_WEIGHT * reversion_half_return
                    )

                time_delay_days = int((forced_date - immediate_date).days)
                baseline_cash_days_proxy = 0.0
                time_cash_days_proxy = DELAYED_WEIGHT * time_delay_days
                reversion_cash_days_proxy = DELAYED_WEIGHT * reversion_delay_days

                detail_rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "window_label": window_label,
                        "rebalance_date": rebalance_date.strftime("%Y-%m-%d"),
                        "next_rebalance_date": next_rebalance_date.strftime("%Y-%m-%d"),
                        "selected_count": int(holding_row["selected_count"]),
                        "selected_codes": "|".join(codes),
                        "reversion_threshold": round(reversion_threshold, 6),
                        "immediate_date": immediate_date.strftime("%Y-%m-%d"),
                        "forced_date": forced_date.strftime("%Y-%m-%d"),
                        "sell_date": sell_date.strftime("%Y-%m-%d"),
                        "reversion_date": reversion_date.strftime("%Y-%m-%d"),
                        "reversion_signal_value": round(reversion_signal_value, 6)
                        if not math.isnan(reversion_signal_value)
                        else math.nan,
                        "baseline_delay_days": 0,
                        "baseline_cash_days_proxy": baseline_cash_days_proxy,
                        "time_delay_days": time_delay_days,
                        "time_cash_days_proxy": round(time_cash_days_proxy, 6),
                        "reversion_delay_days": reversion_delay_days,
                        "reversion_cash_days_proxy": round(reversion_cash_days_proxy, 6),
                        "baseline_full_entry_return": round(full_return, 6) if not math.isnan(full_return) else math.nan,
                        "split_50_50_time_return": round(split_time_return, 6)
                        if not math.isnan(split_time_return)
                        else math.nan,
                        "split_50_50_reversion_return": round(split_reversion_return, 6)
                        if not math.isnan(split_reversion_return)
                        else math.nan,
                    }
                )
    return detail_rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_summary_rows(detail_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not detail_rows:
        return []
    detail_df = pd.DataFrame(detail_rows)
    strategy_cols = {
        "baseline_full_entry": {
            "return_col": "baseline_full_entry_return",
            "delay_col": "baseline_delay_days",
            "cash_col": "baseline_cash_days_proxy",
        },
        "split_50_50_time": {
            "return_col": "split_50_50_time_return",
            "delay_col": "time_delay_days",
            "cash_col": "time_cash_days_proxy",
        },
        "split_50_50_reversion": {
            "return_col": "split_50_50_reversion_return",
            "delay_col": "reversion_delay_days",
            "cash_col": "reversion_cash_days_proxy",
        },
    }
    rows: list[dict[str, object]] = []
    for window_label in ["test", "review", "all"]:
        window_df = detail_df.copy() if window_label == "all" else detail_df[detail_df["window_label"] == window_label].copy()
        for strategy_name, spec in strategy_cols.items():
            stats = summarize_strategy(window_df, spec["return_col"], spec["delay_col"], spec["cash_col"])
            rows.append(
                {
                    "window_label": window_label,
                    "strategy_name": strategy_name,
                    "period_count": stats["period_count"],
                    "cum_return": round(stats["cum_return"], 6) if not math.isnan(stats["cum_return"]) else math.nan,
                    "mean_return": round(stats["mean_return"], 6) if not math.isnan(stats["mean_return"]) else math.nan,
                    "max_drawdown": round(stats["max_drawdown"], 6)
                    if not math.isnan(stats["max_drawdown"])
                    else math.nan,
                    "positive_period_ratio": round(stats["positive_period_ratio"], 6)
                    if not math.isnan(stats["positive_period_ratio"])
                    else math.nan,
                    "mean_delay_days": round(stats["mean_delay_days"], 6)
                    if not math.isnan(stats["mean_delay_days"])
                    else math.nan,
                    "mean_cash_days": round(stats["mean_cash_days"], 6)
                    if not math.isnan(stats["mean_cash_days"])
                    else math.nan,
                }
            )
    return rows


def write_note(detail_rows: list[dict[str, object]], summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Fundamental Mean Reversion Entry Rolling Validation V1",
        "",
        "Objective:",
        "- keep the current primary fundamental stock-selection line unchanged",
        "- test whether mean reversion should only change post-rebalance entry speed",
        "- keep the evaluation causal by using a train-window signal threshold",
        "",
        "Frozen setup:",
        f"- scenario: `{TARGET_SCENARIO}`",
        f"- combo: `{TARGET_COMBO}`",
        f"- hold bucket: `{HOLD_BUCKET}` of `{GROUP_COUNT}`",
        f"- reversion signal: pool-average `rev5_abnvol`",
        f"- trigger threshold: train-window `{int(REV_SIGNAL_QUANTILE * 100)}`th percentile",
        f"- search window: `{SEARCH_TRADING_DAYS}` trading days after each rebalance date",
        "",
        "Compared entry styles:",
        "- `baseline_full_entry`: buy the full basket on the first tradable day",
        "- `split_50_50_time`: buy `50%` immediately and force the other `50%` at day 20",
        "- `split_50_50_reversion`: buy `50%` immediately and trigger the other `50%` when the signal crosses the train threshold, otherwise force at day 20",
        "",
        "Summary:",
    ]
    summary_df = pd.DataFrame(summary_rows)
    if summary_df.empty:
        lines.append("- no valid rows")
    else:
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['window_label']}` `{row['strategy_name']}` | periods=`{row['period_count']}` | "
                f"cum_return=`{row['cum_return']}` | mean_return=`{row['mean_return']}` | "
                f"max_drawdown=`{row['max_drawdown']}` | positive_ratio=`{row['positive_period_ratio']}` | "
                f"mean_delay_days=`{row['mean_delay_days']}` | mean_cash_days=`{row['mean_cash_days']}`"
            )
    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_DETAIL_PATH.name}]({OUTPUT_DETAIL_PATH})",
            f"- [{OUTPUT_SUMMARY_PATH.name}]({OUTPUT_SUMMARY_PATH})",
        ]
    )
    OUTPUT_NOTE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    detail_rows = build_detail_rows()
    summary_rows = build_summary_rows(detail_rows)
    write_csv(OUTPUT_DETAIL_PATH, detail_rows)
    write_csv(OUTPUT_SUMMARY_PATH, summary_rows)
    write_note(detail_rows, summary_rows)
    print(OUTPUT_DETAIL_PATH)
    print(OUTPUT_SUMMARY_PATH)
    print(OUTPUT_NOTE_PATH)


if __name__ == "__main__":
    main()
