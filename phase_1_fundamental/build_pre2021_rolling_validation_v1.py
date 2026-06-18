import csv
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
IMPROVEMENT_PANEL_PATH = SCRIPT_DIR / "improvement_factor_panel_v1.csv"
CORE_RESULTS_PATH = SCRIPT_DIR / "single_factor_test_results_core_v2.csv"
IMPROVEMENT_RESULTS_PATH = SCRIPT_DIR / "improvement_factor_test_results_v1.csv"
FACTOR_POOL_PATH = SCRIPT_DIR / "final_core_factor_pool_v3.csv"

OUTPUT_FOLDS_PATH = SCRIPT_DIR / "pre2021_rolling_validation_v1_folds.csv"
OUTPUT_RESULTS_PATH = SCRIPT_DIR / "pre2021_rolling_validation_v1_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "pre2021_rolling_validation_v1.md"

RESEARCH_END = pd.Timestamp("2021-05-01")
TRAIN_YEARS = 5
VALIDATION_REBALANCE_COUNT = 4
FOLD_STEP = 2
MIN_TRAIN_REBALANCE_DATES = 16

SCENARIO_BASE = "base_core_7"
SCENARIO_ENHANCED = "base_plus_top2_9"
COMBO_NAMES = [
    "combo__equal_weight",
    "combo__ic_weight_train",
    "combo__quarterly_plus_annual",
]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_panel() -> pd.DataFrame:
    base_df = pd.read_csv(BASE_PANEL_PATH, encoding="utf-8-sig")
    base_df["rebalance_date"] = pd.to_datetime(base_df["rebalance_date"])
    base_df = base_df[base_df["rebalance_stock_pool_flag"].astype(str) == "1"].copy()

    improvement_df = pd.read_csv(IMPROVEMENT_PANEL_PATH, encoding="utf-8-sig")
    improvement_df["rebalance_date"] = pd.to_datetime(improvement_df["rebalance_date"])
    improve_cols = [col for col in improvement_df.columns if col.startswith("improve__")]

    combined = base_df.merge(
        improvement_df[["rebalance_date", "code"] + improve_cols],
        how="left",
        on=["rebalance_date", "code"],
    )
    return combined


def prepare_factor_metadata() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    core_results = {row["factor_name"]: row for row in load_rows(CORE_RESULTS_PATH)}
    improvement_results = {row["factor_name"]: row for row in load_rows(IMPROVEMENT_RESULTS_PATH)}

    base_rows: list[dict[str, str]] = []
    enhanced_rows: list[dict[str, str]] = []

    for row in load_rows(FACTOR_POOL_PATH):
        factor_name = row["factor_name"]
        factor_result = core_results.get(factor_name) or improvement_results.get(factor_name)
        if factor_result is None:
            raise KeyError(f"Missing factor metadata for {factor_name}")

        metadata_row = {
            "factor_name": factor_name,
            "factor_family": row["factor_family"],
            "layer": row["layer"],
            "direction": factor_result["direction"],
            "target_label": factor_result["target_label"],
        }

        if row["v3_status"] == "keep_final":
            base_rows.append(metadata_row)
            enhanced_rows.append(metadata_row)
        elif row["v3_status"] == "keep_enhancement":
            enhanced_rows.append(metadata_row)

    return base_rows, enhanced_rows


def month_floor(ts: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=ts.year, month=ts.month, day=1)


