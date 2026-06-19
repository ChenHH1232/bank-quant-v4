from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_quarterly_rebalance_panel_v1.csv"
FOLDS_PATH = SCRIPT_DIR / "momentum_quarterly_rolling_validation_v1_folds.csv"
RESULTS_PATH = SCRIPT_DIR / "momentum_quarterly_rolling_validation_v1_results.csv"
SUMMARY_PATH = SCRIPT_DIR / "momentum_quarterly_rolling_validation_v1.md"

TRAIN_YEARS = 5
VALIDATION_QUARTERS = 8
REVIEW_QUARTERS = 4
TRAIN_MIN_REBALANCE_DATES = 16

ALPHA_CANDIDATES = [
    {"factor_name": "mom_12_1", "priority_rank": 1},
    {"factor_name": "mom_6_1", "priority_rank": 2},
    {"factor_name": "mom_3m", "priority_rank": 3},
]
SUPPORT_CANDIDATES = [{"factor_name": "liq_money_1m", "priority_rank": 1}]
TARGET_LABEL = "y_quarter_total_return_close"


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["next_rebalance_date"] = pd.to_datetime(df["next_rebalance_date"])
    return df[df["rebalance_stock_pool_flag"] == 1].copy()


def month_floor(ts: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=ts.year, month=ts.month, day=1)


