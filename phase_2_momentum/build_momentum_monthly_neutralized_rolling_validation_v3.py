from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
FOLDS_PATH = SCRIPT_DIR / "momentum_monthly_neutralized_rolling_validation_v3_folds.csv"
RESULTS_PATH = SCRIPT_DIR / "momentum_monthly_neutralized_rolling_validation_v3_results.csv"
SUMMARY_PATH = SCRIPT_DIR / "momentum_monthly_neutralized_rolling_validation_v3.md"

TRAIN_MONTHS = 60
VALIDATION_MONTHS = 24
REVIEW_MONTHS = 12
MIN_NAMES_PER_DATE = 5
POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_LABEL = "y_month_total_return_close"
CONTROL_COLS = ["avg_money_20d_pre_rebalance", "avg_market_cap_20d_pre_rebalance"]

CANDIDATE_SPECS = [
    {"factor_name": "mom_6_1_neu", "components": [("mom_6_1", 1.0)], "priority_rank": 1},
    {"factor_name": "combo_631_midheavy_neu", "components": [("mom_3_1", 0.1), ("mom_6_1", 0.6), ("mom_12_1", 0.3)], "priority_rank": 2},
    {"factor_name": "combo_631_balanced_neu", "components": [("mom_3_1", 0.2), ("mom_6_1", 0.5), ("mom_12_1", 0.3)], "priority_rank": 3},
    {"factor_name": "mom_3_1_neu", "components": [("mom_3_1", 1.0)], "priority_rank": 4},
    {"factor_name": "mom_12_1_neu", "components": [("mom_12_1", 1.0)], "priority_rank": 5},
]


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["next_rebalance_date"] = pd.to_datetime(df["next_rebalance_date"])
    return df[df[POOL_FLAG] == 1].copy()