def build_folds(dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    for start_idx in range(0, len(dates), FOLD_STEP):
        validation_dates = dates[start_idx : start_idx + VALIDATION_REBALANCE_COUNT]
        if len(validation_dates) < VALIDATION_REBALANCE_COUNT:
            continue
        validation_start = validation_dates[0]
        train_start = month_floor(validation_start) - pd.DateOffset(years=TRAIN_YEARS)
        train_dates = [d for d in dates if train_start <= d < validation_start]
        if len(train_dates) < MIN_TRAIN_REBALANCE_DATES:
            continue
        folds.append(
            {
                "fold_id": f"fold_{len(folds) + 1:02d}",
                "train_start": train_start.strftime("%Y-%m-%d"),
                "train_end": (validation_start - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "validation_start": validation_start.strftime("%Y-%m-%d"),
                "validation_end": validation_dates[-1].strftime("%Y-%m-%d"),
                "train_rebalance_dates": len(train_dates),
                "validation_rebalance_dates": len(validation_dates),
            }
        )
    return folds


def preprocess_factor(full_df: pd.DataFrame, train_mask: pd.Series, factor_name: str) -> pd.Series:
    values = pd.to_numeric(full_df[factor_name], errors="coerce")
    train_values = values[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=full_df.index, dtype="float64")
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = values.clip(lower=lower, upper=upper)
    train_clipped = clipped[train_mask].dropna()
    mean_value = float(train_clipped.mean())
    std_value = float(train_clipped.std(ddof=0))
    if std_value <= 0 or pd.isna(std_value):
        return pd.Series(index=full_df.index, dtype="float64")
    return (clipped - mean_value) / std_value


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def evaluate_score(df: pd.DataFrame, score_col: str, target_col: str, mask: pd.Series) -> dict[str, object]:
    window = df[mask].copy()
    window[score_col] = pd.to_numeric(window[score_col], errors="coerce")
    window[target_col] = pd.to_numeric(window[target_col], errors="coerce")
    window = window.dropna(subset=[score_col, target_col])

    ic_values: list[float] = []
    top_minus_bottom_values: list[float] = []
    positive_ic_count = 0

    for _, group in window.groupby("rebalance_date"):
        if len(group) < 5:
            continue
        ic = group[score_col].rank(method="average").corr(group[target_col].rank(method="average"), method="pearson")
        if pd.isna(ic):
            continue
        ic_values.append(float(ic))
        if ic > 0:
            positive_ic_count += 1

        group = group.copy()
        group["_bucket"] = assign_groups(group[score_col], 5)
        bucket_means = group.groupby("_bucket")[target_col].mean().to_dict()
        if 1 in bucket_means and 5 in bucket_means:
            top_minus_bottom_values.append(float(bucket_means[5] - bucket_means[1]))

    if not ic_values:
        return {
            "rows": len(window),
            "dates": int(window["rebalance_date"].nunique()),
            "rank_ic_mean": "",
            "rank_ic_ir": "",
            "positive_ic_ratio": "",
            "top_minus_bottom": "",
        }

    ic_array = np.array(ic_values, dtype=float)
    ic_mean = float(ic_array.mean())
    ic_std = float(ic_array.std(ddof=0))
    return {
        "rows": len(window),
        "dates": int(window["rebalance_date"].nunique()),
        "rank_ic_mean": round(ic_mean, 6),
        "rank_ic_ir": round(ic_mean / ic_std, 6) if ic_std > 1e-12 else "",
        "positive_ic_ratio": round(float(positive_ic_count / len(ic_values)), 6),
        "top_minus_bottom": round(float(np.mean(top_minus_bottom_values)), 8) if top_minus_bottom_values else "",
    }


def build_scored_panel(panel_df: pd.DataFrame, metadata_rows: list[dict[str, str]], train_mask: pd.Series) -> tuple[pd.DataFrame, dict[str, float], dict[str, list[str]]]:
    df = panel_df.copy()
    quarter_factors: list[str] = []
    year_factors: list[str] = []
    train_ic_weight_map: dict[str, float] = {}

    for row in metadata_rows:
        factor_name = row["factor_name"]
        z_col = f"z__{factor_name}"
        adj_col = f"adj__{factor_name}"
        df[z_col] = preprocess_factor(df, train_mask, factor_name)
        multiplier = 1.0 if row["direction"] == "larger_better" else -1.0
        df[adj_col] = df[z_col] * multiplier

        factor_metrics = evaluate_score(df, adj_col, row["target_label"], train_mask)
        train_ic = factor_metrics["rank_ic_mean"]
        train_ic_weight_map[adj_col] = abs(float(train_ic)) if train_ic != "" else 0.0

        if row["target_label"] == "y_year_avg_daily_return_close":
            year_factors.append(adj_col)
        else:
            quarter_factors.append(adj_col)

    return df, train_ic_weight_map, {
        "quarter_factors": quarter_factors,
        "year_factors": year_factors,
        "all_factors": quarter_factors + year_factors,
    }


def add_combo_scores(df: pd.DataFrame, train_ic_weight_map: dict[str, float], factor_groups: dict[str, list[str]]) -> pd.DataFrame:
    df = df.copy()
    all_factors = factor_groups["all_factors"]
    quarter_factors = factor_groups["quarter_factors"]
    year_factors = factor_groups["year_factors"]

    df["combo__equal_weight"] = df[all_factors].mean(axis=1, skipna=True)

    ic_total = sum(train_ic_weight_map.get(col, 0.0) for col in all_factors)
    if ic_total > 0:
        weighted_sum = None
        for col in all_factors:
            part = df[col] * (train_ic_weight_map.get(col, 0.0) / ic_total)
            weighted_sum = part if weighted_sum is None else weighted_sum + part
        df["combo__ic_weight_train"] = weighted_sum
    else:
        df["combo__ic_weight_train"] = np.nan

    quarterly_mean = df[quarter_factors].mean(axis=1, skipna=True) if quarter_factors else np.nan
    annual_mean = df[year_factors].mean(axis=1, skipna=True) if year_factors else np.nan
    if quarter_factors and year_factors:
        df["combo__quarterly_plus_annual"] = (quarterly_mean * 0.67) + (annual_mean * 0.33)
    elif quarter_factors:
        df["combo__quarterly_plus_annual"] = quarterly_mean
    else:
        df["combo__quarterly_plus_annual"] = annual_mean

    return df


def summarize_fold(df: pd.DataFrame, fold: dict[str, object], scenario_name: str, combo_name: str) -> dict[str, object]:
    train_start = pd.Timestamp(fold["train_start"])
    validation_start = pd.Timestamp(fold["validation_start"])
    validation_end = pd.Timestamp(fold["validation_end"])

    train_mask = (df["rebalance_date"] >= train_start) & (df["rebalance_date"] < validation_start)
    validation_mask = (df["rebalance_date"] >= validation_start) & (df["rebalance_date"] <= validation_end)

    train_metrics = evaluate_score(df, combo_name, "y_quarter_avg_daily_return_close", train_mask)
    validation_metrics = evaluate_score(df, combo_name, "y_quarter_avg_daily_return_close", validation_mask)

    return {
        "fold_id": fold["fold_id"],
        "scenario_name": scenario_name,
        "combo_name": combo_name,
        "train_start": fold["train_start"],
        "train_end": fold["train_end"],
        "validation_start": fold["validation_start"],
        "validation_end": fold["validation_end"],
        "train_rebalance_dates": fold["train_rebalance_dates"],
        "validation_rebalance_dates": fold["validation_rebalance_dates"],
        "train_rows": train_metrics["rows"],
        "train_dates": train_metrics["dates"],
        "train_rank_ic_mean": train_metrics["rank_ic_mean"],
        "train_rank_ic_ir": train_metrics["rank_ic_ir"],
        "train_positive_ic_ratio": train_metrics["positive_ic_ratio"],
        "train_top_minus_bottom": train_metrics["top_minus_bottom"],
        "validation_rows": validation_metrics["rows"],
        "validation_dates": validation_metrics["dates"],
        "validation_rank_ic_mean": validation_metrics["rank_ic_mean"],
        "validation_rank_ic_ir": validation_metrics["rank_ic_ir"],
        "validation_positive_ic_ratio": validation_metrics["positive_ic_ratio"],
        "validation_top_minus_bottom": validation_metrics["top_minus_bottom"],
    }


def build_result_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]], base_rows: list[dict[str, str]], enhanced_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    scenario_map = {
        SCENARIO_BASE: base_rows,
        SCENARIO_ENHANCED: enhanced_rows,
    }

    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)

        for scenario_name, metadata_rows in scenario_map.items():
            scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, metadata_rows, train_mask)
            scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)

            for combo_name in COMBO_NAMES:
                rows.append(summarize_fold(scored_df, fold, scenario_name, combo_name))
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def format_metric(value: object) -> str:
    if value == "" or pd.isna(value):
        return ""
    return str(value)


