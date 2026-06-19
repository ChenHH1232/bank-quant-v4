from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "mean_reversion_factor_panel_v1.csv"
CALENDAR_PATH = SCRIPT_DIR / "raw_downloads" / "momentum_price_repair_v1" / "trade_calendar.csv"
MONTHLY_PANEL_PATH = SCRIPT_DIR / "mean_reversion_monthly_rebalance_panel_v1.csv"
RESULTS_PATH = SCRIPT_DIR / "mean_reversion_single_factor_test_results_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "mean_reversion_single_factor_test_results_v1.md"

TRAIN_START = pd.Timestamp("2014-01-01")
TRAIN_END = pd.Timestamp("2019-01-01")
VALIDATION_START = pd.Timestamp("2019-01-01")
VALIDATION_END = pd.Timestamp("2021-01-01")

FACTOR_SPECS = [
    {"factor_name": "rev_5d", "factor_family": "mean_reversion", "target_label": "y_month_total_return_close"},
    {"factor_name": "rev_10d", "factor_family": "mean_reversion", "target_label": "y_month_total_return_close"},
    {"factor_name": "rev_20d", "factor_family": "mean_reversion", "target_label": "y_month_total_return_close"},
    {"factor_name": "close_to_ma20", "factor_family": "mean_reversion", "target_label": "y_month_total_return_close"},
]