def build_folds(dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    span = TRAIN_MONTHS + VALIDATION_MONTHS + REVIEW_MONTHS
    for start_idx in range(0, len(dates) - span + 1):
        train_dates = dates[start_idx : start_idx + TRAIN_MONTHS]
        validation_dates = dates[start_idx + TRAIN_MONTHS : start_idx + TRAIN_MONTHS + VALIDATION_MONTHS]
        review_dates = dates[start_idx + TRAIN_MONTHS + VALIDATION_MONTHS : start_idx + span]
        if len(train_dates) != TRAIN_MONTHS or len(validation_dates) != VALIDATION_MONTHS or len(review_dates) != REVIEW_MONTHS:
            continue
        folds.append(
            {
                "fold_id": f"mom_mneu_fold_{len(folds) + 1:03d}",
                "train_start": train_dates[0].strftime("%Y-%m-%d"),
                "train_end": train_dates[-1].strftime("%Y-%m-%d"),
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


def add_log_controls(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["_log_avg_money"] = np.where(pd.to_numeric(out["avg_money_20d_pre_rebalance"], errors="coerce") > 0, np.log(pd.to_numeric(out["avg_money_20d_pre_rebalance"], errors="coerce")), np.nan)
    out["_log_avg_market_cap"] = np.where(pd.to_numeric(out["avg_market_cap_20d_pre_rebalance"], errors="coerce") > 0, np.log(pd.to_numeric(out["avg_market_cap_20d_pre_rebalance"], errors="coerce")), np.nan)
    return out


def neutralize_cross_section_by_date(df: pd.DataFrame, raw_factor_name: str) -> pd.Series:
    result = pd.Series(index=df.index, dtype="float64")
    raw_values = pd.to_numeric(df[raw_factor_name], errors="coerce")
    for _, group in df.groupby("rebalance_date"):
        idx = group.index
        y = pd.to_numeric(group[raw_factor_name], errors="coerce")
        x1 = pd.to_numeric(group["_log_avg_money"], errors="coerce")
        x2 = pd.to_numeric(group["_log_avg_market_cap"], errors="coerce")
        valid_mask = y.notna() & x1.notna() & x2.notna()
        if int(valid_mask.sum()) < 4:
            result.loc[idx] = np.nan
            continue
        y_valid = y[valid_mask].to_numpy(dtype=float)
        x_valid = np.column_stack(
            [
                np.ones(int(valid_mask.sum()), dtype=float),
                x1[valid_mask].to_numpy(dtype=float),
                x2[valid_mask].to_numpy(dtype=float),
            ]
        )
        beta, _, _, _ = np.linalg.lstsq(x_valid, y_valid, rcond=None)
        fitted = x_valid @ beta
        residual = y_valid - fitted
        residual_series = pd.Series(residual, index=y[valid_mask].index, dtype="float64")
        result.loc[idx] = residual_series.reindex(idx)
    return result


def preprocess_residual_factor(full_df: pd.DataFrame, train_mask: pd.Series, raw_factor_name: str) -> pd.Series:
    residual_values = neutralize_cross_section_by_date(full_df, raw_factor_name)
    train_values = residual_values[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=full_df.index, dtype="float64")
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = winsorize(residual_values, lower, upper)
    train_clipped = clipped[train_mask].dropna()
    mean_value = float(train_clipped.mean())
    std_value = float(train_clipped.std(ddof=0))
    return zscore(clipped, mean_value, std_value)


def compute_window_metrics(window_df: pd.DataFrame, score_col: str, direction: str | None = None) -> dict[str, object]:
    sample_df = window_df[["rebalance_date", score_col, TARGET_LABEL]].copy()
    total_rows = len(sample_df)
    sample_df[score_col] = pd.to_numeric(sample_df[score_col], errors="coerce")
    sample_df[TARGET_LABEL] = pd.to_numeric(sample_df[TARGET_LABEL], errors="coerce")
    sample_df = sample_df.dropna(subset=[score_col, TARGET_LABEL])
    missing_ratio = 1.0 if total_rows == 0 else 1.0 - (len(sample_df) / total_rows)
    usable_dates = sample_df["rebalance_date"].nunique()
    usable_rows = len(sample_df)

    by_date = []
    for rebalance_date, group in sample_df.groupby("rebalance_date"):
        if len(group) < MIN_NAMES_PER_DATE:
            continue
        ic = compute_rank_ic(group[score_col], group[TARGET_LABEL])
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
        bucket_means = group.groupby("_bucket")[TARGET_LABEL].mean().to_dict()
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


def compute_priority_score(metrics: dict[str, object], priority_rank: int) -> float:
    ic = float(metrics["rank_ic_mean"]) if not pd.isna(metrics["rank_ic_mean"]) else -999.0
    spread = float(metrics["top_minus_bottom"]) if not pd.isna(metrics["top_minus_bottom"]) else -999.0
    pos = float(metrics["positive_ic_ratio"]) if not pd.isna(metrics["positive_ic_ratio"]) else 0.0
    tie_break = (10 - priority_rank) * 1e-6
    return ic + max(spread, 0.0) + max(pos - 0.5, 0.0) + tie_break


def candidate_passes(metrics: dict[str, object]) -> bool:
    ic = float(metrics["rank_ic_mean"]) if not pd.isna(metrics["rank_ic_mean"]) else -999.0
    spread = float(metrics["top_minus_bottom"]) if not pd.isna(metrics["top_minus_bottom"]) else -999.0
    pos = float(metrics["positive_ic_ratio"]) if not pd.isna(metrics["positive_ic_ratio"]) else 0.0
    return ic > 0 and (spread > 0 or pos >= 0.5)


def prepare_scored_frame(panel_df: pd.DataFrame, train_mask: pd.Series) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    df = add_log_controls(panel_df)
    base_factor_meta: dict[str, dict[str, object]] = {}
    used_base_factors = sorted({component_name for spec in CANDIDATE_SPECS for component_name, _ in spec["components"]})

    for factor_name in used_base_factors:
        z_col = f"z_neu__{factor_name}"
        df[z_col] = preprocess_residual_factor(df, train_mask, factor_name)
        train_metrics_raw = compute_window_metrics(df[train_mask], z_col)
        direction = str(train_metrics_raw["direction"])
        mult = 1.0 if direction == "larger_better" else -1.0
        adj_col = f"adj_neu__{factor_name}"
        df[adj_col] = df[z_col] * mult
        base_factor_meta[factor_name] = {"direction": direction, "adj_col": adj_col}

    candidate_meta: dict[str, dict[str, object]] = {}
    for spec in CANDIDATE_SPECS:
        score_col = f"score__{spec['factor_name']}"
        weighted_parts = []
        for component_name, weight in spec["components"]:
            weighted_parts.append(df[str(base_factor_meta[component_name]["adj_col"])] * float(weight))
        weighted_sum = sum(weighted_parts)
        weight_total = sum(abs(float(weight)) for _, weight in spec["components"])
        df[score_col] = weighted_sum / weight_total if weight_total > 0 else np.nan
        candidate_meta[spec["factor_name"]] = {
            "score_col": score_col,
            "priority_rank": spec["priority_rank"],
            "components": " + ".join(f"{weight}*{name}" for name, weight in spec["components"]),
        }
    return df, candidate_meta


def summarize_candidate(df: pd.DataFrame, score_col: str, mask: pd.Series) -> dict[str, object]:
    return compute_window_metrics(df[mask], score_col, direction="larger_better")


def select_candidate(df: pd.DataFrame, candidate_meta: dict[str, dict[str, object]], validation_mask: pd.Series) -> tuple[str, dict[str, object], list[dict[str, object]]]:
    scored_candidates: list[dict[str, object]] = []
    for spec in CANDIDATE_SPECS:
        factor_name = spec["factor_name"]
        metrics = summarize_candidate(df, str(candidate_meta[factor_name]["score_col"]), validation_mask)
        scored_candidates.append(
            {
                "factor_name": factor_name,
                "metrics": metrics,
                "priority_rank": int(candidate_meta[factor_name]["priority_rank"]),
                "priority_score": compute_priority_score(metrics, int(candidate_meta[factor_name]["priority_rank"])),
                "components": str(candidate_meta[factor_name]["components"]),
            }
        )
    scored_candidates.sort(key=lambda item: item["priority_score"], reverse=True)
    for candidate in scored_candidates:
        if candidate_passes(candidate["metrics"]):
            return str(candidate["factor_name"]), dict(candidate["metrics"]), scored_candidates
    first = scored_candidates[0]
    return str(first["factor_name"]), dict(first["metrics"]), scored_candidates


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
        validation_mask = (panel_df["rebalance_date"] >= validation_start) & (panel_df["rebalance_date"] <= validation_end)
        review_mask = (panel_df["rebalance_date"] >= review_start) & (panel_df["rebalance_date"] <= review_end)

        scored_df, candidate_meta = prepare_scored_frame(panel_df, train_mask)
        selected_name, _, candidate_scores = select_candidate(scored_df, candidate_meta, validation_mask)
        selected_score_col = str(candidate_meta[selected_name]["score_col"])

        train_metrics = summarize_candidate(scored_df, selected_score_col, train_mask)
        validation_metrics = summarize_candidate(scored_df, selected_score_col, validation_mask)
        review_metrics = summarize_candidate(scored_df, selected_score_col, review_mask)

        candidate_rank_text = " | ".join(
            [
                f"{item['factor_name']}:{round(float(item['metrics']['rank_ic_mean']), 6) if not pd.isna(item['metrics']['rank_ic_mean']) else 'nan'}"
                for item in candidate_scores
            ]
        )

        rows.append(
            {
                "fold_id": fold["fold_id"],
                "train_start": fold["train_start"],
                "train_end": fold["train_end"],
                "validation_start": fold["validation_start"],
                "validation_end": fold["validation_end"],
                "review_start": fold["review_start"],
                "review_end": fold["review_end"],
                "selected_factor": selected_name,
                "selected_components": str(candidate_meta[selected_name]["components"]),
                "validation_candidate_ranking": candidate_rank_text,
                "train_rows": int(train_metrics["usable_rows"]),
                "train_dates": int(train_metrics["usable_dates"]),
                "train_rank_ic_mean": round(float(train_metrics["rank_ic_mean"]), 6) if not pd.isna(train_metrics["rank_ic_mean"]) else "",
                "train_top_minus_bottom": round(float(train_metrics["top_minus_bottom"]), 8) if not pd.isna(train_metrics["top_minus_bottom"]) else "",
                "validation_rows": int(validation_metrics["usable_rows"]),
                "validation_dates": int(validation_metrics["usable_dates"]),
                "validation_rank_ic_mean": round(float(validation_metrics["rank_ic_mean"]), 6) if not pd.isna(validation_metrics["rank_ic_mean"]) else "",
                "validation_top_minus_bottom": round(float(validation_metrics["top_minus_bottom"]), 8) if not pd.isna(validation_metrics["top_minus_bottom"]) else "",
                "validation_positive_ic_ratio": round(float(validation_metrics["positive_ic_ratio"]), 6) if not pd.isna(validation_metrics["positive_ic_ratio"]) else "",
                "review_rows": int(review_metrics["usable_rows"]),
                "review_dates": int(review_metrics["usable_dates"]),
                "review_rank_ic_mean": round(float(review_metrics["rank_ic_mean"]), 6) if not pd.isna(review_metrics["rank_ic_mean"]) else "",
                "review_top_minus_bottom": round(float(review_metrics["top_minus_bottom"]), 8) if not pd.isna(review_metrics["top_minus_bottom"]) else "",
                "review_positive_ic_ratio": round(float(review_metrics["positive_ic_ratio"]), 6) if not pd.isna(review_metrics["positive_ic_ratio"]) else "",
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


def write_summary(folds: list[dict[str, object]], result_rows: list[dict[str, object]]) -> None:
    df = pd.DataFrame(result_rows)
    lines = [
        "# Momentum Monthly Neutralized Rolling Validation V3",
        "",
        "Protocol:",
        "- monthly rebalance = each month first actual trading day",
        "- fold structure = `60m train + 24m validation + 12m review`",
        "- stock pool = prior-20-trading-day average traded amount top 60% intersect prior-20-trading-day average market-cap top 60%",
        "- neutralization = each rebalance date cross-sectionally regress momentum on `log(avg_money_20d_pre_rebalance)` and `log(avg_market_cap_20d_pre_rebalance)`",
        "- factor library keeps neutralized `mom_3_1`, `mom_6_1`, `mom_12_1`, and two 6-1-centered composites",
        "- each fold reselects the active factor only from its own validation window",
        "",
        f"- fold count: `{len(folds)}`",
        "",
    ]

    if not df.empty:
        lines.append("Selection frequency:")
        selection_counts = df["selected_factor"].value_counts()
        for factor_name, count in selection_counts.items():
            lines.append(f"- `{factor_name}`: `{int(count)}` folds")

        lines.extend(["", "Average selected-factor review results:"])
        review_ic_mean = pd.to_numeric(df["review_rank_ic_mean"], errors="coerce").mean()
        review_spread_mean = pd.to_numeric(df["review_top_minus_bottom"], errors="coerce").mean()
        review_pos_mean = pd.to_numeric(df["review_positive_ic_ratio"], errors="coerce").mean()
        lines.append(f"- mean_review_ic=`{round(float(review_ic_mean), 6)}`")
        lines.append(f"- mean_review_spread=`{round(float(review_spread_mean), 8)}`")
        lines.append(f"- mean_review_positive_ic_ratio=`{round(float(review_pos_mean), 6)}`")

        lines.extend(["", "Per-factor review summary after validation selection:"])
        factor_summary = (
            df.groupby("selected_factor", dropna=False)
            .agg(
                fold_count=("fold_id", "count"),
                mean_validation_ic=("validation_rank_ic_mean", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_review_ic=("review_rank_ic_mean", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_review_spread=("review_top_minus_bottom", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["fold_count", "mean_review_ic"], ascending=[False, False])
        )
        for _, row in factor_summary.iterrows():
            lines.append(
                f"- `{row['selected_factor']}` | folds=`{int(row['fold_count'])}` | mean_validation_ic=`{round(float(row['mean_validation_ic']), 6)}` | mean_review_ic=`{round(float(row['mean_review_ic']), 6)}` | mean_review_spread=`{round(float(row['mean_review_spread']), 8)}`"
            )

        lines.extend(["", "Latest folds preview:"])
        preview_df = df.tail(5)
        for _, row in preview_df.iterrows():
            lines.append(
                f"- `{row['fold_id']}` | validation=`{row['validation_start']}` to `{row['validation_end']}` | review=`{row['review_start']}` to `{row['review_end']}` | selected=`{row['selected_factor']}` | review_ic=`{row['review_rank_ic_mean']}` | review_spread=`{row['review_top_minus_bottom']}`"
            )

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
