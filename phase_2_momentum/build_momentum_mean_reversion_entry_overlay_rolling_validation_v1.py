from __future__ import annotations

import csv
import math
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
MONTHLY_PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
FOLDS_PATH = SCRIPT_DIR / "momentum_monthly_rolling_validation_v2_folds.csv"
DAILY_PANEL_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"

OUTPUT_DETAIL_PATH = SCRIPT_DIR / "momentum_mean_reversion_entry_overlay_rolling_validation_v1_detail.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "momentum_mean_reversion_entry_overlay_rolling_validation_v1_summary.csv"
OUTPUT_NOTE_PATH = SCRIPT_DIR / "momentum_mean_reversion_entry_overlay_rolling_validation_v1.md"

MOMENTUM_COL = "mom_12_1"
MONTHLY_POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_RETURN_COL = "y_month_total_return_close"
HOLD_COUNT = 6
SEARCH_TRADING_DAYS = 20
IMMEDIATE_WEIGHT = 0.5
DELAYED_WEIGHT = 0.5

THRESHOLD_QUANTILES = [0.20, 0.30, 0.40]
SIGNAL_SPECS = {
    "rev5_abnvol": {"signal_col": "rev5_abnvol", "lower_is_better": True},
    "rev_5d": {"signal_col": "rev_5d", "lower_is_better": True},
}