def write_summary(folds: list[dict[str, object]], result_rows: list[dict[str, object]], base_rows: list[dict[str, str]], enhanced_rows: list[dict[str, str]]) -> None:
    result_df = pd.DataFrame(result_rows)
    lines = [
        "# Pre-2021 Rolling Validation V1",
        "",
        "Protocol used in this first rolling framework:",
        f"- research cutoff: `{RESEARCH_END.strftime('%Y-%m-%d')}`",
        f"- train window: previous `{TRAIN_YEARS}` calendar years, month-aligned to the validation start month",
        f"- validation window: next `{VALIDATION_REBALANCE_COUNT}` rebalance dates",
        f"- fold step: `{FOLD_STEP}` rebalance dates",
        f"- minimum train history: `{MIN_TRAIN_REBALANCE_DATES}` rebalance dates",
        "- preprocessing and IC weights are fit inside each fold's train window only",
        "",
        "Scenarios:",
        f"- `{SCENARIO_BASE}`: `{len(base_rows)}` factors",
        f"- `{SCENARIO_ENHANCED}`: `{len(enhanced_rows)}` factors",
        "",
        f"- fold count: `{len(folds)}`",
        "",
        "Fold definitions:",
    ]

    for fold in folds:
        lines.append(
            f"- `{fold['fold_id']}` | train=`{fold['train_start']}` to `{fold['train_end']}` "
            f"| validation=`{fold['validation_start']}` to `{fold['validation_end']}` "
            f"| train_dates=`{fold['train_rebalance_dates']}` | val_dates=`{fold['validation_rebalance_dates']}`"
        )

    lines.extend(["", "Average validation results by scenario and combo:"])
    for scenario_name in [SCENARIO_BASE, SCENARIO_ENHANCED]:
        subset = result_df[result_df["scenario_name"] == scenario_name].copy()
        if subset.empty:
            continue
        scenario_summary = (
            subset.groupby("combo_name", dropna=False)
            .agg(
                fold_count=("fold_id", "count"),
                mean_validation_rank_ic_mean=("validation_rank_ic_mean", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_validation_rank_ic_ir=("validation_rank_ic_ir", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_validation_top_minus_bottom=("validation_top_minus_bottom", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_validation_positive_ic_ratio=("validation_positive_ic_ratio", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(
                ["mean_validation_rank_ic_mean", "mean_validation_top_minus_bottom"],
                ascending=[False, False],
            )
        )
        best_row = scenario_summary.iloc[0]
        lines.append(
            f"- `{scenario_name}` best combo: `{best_row['combo_name']}` | "
            f"mean_val_ic=`{round(float(best_row['mean_validation_rank_ic_mean']), 6)}` | "
            f"mean_val_spread=`{round(float(best_row['mean_validation_top_minus_bottom']), 8)}`"
        )
        for _, row in scenario_summary.iterrows():
            lines.append(
                f"- `{scenario_name}` `{row['combo_name']}` | folds=`{int(row['fold_count'])}` | "
                f"mean_val_ic=`{format_metric(round(float(row['mean_validation_rank_ic_mean']), 6))}` | "
                f"mean_val_ic_ir=`{format_metric(round(float(row['mean_validation_rank_ic_ir']), 6))}` | "
                f"mean_val_spread=`{format_metric(round(float(row['mean_validation_top_minus_bottom']), 8))}` | "
                f"mean_val_pos_ic_ratio=`{format_metric(round(float(row['mean_validation_positive_ic_ratio']), 6))}`"
            )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_FOLDS_PATH.name}]({OUTPUT_FOLDS_PATH})",
            f"- [{OUTPUT_RESULTS_PATH.name}]({OUTPUT_RESULTS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    base_rows, enhanced_rows = prepare_factor_metadata()

    dates = sorted(pd.to_datetime(panel_df["rebalance_date"].drop_duplicates()))
    pre2021_dates = [pd.Timestamp(d) for d in dates if pd.Timestamp(d) < RESEARCH_END]
    folds = build_folds(pre2021_dates)
    result_rows = build_result_rows(panel_df, folds, base_rows, enhanced_rows)

    write_csv(OUTPUT_FOLDS_PATH, folds)
    write_csv(OUTPUT_RESULTS_PATH, result_rows)
    write_summary(folds, result_rows, base_rows, enhanced_rows)

    print(OUTPUT_FOLDS_PATH)
    print(OUTPUT_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