def build_folds(dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    for idx in range(len(dates)):
        validation_dates = dates[idx : idx + VALIDATION_QUARTERS]
        review_dates = dates[idx + VALIDATION_QUARTERS : idx + VALIDATION_QUARTERS + REVIEW_QUARTERS]
        if len(validation_dates) < VALIDATION_QUARTERS or len(review_dates) < REVIEW_QUARTERS:
            continue
        validation_start = validation_dates[0]
        train_start = month_floor(validation_start) - pd.DateOffset(years=TRAIN_YEARS)
        train_dates = [d for d in dates if train_start <= d < validation_start]
        if len(train_dates) < TRAIN_MIN_REBALANCE_DATES:
            continue
        folds.append(
            {
                "fold_id": f"mom_qfold_{len(folds) + 1:02d}",
                "train_start": train_start.strftime("%Y-%m-%d"),
                "train_end": (validation_start - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "validation_start": validation_dates[0].strftime("%Y-%m-%d"),
                "validation_end": validation_dates[-1].strftime("%Y-%m-%d"),
                "review_start": review_dates[0].strftime("%Y-%m-%d"),
                "review_end": review_dates[-1].strftime("%Y-%m-%d"),
                "train_rebalance_dates": len(train_dates),
                "validation_rebalance_dates": len(validation_dates),
                "review_rebalance_dates": len(review_dates),
            }
        )
    return folds


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
        ic = compute_rank_ic(group[score_col], group[target_label])
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
        bucket_means = group.groupby("_bucket")[target_label].mean().to_dict()
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


def compute_priority_score(metrics: dict[str, object]) -> float:
    ic = float(metrics["rank_ic_mean"]) if not pd.isna(metrics["rank_ic_mean"]) else -999.0
    spread = float(metrics["top_minus_bottom"]) if not pd.isna(metrics["top_minus_bottom"]) else -999.0
    pos = float(metrics["positive_ic_ratio"]) if not pd.isna(metrics["positive_ic_ratio"]) else 0.0
    return ic + max(spread, 0.0) + max(pos - 0.5, 0.0)


def factor_decision_passes(metrics: dict[str, object]) -> bool:
    ic = float(metrics["rank_ic_mean"]) if not pd.isna(metrics["rank_ic_mean"]) else -999.0
    spread = float(metrics["top_minus_bottom"]) if not pd.isna(metrics["top_minus_bottom"]) else -999.0
    pos = float(metrics["positive_ic_ratio"]) if not pd.isna(metrics["positive_ic_ratio"]) else 0.0
    return ic > 0 and (spread > 0 or pos >= 0.5)


def prepare_scored_frame(panel_df: pd.DataFrame, train_mask: pd.Series) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    df = panel_df.copy()
    factor_meta: dict[str, dict[str, object]] = {}
    for item in ALPHA_CANDIDATES + SUPPORT_CANDIDATES:
        factor_name = item["factor_name"]
        z_col = f"z__{factor_name}"
        df[z_col] = preprocess_factor(df, train_mask, factor_name)
        train_metrics_raw = compute_window_metrics(df[train_mask], z_col, TARGET_LABEL)
        direction = str(train_metrics_raw["direction"])
        mult = 1.0 if direction == "larger_better" else -1.0
        adj_col = f"adj__{factor_name}"
        df[adj_col] = df[z_col] * mult
        factor_meta[factor_name] = {"direction": direction, "adj_col": adj_col, "priority_rank": item["priority_rank"]}
    return df, factor_meta


def summarize_factor(df: pd.DataFrame, factor_name: str, factor_meta: dict[str, dict[str, object]], mask: pd.Series) -> dict[str, object]:
    return compute_window_metrics(df[mask], str(factor_meta[factor_name]["adj_col"]), TARGET_LABEL, direction="larger_better")


def select_alpha_factor(df: pd.DataFrame, factor_meta: dict[str, dict[str, object]], validation_mask: pd.Series) -> tuple[str, dict[str, object]]:
    scored = []
    for item in ALPHA_CANDIDATES:
        factor_name = item["factor_name"]
        metrics = summarize_factor(df, factor_name, factor_meta, validation_mask)
        scored.append((factor_name, metrics, compute_priority_score(metrics), item["priority_rank"]))
    scored.sort(key=lambda x: (x[2], -x[3]), reverse=True)
    preferred = next((row for row in scored if row[0] == "mom_12_1"), None)
    if preferred and factor_decision_passes(preferred[1]):
        return preferred[0], preferred[1]
    for factor_name, metrics, _, _ in scored:
        if factor_decision_passes(metrics):
            return factor_name, metrics
    return scored[0][0], scored[0][1]


def select_support_factor(df: pd.DataFrame, factor_meta: dict[str, dict[str, object]], validation_mask: pd.Series) -> tuple[str | None, dict[str, object] | None]:
    for item in SUPPORT_CANDIDATES:
        factor_name = item["factor_name"]
        metrics = summarize_factor(df, factor_name, factor_meta, validation_mask)
        if factor_decision_passes(metrics):
            return factor_name, metrics
    return None, None


def add_combo_score(df: pd.DataFrame, factor_meta: dict[str, dict[str, object]], factor_names: list[str], combo_name: str) -> pd.DataFrame:
    cols = [str(factor_meta[name]["adj_col"]) for name in factor_names]
    df = df.copy()
    df[combo_name] = df[cols].mean(axis=1, skipna=True)
    return df


def build_result_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])
        review_start = pd.Timestamp(fold["review_start"])
        review_end = pd.Timestamp(fold["review_end"])
        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)
        validation_mask = (panel_df["rebalance_date"] >= validation_start) & (panel_df["rebalance_date"] <= validation_end)
        review_mask = (panel_df["rebalance_date"] >= review_start) & (panel_df["rebalance_date"] <= review_end)
        scored_df, factor_meta = prepare_scored_frame(panel_df, train_mask)
        alpha_name, alpha_metrics = select_alpha_factor(scored_df, factor_meta, validation_mask)
        support_name, support_metrics = select_support_factor(scored_df, factor_meta, validation_mask)
        scenarios = [("alpha_only", [alpha_name])]
        if support_name:
            scenarios.append(("alpha_plus_support", [alpha_name, support_name]))
        for scenario_name, factor_names in scenarios:
            combo_name = f"combo__{scenario_name}"
            scenario_df = add_combo_score(scored_df, factor_meta, factor_names, combo_name)
            train_metrics = compute_window_metrics(scenario_df[train_mask], combo_name, TARGET_LABEL, direction="larger_better")
            validation_metrics = compute_window_metrics(scenario_df[validation_mask], combo_name, TARGET_LABEL, direction="larger_better")
            review_metrics = compute_window_metrics(scenario_df[review_mask], combo_name, TARGET_LABEL, direction="larger_better")
            rows.append({
                "fold_id": fold["fold_id"],
                "train_start": fold["train_start"],
                "train_end": fold["train_end"],
                "validation_start": fold["validation_start"],
                "validation_end": fold["validation_end"],
                "review_start": fold["review_start"],
                "review_end": fold["review_end"],
                "selected_alpha_factor": alpha_name,
                "selected_alpha_direction": factor_meta[alpha_name]["direction"],
                "selected_alpha_validation_ic": round(float(alpha_metrics["rank_ic_mean"]), 6) if not pd.isna(alpha_metrics["rank_ic_mean"]) else "",
                "selected_support_factor": support_name or "",
                "selected_support_validation_ic": round(float(support_metrics["rank_ic_mean"]), 6) if support_name and not pd.isna(support_metrics["rank_ic_mean"]) else "",
                "scenario_name": scenario_name,
                "factor_set": " + ".join(factor_names),
                "train_rows": int(train_metrics["usable_rows"]),
                "train_dates": int(train_metrics["usable_dates"]),
                "train_rank_ic_mean": round(float(train_metrics["rank_ic_mean"]), 6) if not pd.isna(train_metrics["rank_ic_mean"]) else "",
                "validation_rows": int(validation_metrics["usable_rows"]),
                "validation_dates": int(validation_metrics["usable_dates"]),
                "validation_rank_ic_mean": round(float(validation_metrics["rank_ic_mean"]), 6) if not pd.isna(validation_metrics["rank_ic_mean"]) else "",
                "validation_top_minus_bottom": round(float(validation_metrics["top_minus_bottom"]), 8) if not pd.isna(validation_metrics["top_minus_bottom"]) else "",
                "review_rows": int(review_metrics["usable_rows"]),
                "review_dates": int(review_metrics["usable_dates"]),
                "review_rank_ic_mean": round(float(review_metrics["rank_ic_mean"]), 6) if not pd.isna(review_metrics["rank_ic_mean"]) else "",
                "review_top_minus_bottom": round(float(review_metrics["top_minus_bottom"]), 8) if not pd.isna(review_metrics["top_minus_bottom"]) else "",
            })
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(folds: list[dict[str, object]], result_rows: list[dict[str, object]]) -> None:
    df = pd.DataFrame(result_rows)
    lines = [
        "# Momentum Quarterly Rolling Validation V1",
        "",
        "Protocol:",
        "- quarterly rebalance dates inherit the phase-1 fundamental calendar",
        "- fold structure = `5y train + 8q validation + 4q review`",
        "- stock pool keeps prior-20-trading-day amount and market-cap double-top-80% rule",
        "- alpha candidates keep the frozen momentum shortlist led by `mom_12_1`",
        "",
        f"- fold count: `{len(folds)}`",
        "",
    ]
    if not df.empty:
        lines.append("Average review results by scenario:")
        summary = (
            df.groupby("scenario_name", dropna=False)
            .agg(
                fold_count=("fold_id", "count"),
                mean_review_ic=("review_rank_ic_mean", lambda s: pd.to_numeric(s, errors='coerce').mean()),
                mean_review_spread=("review_top_minus_bottom", lambda s: pd.to_numeric(s, errors='coerce').mean()),
            )
            .reset_index()
            .sort_values(["mean_review_ic", "mean_review_spread"], ascending=[False, False])
        )
        for _, row in summary.iterrows():
            lines.append(
                f"- `{row['scenario_name']}` | folds=`{int(row['fold_count'])}` | mean_review_ic=`{round(float(row['mean_review_ic']), 6)}` | mean_review_spread=`{round(float(row['mean_review_spread']), 8)}`"
            )
        lines.extend(["", "Alpha selection frequency:"])
        alpha_counts = df[["fold_id", "selected_alpha_factor"]].drop_duplicates()["selected_alpha_factor"].value_counts()
        for name, count in alpha_counts.items():
            lines.append(f"- `{name}`: `{int(count)}` folds")
    lines.extend(["", "Outputs:", f"- [{FOLDS_PATH.name}]({FOLDS_PATH})", f"- [{RESULTS_PATH.name}]({RESULTS_PATH})"])
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    dates = sorted(pd.Timestamp(d) for d in panel_df["rebalance_date"].drop_duplicates())
    folds = build_folds(dates)
    result_rows = build_result_rows(panel_df, folds)
    write_csv(FOLDS_PATH, folds)
    write_csv(RESULTS_PATH, result_rows)
    write_summary(folds, result_rows)
    print(FOLDS_PATH)
    print(RESULTS_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
