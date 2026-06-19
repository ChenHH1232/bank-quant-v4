from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
MONTHLY_PANEL_PATH = SCRIPT_DIR / "mean_reversion_monthly_rebalance_panel_v1.csv"
RESULTS_PATH = SCRIPT_DIR / "mean_reversion_composite_test_results_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "mean_reversion_composite_test_results_v1.md"

TRAIN_START = pd.Timestamp("2014-01-01")
TRAIN_END = pd.Timestamp("2019-01-01")
VALIDATION_START = pd.Timestamp("2019-01-01")
VALIDATION_END = pd.Timestamp("2021-01-01")

CANDIDATE_SPECS = [
    {
        "factor_name": "rev5_downratio",
        "components": [("rev_5d", -0.7), ("down_day_ratio_20d", 0.3)],
        "target_label": "y_month_total_return_close",
    },
    {
        "factor_name": "rev5_abnvol",
        "components": [("rev_5d", -0.7), ("abnormal_volume_ratio", 0.3)],
        "target_label": "y_month_total_return_close",
    },
    {
        "factor_name": "rev5_lowpb",
        "components": [("rev_5d", -0.7), ("pb_ratio", -0.3)],
        "target_label": "y_month_total_return_close",
    },
]

TRAIN_MIN_DATES = 24
VALIDATION_MIN_DATES = 12
TRAIN_MIN_ROWS = 300
VALIDATION_MIN_ROWS = 120


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(MONTHLY_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    return df[df["mean_reversion_ready_v1"] == 1].copy()


def winsorize(series: pd.Series, lower: float, upper: float) -> pd.Series:
    return series.clip(lower=lower, upper=upper)


def zscore(series: pd.Series, mean_value: float, std_value: float) -> pd.Series:
    if std_value <= 0 or math.isnan(std_value):
        return series * np.nan
    return (series - mean_value) / std_value


def preprocess_component(full_df: pd.DataFrame, train_mask: pd.Series, factor_name: str) -> pd.Series:
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


def compute_spearman_like_rank_ic(x: pd.Series, y: pd.Series) -> float:
    ranked_x = x.rank(method="average")
    ranked_y = y.rank(method="average")
    value = ranked_x.corr(ranked_y, method="pearson")
    return float(value) if not pd.isna(value) else np.nan


def compute_window_metrics(window_df: pd.DataFrame, score_col: str, target_label: str, direction: str | None = None) -> dict[str, object]:
    sample_df = window_df[["rebalance_date", score_col, target_label]].copy()
    total_rows = len(sample_df)
    sample_df[score_col] = pd.to_numeric(sample_df[score_col], errors="coerce")
    sample_df[target_label] = pd.to_numeric(sample_df[target_label], errors="coerce")
    sample_df = sample_df.dropna(subset=[score_col, target_label])

    missing_ratio = 1.0 if total_rows == 0 else 1.0 - (len(sample_df) / total_rows)
    usable_dates = sample_df["rebalance_date"].nunique()
    usable_rows = len(sample_df)

    by_date = []
    for rebalance_date, group in sample_df.groupby("rebalance_date"):
        if len(group) < 5:
            continue
        rank_ic = compute_spearman_like_rank_ic(group[score_col], group[target_label])
        if pd.isna(rank_ic):
            continue
        by_date.append({"rebalance_date": rebalance_date, "rank_ic": float(rank_ic), "group": group})

    if not by_date:
        return {
            "usable_rows": usable_rows,
            "usable_dates": usable_dates,
            "missing_ratio": missing_ratio,
            "rank_ic_mean_raw": np.nan,
            "positive_ic_ratio_raw": np.nan,
            "top_minus_bottom_raw": np.nan,
            "direction": direction or "larger_better",
        }

    rank_ic_values = np.array([item["rank_ic"] for item in by_date], dtype=float)
    rank_ic_mean_raw = float(rank_ic_values.mean())
    positive_ic_ratio_raw = float((rank_ic_values > 0).mean())
    if direction is None:
        direction = "larger_better" if rank_ic_mean_raw >= 0 else "smaller_better"

    multiplier = 1.0 if direction == "larger_better" else -1.0
    spreads = []
    for item in by_date:
        group = item["group"].copy()
        group["_bucket"] = assign_groups(group[score_col], 5)
        group = group.dropna(subset=["_bucket"])
        bucket_means = group.groupby("_bucket")[target_label].mean().to_dict()
        if 1 in bucket_means and 5 in bucket_means:
            spreads.append(float(bucket_means[5] - bucket_means[1]) * multiplier)

    return {
        "usable_rows": usable_rows,
        "usable_dates": usable_dates,
        "missing_ratio": missing_ratio,
        "rank_ic_mean": rank_ic_mean_raw * multiplier,
        "positive_ic_ratio": positive_ic_ratio_raw if multiplier > 0 else 1.0 - positive_ic_ratio_raw,
        "top_minus_bottom": float(np.mean(spreads)) if spreads else np.nan,
        "direction": direction,
    }


def classify_status(train_metrics: dict[str, object], validation_metrics: dict[str, object]) -> str:
    if (
        int(train_metrics["usable_dates"]) < TRAIN_MIN_DATES
        or int(validation_metrics["usable_dates"]) < VALIDATION_MIN_DATES
        or int(train_metrics["usable_rows"]) < TRAIN_MIN_ROWS
        or int(validation_metrics["usable_rows"]) < VALIDATION_MIN_ROWS
        or float(train_metrics["missing_ratio"]) > 0.60
        or float(validation_metrics["missing_ratio"]) > 0.60
    ):
        return "D"
    train_ic = float(train_metrics["rank_ic_mean"]) if not pd.isna(train_metrics["rank_ic_mean"]) else -999.0
    val_ic = float(validation_metrics["rank_ic_mean"]) if not pd.isna(validation_metrics["rank_ic_mean"]) else -999.0
    val_spread = float(validation_metrics["top_minus_bottom"]) if not pd.isna(validation_metrics["top_minus_bottom"]) else -999.0
    val_pos = float(validation_metrics["positive_ic_ratio"]) if not pd.isna(validation_metrics["positive_ic_ratio"]) else 0.0
    if train_ic >= 0.01 and val_ic > 0 and (val_spread > 0 or val_pos >= 0.5):
        return "A"
    if train_ic > 0 and val_ic >= 0:
        return "B"
    return "C"


def build_results(panel_df: pd.DataFrame) -> list[dict[str, object]]:
    train_mask = (panel_df["rebalance_date"] >= TRAIN_START) & (panel_df["rebalance_date"] < TRAIN_END)
    validation_mask = (panel_df["rebalance_date"] >= VALIDATION_START) & (panel_df["rebalance_date"] < VALIDATION_END)

    results = []
    for spec in CANDIDATE_SPECS:
        work = panel_df.copy()
        parts = []
        total_weight = 0.0
        for factor_name, weight in spec["components"]:
            z_col = f"z__{factor_name}"
            work[z_col] = preprocess_component(work, train_mask, factor_name)
            parts.append(pd.to_numeric(work[z_col], errors="coerce") * float(weight))
            total_weight += abs(float(weight))
        work["score"] = sum(parts) / total_weight if total_weight > 0 else np.nan

        train_metrics = compute_window_metrics(work[train_mask], "score", spec["target_label"], direction="larger_better")
        validation_metrics = compute_window_metrics(work[validation_mask], "score", spec["target_label"], direction="larger_better")
        status = classify_status(train_metrics, validation_metrics)

        results.append(
            {
                "factor_name": spec["factor_name"],
                "components": " + ".join(f"{w}*{n}" for n, w in spec["components"]),
                "direction": "larger_better",
                "train_rows": int(train_metrics["usable_rows"]),
                "validation_rows": int(validation_metrics["usable_rows"]),
                "train_dates": int(train_metrics["usable_dates"]),
                "validation_dates": int(validation_metrics["usable_dates"]),
                "train_rank_ic_mean": round(float(train_metrics["rank_ic_mean"]), 6) if not pd.isna(train_metrics["rank_ic_mean"]) else "",
                "validation_rank_ic_mean": round(float(validation_metrics["rank_ic_mean"]), 6) if not pd.isna(validation_metrics["rank_ic_mean"]) else "",
                "train_positive_ic_ratio": round(float(train_metrics["positive_ic_ratio"]), 6) if not pd.isna(train_metrics["positive_ic_ratio"]) else "",
                "validation_positive_ic_ratio": round(float(validation_metrics["positive_ic_ratio"]), 6) if not pd.isna(validation_metrics["positive_ic_ratio"]) else "",
                "train_top_minus_bottom": round(float(train_metrics["top_minus_bottom"]), 8) if not pd.isna(train_metrics["top_minus_bottom"]) else "",
                "validation_top_minus_bottom": round(float(validation_metrics["top_minus_bottom"]), 8) if not pd.isna(validation_metrics["top_minus_bottom"]) else "",
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


def write_summary(rows: list[dict[str, object]], panel_df: pd.DataFrame) -> None:
    df = pd.DataFrame(rows)
    status_counts = df["final_status"].value_counts().to_dict() if not df.empty else {}
    ranked = df.sort_values(["final_status", "validation_rank_ic_mean"], ascending=[True, False]) if not df.empty else df
    lines = [
        "# Mean Reversion Composite Test Results V1",
        "",
        "Window:",
        "- training: `2014-01-01` to `2019-01-01`",
        "- validation: `2019-01-01` to `2021-01-01`",
        "- monthly sample: first actual trade day of each month",
        "- target: next monthly rebalance `close-to-close` total return",
        "",
        f"- Ready monthly rows: `{len(panel_df)}`",
        f"- Monthly rebalance dates: `{panel_df['rebalance_date'].nunique()}`",
        f"- Tested composites: `{len(rows)}`",
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
                f"- `{row['factor_name']}` | status=`{row['final_status']}` | val_ic=`{row['validation_rank_ic_mean']}` | val_spread=`{row['validation_top_minus_bottom']}` | components=`{row['components']}`"
            )
    lines.extend(["", "Output:", f"- [{RESULTS_PATH.name}]({RESULTS_PATH})"])
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    rows = build_results(panel_df)
    write_csv(rows, RESULTS_PATH)
    write_summary(rows, panel_df)
    print(RESULTS_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