TRAIN_MIN_DATES = 24
VALIDATION_MIN_DATES = 12
TRAIN_MIN_ROWS = 300
VALIDATION_MIN_ROWS = 120


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_monthly_calendar() -> pd.DataFrame:
    df = pd.read_csv(CALENDAR_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["month_key"] = df["date"].dt.strftime("%Y-%m")
    out = df.groupby("month_key", as_index=False).first()[["month_key", "date"]].copy()
    out = out.rename(columns={"date": "rebalance_date"})
    return out.sort_values("rebalance_date").reset_index(drop=True)


def build_monthly_panel(daily_df: pd.DataFrame, calendar_df: pd.DataFrame) -> pd.DataFrame:
    sampled = daily_df.merge(calendar_df, left_on="date", right_on="rebalance_date", how="inner").copy()
    sampled = sampled.drop(columns=["date"]).sort_values(["code", "rebalance_date"]).reset_index(drop=True)
    sampled["next_rebalance_date"] = sampled.groupby("code")["rebalance_date"].shift(-1)
    sampled["next_rebalance_close"] = pd.to_numeric(sampled.groupby("code")["close"].shift(-1), errors="coerce")
    sampled["close"] = pd.to_numeric(sampled["close"], errors="coerce")
    sampled["y_month_total_return_close"] = sampled["next_rebalance_close"].div(sampled["close"]) - 1.0
    return sampled.sort_values(["rebalance_date", "code"]).reset_index(drop=True)


def winsorize_with_train_params(series: pd.Series, lower: float, upper: float) -> pd.Series:
    return series.clip(lower=lower, upper=upper)


def zscore_with_train_params(series: pd.Series, mean_value: float, std_value: float) -> pd.Series:
    if std_value <= 0 or math.isnan(std_value):
        return series * np.nan
    return (series - mean_value) / std_value


def preprocess_factor(train_df: pd.DataFrame, validation_df: pd.DataFrame, factor_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_values = pd.to_numeric(train_df[factor_name], errors="coerce")
    valid_values = pd.to_numeric(validation_df[factor_name], errors="coerce")

    non_null_train = train_values.dropna()
    if non_null_train.empty:
        train_df = train_df.copy()
        validation_df = validation_df.copy()
        train_df["_factor_value"] = np.nan
        validation_df["_factor_value"] = np.nan
        return train_df, validation_df

    lower = float(non_null_train.quantile(0.01))
    upper = float(non_null_train.quantile(0.99))
    clipped_train = winsorize_with_train_params(train_values, lower, upper)
    clipped_valid = winsorize_with_train_params(valid_values, lower, upper)

    mean_value = float(clipped_train.dropna().mean())
    std_value = float(clipped_train.dropna().std(ddof=0))

    train_df = train_df.copy()
    validation_df = validation_df.copy()
    train_df["_factor_value"] = zscore_with_train_params(clipped_train, mean_value, std_value)
    validation_df["_factor_value"] = zscore_with_train_params(clipped_valid, mean_value, std_value)
    return train_df, validation_df


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def compute_spearman_like_rank_ic(x: pd.Series, y: pd.Series) -> float:
    ranked_x = x.rank(method="average")
    ranked_y = y.rank(method="average")
    value = ranked_x.corr(ranked_y, method="pearson")
    return float(value) if not pd.isna(value) else np.nan


def compute_window_metrics(window_df: pd.DataFrame, factor_name: str, target_label: str, direction: str | None = None) -> dict[str, object]:
    sample_df = window_df[["rebalance_date", factor_name, target_label, "_factor_value"]].copy()
    total_rows = len(sample_df)
    sample_df[factor_name] = pd.to_numeric(sample_df[factor_name], errors="coerce")
    sample_df[target_label] = pd.to_numeric(sample_df[target_label], errors="coerce")
    sample_df = sample_df.dropna(subset=["_factor_value", target_label])

    missing_ratio = 1.0 if total_rows == 0 else 1.0 - (len(sample_df) / total_rows)
    usable_dates = sample_df["rebalance_date"].nunique()
    usable_rows = len(sample_df)

    by_date = []
    for rebalance_date, group in sample_df.groupby("rebalance_date"):
        if len(group) < 5:
            continue
        rank_ic = compute_spearman_like_rank_ic(group["_factor_value"], group[target_label])
        if pd.isna(rank_ic):
            continue
        by_date.append({"rebalance_date": rebalance_date, "rank_ic": float(rank_ic), "group": group})

    if not by_date:
        return {
            "usable_rows": usable_rows,
            "usable_dates": usable_dates,
            "missing_ratio": missing_ratio,
            "rank_ic_mean_raw": np.nan,
            "rank_ic_ir_raw": np.nan,
            "positive_ic_ratio_raw": np.nan,
            "top_minus_bottom_raw": np.nan,
            "monotonic_flag_raw": 0,
        }

    rank_ic_values = np.array([item["rank_ic"] for item in by_date], dtype=float)
    rank_ic_mean_raw = float(rank_ic_values.mean())
    rank_ic_std_raw = float(rank_ic_values.std(ddof=0))
    rank_ic_ir_raw = float(rank_ic_mean_raw / rank_ic_std_raw) if rank_ic_std_raw > 0 else np.nan
    positive_ic_ratio_raw = float((rank_ic_values > 0).mean())

    if direction is None:
        direction = "larger_better" if rank_ic_mean_raw >= 0 else "smaller_better"

    adjusted_multiplier = 1.0 if direction == "larger_better" else -1.0
    group_means_by_bucket: dict[int, list[float]] = {}
    top_minus_bottom_list: list[float] = []

    for item in by_date:
        group = item["group"].copy()
        group["_bucket"] = assign_groups(group["_factor_value"], 5)
        group = group.dropna(subset=["_bucket"])
        if group.empty:
            continue
        bucket_means = group.groupby("_bucket")[target_label].mean().to_dict()
        for bucket, value in bucket_means.items():
            group_means_by_bucket.setdefault(int(bucket), []).append(float(value))
        if 1 in bucket_means and 5 in bucket_means:
            raw_spread = float(bucket_means[5] - bucket_means[1])
            top_minus_bottom_list.append(raw_spread * adjusted_multiplier)

    averaged_buckets: list[float] = []
    for bucket in range(1, 6):
        values = group_means_by_bucket.get(bucket, [])
        averaged_buckets.append(float(np.mean(values)) if values else np.nan)

    monotonic_flag_raw = 0
    finite_buckets = [value for value in averaged_buckets if not pd.isna(value)]
    if len(finite_buckets) >= 3:
        if direction == "larger_better":
            monotonic_flag_raw = int(all(x <= y for x, y in zip(finite_buckets, finite_buckets[1:])))
        else:
            monotonic_flag_raw = int(all(x >= y for x, y in zip(finite_buckets, finite_buckets[1:])))

    return {
        "usable_rows": usable_rows,
        "usable_dates": usable_dates,
        "missing_ratio": missing_ratio,
        "rank_ic_mean_raw": rank_ic_mean_raw,
        "rank_ic_ir_raw": rank_ic_ir_raw,
        "positive_ic_ratio_raw": positive_ic_ratio_raw,
        "top_minus_bottom_raw": float(np.mean(top_minus_bottom_list)) if top_minus_bottom_list else np.nan,
        "monotonic_flag_raw": monotonic_flag_raw,
        "direction": direction,
    }


def enrich_adjusted_metrics(metrics: dict[str, object], direction: str) -> dict[str, object]:
    multiplier = 1.0 if direction == "larger_better" else -1.0
    adjusted = dict(metrics)
    adjusted["adjusted_rank_ic_mean"] = float(metrics["rank_ic_mean_raw"]) * multiplier
    raw_ir = metrics["rank_ic_ir_raw"]
    adjusted["adjusted_rank_ic_ir"] = float(raw_ir) * multiplier if not pd.isna(raw_ir) else np.nan
    raw_positive = metrics["positive_ic_ratio_raw"]
    adjusted["adjusted_positive_ic_ratio"] = np.nan if pd.isna(raw_positive) else float(raw_positive if multiplier > 0 else 1.0 - raw_positive)
    raw_spread = metrics["top_minus_bottom_raw"]
    adjusted["adjusted_top_minus_bottom"] = float(raw_spread) if not pd.isna(raw_spread) else np.nan
    adjusted["monotonic_flag"] = int(metrics["monotonic_flag_raw"])
    return adjusted


def classify_status(train_metrics: dict[str, object], validation_metrics: dict[str, object]) -> str:
    train_rows = int(train_metrics["usable_rows"])
    validation_rows = int(validation_metrics["usable_rows"])
    train_dates = int(train_metrics["usable_dates"])
    validation_dates = int(validation_metrics["usable_dates"])
    train_missing = float(train_metrics["missing_ratio"])
    validation_missing = float(validation_metrics["missing_ratio"])

    if (
        train_dates < TRAIN_MIN_DATES
        or validation_dates < VALIDATION_MIN_DATES
        or train_rows < TRAIN_MIN_ROWS
        or validation_rows < VALIDATION_MIN_ROWS
        or train_missing > 0.60
        or validation_missing > 0.60
    ):
        return "D"

    train_ic = float(train_metrics["adjusted_rank_ic_mean"])
    validation_ic = float(validation_metrics["adjusted_rank_ic_mean"])
    validation_structure_ok = (
        int(validation_metrics["monotonic_flag"]) == 1
        or float(validation_metrics["adjusted_top_minus_bottom"]) > 0
        or float(validation_metrics["adjusted_positive_ic_ratio"]) >= 0.50
    )

    if train_ic >= 0.01 and validation_ic > 0 and validation_structure_ok:
        return "A"
    if train_ic > 0 and validation_ic >= 0:
        return "B"
    return "C"


def build_results(panel_df: pd.DataFrame) -> list[dict[str, object]]:
    panel_df = panel_df[panel_df["mean_reversion_ready_v1"] == 1].copy()
    train_mask = (panel_df["rebalance_date"] >= TRAIN_START) & (panel_df["rebalance_date"] < TRAIN_END)
    validation_mask = (panel_df["rebalance_date"] >= VALIDATION_START) & (panel_df["rebalance_date"] < VALIDATION_END)

    results: list[dict[str, object]] = []
    for spec in FACTOR_SPECS:
        factor_name = spec["factor_name"]
        target_label = spec["target_label"]
        train_df, validation_df = preprocess_factor(panel_df[train_mask], panel_df[validation_mask], factor_name)
        train_metrics_raw = compute_window_metrics(train_df, factor_name, target_label)
        direction = str(train_metrics_raw.get("direction", "larger_better"))
        train_metrics = enrich_adjusted_metrics(train_metrics_raw, direction)
        validation_metrics_raw = compute_window_metrics(validation_df, factor_name, target_label, direction=direction)
        validation_metrics = enrich_adjusted_metrics(validation_metrics_raw, direction)
        status = classify_status(train_metrics, validation_metrics)

        results.append(
            {
                "factor_name": factor_name,
                "factor_family": spec["factor_family"],
                "target_label": target_label,
                "direction": direction,
                "train_rows": int(train_metrics["usable_rows"]),
                "validation_rows": int(validation_metrics["usable_rows"]),
                "train_dates": int(train_metrics["usable_dates"]),
                "validation_dates": int(validation_metrics["usable_dates"]),
                "train_missing_ratio": round(float(train_metrics["missing_ratio"]), 6),
                "validation_missing_ratio": round(float(validation_metrics["missing_ratio"]), 6),
                "train_rank_ic_mean": round(float(train_metrics["adjusted_rank_ic_mean"]), 6) if not pd.isna(train_metrics["adjusted_rank_ic_mean"]) else "",
                "validation_rank_ic_mean": round(float(validation_metrics["adjusted_rank_ic_mean"]), 6) if not pd.isna(validation_metrics["adjusted_rank_ic_mean"]) else "",
                "train_rank_ic_ir": round(float(train_metrics["adjusted_rank_ic_ir"]), 6) if not pd.isna(train_metrics["adjusted_rank_ic_ir"]) else "",
                "validation_rank_ic_ir": round(float(validation_metrics["adjusted_rank_ic_ir"]), 6) if not pd.isna(validation_metrics["adjusted_rank_ic_ir"]) else "",
                "train_positive_ic_ratio": round(float(train_metrics["adjusted_positive_ic_ratio"]), 6) if not pd.isna(train_metrics["adjusted_positive_ic_ratio"]) else "",
                "validation_positive_ic_ratio": round(float(validation_metrics["adjusted_positive_ic_ratio"]), 6) if not pd.isna(validation_metrics["adjusted_positive_ic_ratio"]) else "",
                "train_top_minus_bottom": round(float(train_metrics["adjusted_top_minus_bottom"]), 8) if not pd.isna(train_metrics["adjusted_top_minus_bottom"]) else "",
                "validation_top_minus_bottom": round(float(validation_metrics["adjusted_top_minus_bottom"]), 8) if not pd.isna(validation_metrics["adjusted_top_minus_bottom"]) else "",
                "train_monotonic_flag": int(train_metrics["monotonic_flag"]),
                "validation_monotonic_flag": int(validation_metrics["monotonic_flag"]),
                "final_status": status,
            }
        )
    return results


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(result_rows: list[dict[str, object]], monthly_panel: pd.DataFrame) -> None:
    ready_panel = monthly_panel[monthly_panel["mean_reversion_ready_v1"] == 1].copy()
    df = pd.DataFrame(result_rows)
    status_counts = df["final_status"].value_counts().to_dict() if not df.empty else {}
    ranked = df.sort_values(["final_status", "validation_rank_ic_mean"], ascending=[True, False]) if not df.empty else df

    lines = [
        "# Mean Reversion Single-Factor Test Results V1",
        "",
        "Window:",
        "- training: `2014-01-01` to `2019-01-01`",
        "- validation: `2019-01-01` to `2021-01-01`",
        "- monthly sample: first actual trade day of each month",
        "- stock pool proxy: daily rows with `mean_reversion_ready_v1 == 1` on monthly rebalance dates",
        "- target: next monthly rebalance `close-to-close` total return",
        "",
        f"- Monthly sample rows: `{len(monthly_panel)}`",
        f"- Ready monthly rows: `{len(ready_panel)}`",
        f"- Monthly rebalance dates: `{monthly_panel['rebalance_date'].nunique()}`",
        f"- Tested factors: `{len(result_rows)}`",
        f"- A: `{status_counts.get('A', 0)}`",
        f"- B: `{status_counts.get('B', 0)}`",
        f"- C: `{status_counts.get('C', 0)}`",
        f"- D: `{status_counts.get('D', 0)}`",
        "",
        "Full ranking:",
    ]

    if ranked.empty:
        lines.append("- none")
    else:
        for _, row in ranked.iterrows():
            lines.append(
                f"- `{row['factor_name']}` | status=`{row['final_status']}` | direction=`{row['direction']}` | train_dates=`{row['train_dates']}` | val_dates=`{row['validation_dates']}` | val_ic=`{row['validation_rank_ic_mean']}` | val_spread=`{row['validation_top_minus_bottom']}`"
            )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{MONTHLY_PANEL_PATH.name}]({MONTHLY_PANEL_PATH})",
            f"- [{RESULTS_PATH.name}]({RESULTS_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    daily_panel = load_panel()
    calendar_df = load_monthly_calendar()
    monthly_panel = build_monthly_panel(daily_panel, calendar_df)
    monthly_panel.to_csv(MONTHLY_PANEL_PATH, index=False, encoding="utf-8-sig")
    result_rows = build_results(monthly_panel)
    write_csv(result_rows, RESULTS_PATH)
    write_summary(result_rows, monthly_panel)
    print(MONTHLY_PANEL_PATH)
    print(RESULTS_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
