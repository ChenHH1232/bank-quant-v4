from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
MONTHLY_PANEL_PATH = SCRIPT_DIR / "mean_reversion_monthly_rebalance_panel_v1.csv"
DAILY_PANEL_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"
FOLDS_PATH = SCRIPT_DIR / "momentum_monthly_rolling_validation_v2_folds.csv"
ETF_CACHE_PATH = SCRIPT_DIR / "raw_downloads" / "benchmark_512800_sina_daily.csv"
RESULTS_PATH = SCRIPT_DIR / "sector_relative_mean_reversion_rolling_validation_v4_results.csv"
SUMMARY_PATH = SCRIPT_DIR / "sector_relative_mean_reversion_rolling_validation_v4.md"

ETF_SYMBOL = "sh512800"
TARGET_COL = "y_month_total_return_close"
READY_FLAG = "mean_reversion_ready_v1"
MIN_NAMES_PER_DATE = 5
BOLL_K = 2.0

FACTOR_SPECS = [
    {"factor_name": "ratio_z_10d", "label": "price ratio zscore 10d"},
    {"factor_name": "ratio_z_20d", "label": "price ratio zscore 20d"},
    {"factor_name": "ratio_z_40d", "label": "price ratio zscore 40d"},
    {"factor_name": "ratio_below_lower_10d", "label": "below lower bollinger 10d"},
    {"factor_name": "ratio_below_lower_20d", "label": "below lower bollinger 20d"},
    {"factor_name": "ratio_below_lower_40d", "label": "below lower bollinger 40d"},
]