def load_monthly_panel() -> pd.DataFrame:
    df = pd.read_csv(MONTHLY_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["next_rebalance_date"] = pd.to_datetime(df["next_rebalance_date"])
    df = df[df[MONTHLY_POOL_FLAG] == 1].copy()
    for col in [MOMENTUM_COL, TARGET_RETURN_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[
        [
            "rebalance_date",
            "next_rebalance_date",
            "code",
            MOMENTUM_COL,
            TARGET_RETURN_COL,
        ]
    ].copy()


def load_folds() -> list[dict[str, object]]:
    df = pd.read_csv(FOLDS_PATH, encoding="utf-8-sig")
    for col in [
        "train_start",
        "train_end",
        "validation_start",
        "validation_end",
        "review_start",
        "review_end",
    ]:
        df[col] = pd.to_datetime(df[col])
    return df.to_dict("records")


def load_daily_panel() -> pd.DataFrame:
    usecols = ["date", "code", "close", "rev_5d", "abnormal_volume_ratio", "mean_reversion_ready_v1"]
    df = pd.read_csv(DAILY_PANEL_PATH, usecols=usecols, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    for col in ["close", "rev_5d", "abnormal_volume_ratio", "mean_reversion_ready_v1"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["rev5_abnvol"] = -0.7 * df["rev_5d"] + 0.3 * df["abnormal_volume_ratio"]
    return df.sort_values(["date", "code"]).reset_index(drop=True)


def build_daily_lookup(daily_df: pd.DataFrame) -> dict[str, object]:
    close_pivot = daily_df.pivot(index="date", columns="code", values="close").sort_index()
    ready_df = daily_df[daily_df["mean_reversion_ready_v1"] == 1].copy()
    signal_pivots = {
        "rev_5d": ready_df.pivot(index="date", columns="code", values="rev_5d").sort_index(),
        "rev5_abnvol": ready_df.pivot(index="date", columns="code", values="rev5_abnvol").sort_index(),
    }
    return {
        "close_pivot": close_pivot,
        "signal_pivots": signal_pivots,
    }


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


def preprocess_momentum_factor(full_df: pd.DataFrame, train_mask: pd.Series) -> pd.Series:
    values = pd.to_numeric(full_df[MOMENTUM_COL], errors="coerce")
    train_values = values[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=full_df.index, dtype="float64")
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = values.clip(lower=lower, upper=upper)
    train_clipped = clipped[train_mask].dropna()
    mean_value = float(train_clipped.mean())
    std_value = float(train_clipped.std(ddof=0))
    if pd.isna(std_value) or std_value <= 1e-12:
        return pd.Series(index=full_df.index, dtype="float64")
    return (clipped - mean_value) / std_value


def select_top_n(group: pd.DataFrame, score_col: str, top_n: int) -> pd.DataFrame:
    work = group.dropna(subset=[score_col]).sort_values([score_col, "code"], ascending=[False, True]).copy()
    return work.head(int(top_n)).copy()


def build_window_holdings(
    scored_df: pd.DataFrame,
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    window_df = scored_df[(scored_df["rebalance_date"] >= window_start) & (scored_df["rebalance_date"] <= window_end)].copy()
    rebalance_dates = sorted(pd.to_datetime(window_df["rebalance_date"].drop_duplicates()).tolist())
    for rebalance_date in rebalance_dates:
        group = window_df[window_df["rebalance_date"] == rebalance_date].copy()
        picked = select_top_n(group, "score__mom12", HOLD_COUNT)
        if len(picked) < HOLD_COUNT:
            continue
        next_rebalance_date = pd.to_datetime(picked["next_rebalance_date"].dropna()).min()
        if pd.isna(next_rebalance_date):
            continue
        rows.append(
            {
                "rebalance_date": pd.Timestamp(rebalance_date),
                "next_rebalance_date": pd.Timestamp(next_rebalance_date),
                "selected_codes": sorted(picked["code"].astype(str).tolist()),
                "selected_count": int(len(picked)),
            }
        )
    return rows


def basket_signal(
    daily_lookup: dict[str, object],
    codes: list[str],
    signal_date: pd.Timestamp,
    signal_col: str,
) -> float:
    signal_pivot = daily_lookup["signal_pivots"][signal_col]
    if signal_date not in signal_pivot.index:
        return math.nan
    values = pd.to_numeric(signal_pivot.reindex(columns=codes).loc[signal_date], errors="coerce").dropna()
    if values.empty:
        return math.nan
    return float(values.mean())


def basket_return(
    daily_lookup: dict[str, object],
    codes: list[str],
    buy_date: pd.Timestamp,
    sell_date: pd.Timestamp,
) -> float:
    close_pivot = daily_lookup["close_pivot"]
    if buy_date not in close_pivot.index or sell_date not in close_pivot.index:
        return math.nan
    buy = pd.to_numeric(close_pivot.reindex(columns=codes).loc[buy_date], errors="coerce")
    sell = pd.to_numeric(close_pivot.reindex(columns=codes).loc[sell_date], errors="coerce")
    merged = pd.DataFrame({"buy": buy, "sell": sell}).dropna()
    if merged.empty:
        return math.nan
    merged["ret"] = merged["sell"] / merged["buy"] - 1.0
    return float(merged["ret"].mean())


def collect_train_signal_values(
    holdings_rows: list[dict[str, object]],
    daily_lookup: dict[str, object],
    trade_dates: list[pd.Timestamp],
    signal_col: str,
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
            signal_value = basket_signal(daily_lookup, codes, signal_date, signal_col)
            if not math.isnan(signal_value):
                signal_values.append(signal_value)
    return signal_values


def choose_reversion_entry_date(
    codes: list[str],
    immediate_date: pd.Timestamp,
    forced_date: pd.Timestamp,
    threshold: float,
    daily_lookup: dict[str, object],
    trade_dates: list[pd.Timestamp],
    signal_col: str,
    lower_is_better: bool,
) -> tuple[pd.Timestamp, float, int]:
    start_idx = trade_dates.index(immediate_date)
    end_idx = trade_dates.index(forced_date)
    for idx in range(start_idx, end_idx + 1):
        signal_date = pd.Timestamp(trade_dates[idx])
        signal_value = basket_signal(daily_lookup, codes, signal_date, signal_col)
        if math.isnan(signal_value):
            continue
        if lower_is_better and signal_value <= threshold:
            return signal_date, signal_value, idx - start_idx
        if (not lower_is_better) and signal_value >= threshold:
            return signal_date, signal_value, idx - start_idx
    forced_signal = basket_signal(daily_lookup, codes, forced_date, signal_col)
    return forced_date, forced_signal, end_idx - start_idx


def compute_drawdown(return_series: pd.Series) -> float:
    sample = pd.to_numeric(return_series, errors="coerce").dropna()
    if sample.empty:
        return math.nan
    equity = (1.0 + sample).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return float(drawdown.min())


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
    monthly_df = load_monthly_panel()
    folds = load_folds()
    daily_df = load_daily_panel()
    daily_lookup = build_daily_lookup(daily_df)
    trade_dates = get_trade_dates(daily_df)

    detail_rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        train_end = pd.Timestamp(fold["train_end"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])
        review_start = pd.Timestamp(fold["review_start"])
        review_end = pd.Timestamp(fold["review_end"])

        train_mask = (monthly_df["rebalance_date"] >= train_start) & (monthly_df["rebalance_date"] <= train_end)
        scored_df = monthly_df.copy()
        scored_df["score__mom12"] = preprocess_momentum_factor(scored_df, train_mask)

        train_holdings = build_window_holdings(scored_df, train_start, train_end)
        if not train_holdings:
            continue

        threshold_map: dict[tuple[str, float], float] = {}
        for signal_name, spec in SIGNAL_SPECS.items():
            train_signal_values = collect_train_signal_values(
                train_holdings,
                daily_lookup,
                trade_dates,
                spec["signal_col"],
            )
            if not train_signal_values:
                continue
            train_signal_series = pd.Series(train_signal_values)
            for threshold_quantile in THRESHOLD_QUANTILES:
                threshold_map[(signal_name, threshold_quantile)] = float(train_signal_series.quantile(threshold_quantile))

        if not threshold_map:
            continue

        window_specs = [
            ("validation", validation_start, validation_end),
            ("review", review_start, review_end),
        ]
        for window_label, window_start, window_end in window_specs:
            holdings_rows = build_window_holdings(scored_df, window_start, window_end)
            for holding_row in holdings_rows:
                rebalance_date = pd.Timestamp(holding_row["rebalance_date"])
                next_rebalance_date = pd.Timestamp(holding_row["next_rebalance_date"])
                codes = list(holding_row["selected_codes"])

                immediate_date = first_trade_on_or_after(trade_dates, rebalance_date)
                forced_date = nth_trade_on_or_after(trade_dates, rebalance_date, SEARCH_TRADING_DAYS - 1)
                sell_date = first_trade_on_or_after(trade_dates, next_rebalance_date)
                if immediate_date is None or forced_date is None or sell_date is None:
                    continue
                if forced_date >= sell_date:
                    continue

                full_return = basket_return(daily_lookup, codes, immediate_date, sell_date)
                immediate_half_return = basket_return(daily_lookup, codes, immediate_date, sell_date)
                time_half_return = basket_return(daily_lookup, codes, forced_date, sell_date)

                split_time_return = math.nan
                if not math.isnan(immediate_half_return) and not math.isnan(time_half_return):
                    split_time_return = IMMEDIATE_WEIGHT * immediate_half_return + DELAYED_WEIGHT * time_half_return

                time_delay_days = int((forced_date - immediate_date).days)
                baseline_cash_days_proxy = 0.0
                time_cash_days_proxy = DELAYED_WEIGHT * time_delay_days

                for signal_name, spec in SIGNAL_SPECS.items():
                    for threshold_quantile in THRESHOLD_QUANTILES:
                        threshold_key = (signal_name, threshold_quantile)
                        if threshold_key not in threshold_map:
                            continue
                        threshold_value = threshold_map[threshold_key]
                        reversion_date, signal_value, reversion_delay_days = choose_reversion_entry_date(
                            codes,
                            immediate_date,
                            forced_date,
                            threshold_value,
                            daily_lookup,
                            trade_dates,
                            spec["signal_col"],
                            spec["lower_is_better"],
                        )
                        reversion_half_return = basket_return(daily_lookup, codes, reversion_date, sell_date)
                        split_reversion_return = math.nan
                        if not math.isnan(immediate_half_return) and not math.isnan(reversion_half_return):
                            split_reversion_return = (
                                IMMEDIATE_WEIGHT * immediate_half_return + DELAYED_WEIGHT * reversion_half_return
                            )

                        detail_rows.append(
                            {
                                "fold_id": fold["fold_id"],
                                "window_label": window_label,
                                "base_strategy": "direct_mom12_top6",
                                "signal_name": signal_name,
                                "threshold_quantile": threshold_quantile,
                                "rebalance_date": rebalance_date.strftime("%Y-%m-%d"),
                                "next_rebalance_date": next_rebalance_date.strftime("%Y-%m-%d"),
                                "selected_count": int(holding_row["selected_count"]),
                                "selected_codes": "|".join(codes),
                                "signal_threshold": round(threshold_value, 6),
                                "immediate_date": immediate_date.strftime("%Y-%m-%d"),
                                "forced_date": forced_date.strftime("%Y-%m-%d"),
                                "sell_date": sell_date.strftime("%Y-%m-%d"),
                                "reversion_date": reversion_date.strftime("%Y-%m-%d"),
                                "signal_value": round(signal_value, 6) if not math.isnan(signal_value) else math.nan,
                                "baseline_delay_days": 0,
                                "baseline_cash_days_proxy": baseline_cash_days_proxy,
                                "time_delay_days": time_delay_days,
                                "time_cash_days_proxy": round(time_cash_days_proxy, 6),
                                "reversion_delay_days": reversion_delay_days,
                                "reversion_cash_days_proxy": round(DELAYED_WEIGHT * reversion_delay_days, 6),
                                "baseline_full_entry_return": round(full_return, 6) if not math.isnan(full_return) else math.nan,
                                "split_50_50_time_return": round(split_time_return, 6) if not math.isnan(split_time_return) else math.nan,
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
    strategy_specs = {
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
    group_keys = [
        ("validation", ["validation"]),
        ("review", ["review"]),
        ("all", ["validation", "review"]),
    ]
    for signal_name in SIGNAL_SPECS:
        for threshold_quantile in THRESHOLD_QUANTILES:
            subset = detail_df[
                (detail_df["signal_name"] == signal_name)
                & (pd.to_numeric(detail_df["threshold_quantile"], errors="coerce") == threshold_quantile)
            ].copy()
            if subset.empty:
                continue
            for window_label, source_windows in group_keys:
                window_df = subset[subset["window_label"].isin(source_windows)].copy()
                for strategy_name, spec in strategy_specs.items():
                    stats = summarize_strategy(window_df, spec["return_col"], spec["delay_col"], spec["cash_col"])
                    rows.append(
                        {
                            "base_strategy": "direct_mom12_top6",
                            "signal_name": signal_name,
                            "threshold_quantile": threshold_quantile,
                            "window_label": window_label,
                            "strategy_name": strategy_name,
                            "period_count": stats["period_count"],
                            "cum_return": round(stats["cum_return"], 6) if not math.isnan(stats["cum_return"]) else math.nan,
                            "mean_return": round(stats["mean_return"], 6) if not math.isnan(stats["mean_return"]) else math.nan,
                            "max_drawdown": round(stats["max_drawdown"], 6) if not math.isnan(stats["max_drawdown"]) else math.nan,
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


def write_note(summary_rows: list[dict[str, object]], detail_rows: list[dict[str, object]], fold_count: int) -> None:
    lines = [
        "# Momentum Mean Reversion Entry Overlay Rolling Validation V1",
        "",
        "Objective:",
        "- keep the momentum main line fixed as `direct_mom12_top6`",
        "- test whether mean reversion works better as entry timing than as a separate stock-selection layer",
        "- use only train-window information to freeze trigger thresholds inside each fold",
        "",
        "Frozen setup:",
        f"- base strategy: `direct_mom12_top6`",
        f"- folds: `{fold_count}` monthly rolling folds from the momentum main-line framework",
        f"- hold count: `{HOLD_COUNT}`",
        f"- search window: `{SEARCH_TRADING_DAYS}` trading days after each rebalance date",
        f"- signal grid: `{', '.join(SIGNAL_SPECS.keys())}`",
        f"- threshold grid: `{', '.join(str(int(q * 100)) + '%' for q in THRESHOLD_QUANTILES)}`",
        "- strategy comparison = `baseline_full_entry` vs `split_50_50_time` vs `split_50_50_reversion`",
        "",
        f"- evaluated snapshots: `{len(detail_rows)}` raw strategy rows",
        "",
        "Review summary:",
    ]

    summary_df = pd.DataFrame(summary_rows)
    if summary_df.empty:
        lines.append("- no valid rows")
    else:
        review_df = summary_df[summary_df["window_label"] == "review"].copy()
        review_df["cum_return"] = pd.to_numeric(review_df["cum_return"], errors="coerce")
        review_df["mean_return"] = pd.to_numeric(review_df["mean_return"], errors="coerce")
        review_df["max_drawdown"] = pd.to_numeric(review_df["max_drawdown"], errors="coerce")
        review_df = review_df.sort_values(
            ["strategy_name", "cum_return", "mean_return", "max_drawdown"],
            ascending=[True, False, False, False],
        )
        for _, row in review_df.iterrows():
            lines.append(
                f"- `{row['signal_name']}` q=`{int(float(row['threshold_quantile']) * 100)}%` `{row['strategy_name']}` | "
                f"periods=`{row['period_count']}` | cum_return=`{row['cum_return']}` | "
                f"mean_return=`{row['mean_return']}` | max_drawdown=`{row['max_drawdown']}` | "
                f"positive_ratio=`{row['positive_period_ratio']}` | mean_delay_days=`{row['mean_delay_days']}`"
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
    folds = load_folds()
    detail_rows = build_detail_rows()
    summary_rows = build_summary_rows(detail_rows)
    write_csv(OUTPUT_DETAIL_PATH, detail_rows)
    write_csv(OUTPUT_SUMMARY_PATH, summary_rows)
    write_note(summary_rows, detail_rows, len(folds))
    print(OUTPUT_DETAIL_PATH)
    print(OUTPUT_SUMMARY_PATH)
    print(OUTPUT_NOTE_PATH)


if __name__ == "__main__":
    main()