def load_monthly_panel() -> pd.DataFrame:
    df = pd.read_csv(MONTHLY_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    for col in [READY_FLAG, TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df[READY_FLAG] == 1].copy()
    df = df.dropna(subset=[TARGET_COL]).copy()
    return df.sort_values(["rebalance_date", "code"]).reset_index(drop=True)


def load_daily_panel() -> pd.DataFrame:
    df = pd.read_csv(DAILY_PANEL_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    for col in [READY_FLAG, "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df[READY_FLAG] == 1].copy()
    df = df.dropna(subset=["close"]).copy()
    return df.sort_values(["date", "code"]).reset_index(drop=True)


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


def load_etf_history() -> pd.DataFrame:
    if ETF_CACHE_PATH.exists():
        df = pd.read_csv(ETF_CACHE_PATH, encoding="utf-8-sig")
    else:
        import akshare as ak

        df = ak.fund_etf_hist_sina(symbol=ETF_SYMBOL)
        ETF_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(ETF_CACHE_PATH, index=False, encoding="utf-8-sig")

    df["date"] = pd.to_datetime(df["date"])
    for col in ["open", "high", "low", "close", "volume", "amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("date").reset_index(drop=True)


def build_ratio_feature_panel(daily_df: pd.DataFrame, etf_df: pd.DataFrame) -> pd.DataFrame:
    merged = daily_df.merge(etf_df[["date", "close"]].rename(columns={"close": "etf_close"}), on="date", how="left")
    merged["ratio_close"] = pd.to_numeric(merged["close"], errors="coerce") / pd.to_numeric(merged["etf_close"], errors="coerce")
    merged.loc[(merged["etf_close"].abs() <= 1e-12) | merged["etf_close"].isna(), "ratio_close"] = np.nan

    result_parts: list[pd.DataFrame] = []
    for _, group in merged.groupby("code", sort=False):
        one = group.sort_values("date").copy()
        for lookback in [10, 20, 40]:
            mean_value = one["ratio_close"].rolling(lookback, min_periods=lookback).mean()
            std_value = one["ratio_close"].rolling(lookback, min_periods=lookback).std(ddof=0)
            z_col = f"ratio_z_{lookback}d"
            lower_col = f"ratio_below_lower_{lookback}d"
            one[z_col] = (one["ratio_close"] - mean_value) / std_value
            one.loc[(std_value.abs() <= 1e-12) | std_value.isna(), z_col] = np.nan

            lower_band = mean_value - BOLL_K * std_value
            lower_gap = one["ratio_close"] / lower_band - 1.0
            lower_gap[(lower_band.abs() <= 1e-12) | lower_band.isna()] = np.nan
            one[lower_col] = np.minimum(lower_gap, 0.0)
        result_parts.append(
            one[
                [
                    "date",
                    "code",
                    "ratio_z_10d",
                    "ratio_z_20d",
                    "ratio_z_40d",
                    "ratio_below_lower_10d",
                    "ratio_below_lower_20d",
                    "ratio_below_lower_40d",
                ]
            ]
        )
    return pd.concat(result_parts, ignore_index=True).sort_values(["date", "code"]).reset_index(drop=True)


def attach_ratio_features(monthly_df: pd.DataFrame, ratio_df: pd.DataFrame) -> pd.DataFrame:
    merged = monthly_df.merge(
        ratio_df,
        left_on=["rebalance_date", "code"],
        right_on=["date", "code"],
        how="left",
    )
    merged = merged.drop(columns=["date"])
    return merged.sort_values(["rebalance_date", "code"]).reset_index(drop=True)


def winsorize(series: pd.Series, lower: float, upper: float) -> pd.Series:
    return series.clip(lower=lower, upper=upper)


def zscore(series: pd.Series, mean_value: float, std_value: float) -> pd.Series:
    if std_value <= 0 or math.isnan(std_value):
        return series * np.nan
    return (series - mean_value) / std_value


def preprocess_factor(full_df: pd.DataFrame, train_mask: pd.Series, factor_name: str) -> pd.Series:
    values = pd.to_numeric(full_df[factor_name], errors="coerce")
    train_values = values[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=full_df.index, dtype="float64")
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = winsorize(values, lower, upper)
    train_clipped = clipped[train_mask].dropna()
    mean_value = float(train_clipped.mean())
    std_value = float(train_clipped.std(ddof=0))
    return zscore(clipped, mean_value, std_value)


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def compute_rank_ic(x: pd.Series, y: pd.Series) -> float:
    rx = x.rank(method="average")
    ry = y.rank(method="average")
    value = rx.corr(ry, method="pearson")
    return float(value) if not pd.isna(value) else np.nan


def compute_window_metrics(window_df: pd.DataFrame, score_col: str, direction: str | None = None) -> dict[str, object]:
    sample_df = window_df[["rebalance_date", score_col, TARGET_COL]].copy()
    total_rows = len(sample_df)
    sample_df[score_col] = pd.to_numeric(sample_df[score_col], errors="coerce")
    sample_df[TARGET_COL] = pd.to_numeric(sample_df[TARGET_COL], errors="coerce")
    sample_df = sample_df.dropna(subset=[score_col, TARGET_COL])
    missing_ratio = 1.0 if total_rows == 0 else 1.0 - (len(sample_df) / total_rows)
    usable_dates = sample_df["rebalance_date"].nunique()
    usable_rows = len(sample_df)

    by_date = []
    for rebalance_date, group in sample_df.groupby("rebalance_date"):
        if len(group) < MIN_NAMES_PER_DATE:
            continue
        ic = compute_rank_ic(group[score_col], group[TARGET_COL])
        if pd.isna(ic):
            continue
        by_date.append({"rebalance_date": rebalance_date, "rank_ic": float(ic), "group": group})

    if not by_date:
        return {
            "usable_rows": usable_rows,
            "usable_dates": usable_dates,
            "missing_ratio": missing_ratio,
            "rank_ic_mean": np.nan,
            "rank_ic_ir": np.nan,
            "positive_ic_ratio": np.nan,
            "top_minus_bottom": np.nan,
            "direction": direction or "larger_better",
        }

    ic_values = np.array([item["rank_ic"] for item in by_date], dtype=float)
    ic_mean_raw = float(ic_values.mean())
    ic_std_raw = float(ic_values.std(ddof=0))
    ic_ir_raw = float(ic_mean_raw / ic_std_raw) if ic_std_raw > 0 else np.nan
    pos_raw = float((ic_values > 0).mean())
    if direction is None:
        direction = "larger_better" if ic_mean_raw >= 0 else "smaller_better"
    mult = 1.0 if direction == "larger_better" else -1.0

    spreads: list[float] = []
    for item in by_date:
        group = item["group"].copy()
        group["_bucket"] = assign_groups(group[score_col], 5)
        group = group.dropna(subset=["_bucket"])
        bucket_means = group.groupby("_bucket")[TARGET_COL].mean().to_dict()
        if 1 in bucket_means and 5 in bucket_means:
            spreads.append(float(bucket_means[5] - bucket_means[1]) * mult)

    return {
        "usable_rows": usable_rows,
        "usable_dates": usable_dates,
        "missing_ratio": missing_ratio,
        "rank_ic_mean": ic_mean_raw * mult,
        "rank_ic_ir": ic_ir_raw * mult if not pd.isna(ic_ir_raw) else np.nan,
        "positive_ic_ratio": pos_raw if mult > 0 else 1.0 - pos_raw,
        "top_minus_bottom": float(np.mean(spreads)) if spreads else np.nan,
        "direction": direction,
    }


def build_result_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        train_end = pd.Timestamp(fold["train_end"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])
        review_start = pd.Timestamp(fold["review_start"])
        review_end = pd.Timestamp(fold["review_end"])

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] <= train_end)
        for spec in FACTOR_SPECS:
            factor_name = spec["factor_name"]
            scored_df = panel_df.copy()
            score_col = f"score__{factor_name}"
            scored_df[score_col] = preprocess_factor(scored_df, train_mask, factor_name)

            train_metrics = compute_window_metrics(scored_df[train_mask], score_col)
            direction = str(train_metrics["direction"])

            window_specs = [
                ("train", train_start, train_end),
                ("validation", validation_start, validation_end),
                ("review", review_start, review_end),
            ]
            for window_label, window_start, window_end in window_specs:
                window_mask = (scored_df["rebalance_date"] >= window_start) & (scored_df["rebalance_date"] <= window_end)
                window_metrics = compute_window_metrics(scored_df[window_mask], score_col, direction=direction)
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "factor_name": factor_name,
                        "factor_label": spec["label"],
                        "window_label": window_label,
                        "train_start": train_start.strftime("%Y-%m-%d"),
                        "train_end": train_end.strftime("%Y-%m-%d"),
                        "window_start": window_start.strftime("%Y-%m-%d"),
                        "window_end": window_end.strftime("%Y-%m-%d"),
                        "direction": direction,
                        "usable_rows": int(window_metrics["usable_rows"]),
                        "usable_dates": int(window_metrics["usable_dates"]),
                        "missing_ratio": round(float(window_metrics["missing_ratio"]), 6)
                        if not pd.isna(window_metrics["missing_ratio"])
                        else np.nan,
                        "rank_ic_mean": round(float(window_metrics["rank_ic_mean"]), 6)
                        if not pd.isna(window_metrics["rank_ic_mean"])
                        else np.nan,
                        "rank_ic_ir": round(float(window_metrics["rank_ic_ir"]), 6)
                        if not pd.isna(window_metrics["rank_ic_ir"])
                        else np.nan,
                        "positive_ic_ratio": round(float(window_metrics["positive_ic_ratio"]), 6)
                        if not pd.isna(window_metrics["positive_ic_ratio"])
                        else np.nan,
                        "top_minus_bottom": round(float(window_metrics["top_minus_bottom"]), 6)
                        if not pd.isna(window_metrics["top_minus_bottom"])
                        else np.nan,
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(rows: list[dict[str, object]], fold_count: int, etf_df: pd.DataFrame) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# Sector Relative Mean Reversion Rolling Validation V4",
        "",
        "Purpose:",
        "- test zscore and lower-bollinger deviation on stock-vs-ETF price ratio",
        f"- sector ETF proxy = `{ETF_SYMBOL}`",
        "- ratio definition = `stock close / ETF close`",
        f"- bollinger setup = rolling mean +/- `{BOLL_K}` * rolling std",
        "",
        "Frozen setup:",
        f"- fold count: `{fold_count}` monthly rolling folds",
        f"- ETF history start: `{etf_df['date'].min().date()}`",
        f"- ETF history end: `{etf_df['date'].max().date()}`",
        f"- target: next-month return `{TARGET_COL}`",
        f"- factor set: `{', '.join(spec['factor_name'] for spec in FACTOR_SPECS)}`",
        "",
    ]

    if not df.empty:
        summary_df = (
            df[df["window_label"].isin(["validation", "review"])]
            .groupby(["factor_name", "factor_label", "window_label"], dropna=False)
            .agg(
                fold_count=("fold_id", "nunique"),
                mean_rank_ic=("rank_ic_mean", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_rank_ic_ir=("rank_ic_ir", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_positive_ic_ratio=("positive_ic_ratio", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_top_minus_bottom=("top_minus_bottom", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_missing_ratio=("missing_ratio", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["window_label", "mean_rank_ic", "mean_top_minus_bottom"], ascending=[True, False, False])
        )
        lines.append("Validation and review summary:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['factor_name']}` `{row['window_label']}` | "
                f"folds=`{int(row['fold_count'])}` | "
                f"mean_rank_ic=`{format_float(row['mean_rank_ic'])}` | "
                f"mean_rank_ic_ir=`{format_float(row['mean_rank_ic_ir'])}` | "
                f"mean_positive_ic_ratio=`{format_float(row['mean_positive_ic_ratio'])}` | "
                f"mean_top_minus_bottom=`{format_float(row['mean_top_minus_bottom'])}` | "
                f"mean_missing_ratio=`{format_float(row['mean_missing_ratio'])}`"
            )

        review_df = summary_df[summary_df["window_label"] == "review"].copy()
        if not review_df.empty:
            best = review_df.sort_values(
                ["mean_rank_ic", "mean_top_minus_bottom", "mean_positive_ic_ratio"],
                ascending=[False, False, False],
            ).iloc[0]
            lines.extend(
                [
                    "",
                    "Current best zscore/bollinger candidate:",
                    f"- `{best['factor_name']}` | review mean_rank_ic=`{format_float(best['mean_rank_ic'])}` | review mean_top_minus_bottom=`{format_float(best['mean_top_minus_bottom'])}`",
                ]
            )

    lines.extend(["", "Outputs:", f"- [{RESULTS_PATH.name}]({RESULTS_PATH})", f"- ETF cache: [{ETF_CACHE_PATH.name}]({ETF_CACHE_PATH})"])
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    monthly_df = load_monthly_panel()
    daily_df = load_daily_panel()
    etf_df = load_etf_history()
    ratio_df = build_ratio_feature_panel(daily_df, etf_df)
    enriched_df = attach_ratio_features(monthly_df, ratio_df)
    folds = load_folds()
    rows = build_result_rows(enriched_df, folds)
    write_csv(RESULTS_PATH, rows)
    write_summary(rows, len(folds), etf_df)
    print(RESULTS_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
