import csv
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
CORE_RESULTS_PATH = SCRIPT_DIR / "single_factor_test_results_core_v2.csv"
CORE_POOL_PATH = SCRIPT_DIR / "final_core_factor_pool_v2_trimmed.csv"
OUTPUT_PANEL_PATH = SCRIPT_DIR / "multifactor_core_v2_panel.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "multifactor_core_v2_summary.md"

TRAIN_START = pd.Timestamp("2014-05-01")
TRAIN_END = pd.Timestamp("2019-05-01")
VALIDATION_START = pd.Timestamp("2019-05-01")
VALIDATION_END = pd.Timestamp("2021-05-01")


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_stock_pool_flag"].astype(str) == "1"].copy()
    return df


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def prepare_factor_metadata() -> list[dict[str, str]]:
    pool_rows = load_rows(CORE_POOL_PATH)
    result_rows = {row["factor_name"]: row for row in load_rows(CORE_RESULTS_PATH)}
    final_keep = []
    for row in pool_rows:
        if row["final_status"] != "keep_final":
            continue
        factor_name = row["factor_name"]
        result_row = result_rows[factor_name]
        final_keep.append(
            {
                "factor_name": factor_name,
                "factor_family": row["factor_family"],
                "target_label": result_row["target_label"],
                "direction": result_row["direction"],
                "validation_rank_ic_mean": result_row["validation_rank_ic_mean"],
            }
        )
    return final_keep


def preprocess_factor(full_df: pd.DataFrame, train_mask: pd.Series, factor_name: str) -> pd.Series:
    values = pd.to_numeric(full_df[factor_name], errors="coerce")
    train_values = values[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=full_df.index, dtype="float64")
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = values.clip(lower=lower, upper=upper)
    mean_value = float(clipped[train_mask].dropna().mean())
    std_value = float(clipped[train_mask].dropna().std(ddof=0))
    if std_value <= 0 or pd.isna(std_value):
        return pd.Series(index=full_df.index, dtype="float64")
    z = (clipped - mean_value) / std_value
    return z


def build_scored_panel(panel_df: pd.DataFrame, metadata_rows: list[dict[str, str]]) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    df = panel_df.copy()
    train_mask = (df["rebalance_date"] >= TRAIN_START) & (df["rebalance_date"] < TRAIN_END)

    quarter_factors: list[str] = []
    year_factors: list[str] = []
    for row in metadata_rows:
        factor_name = row["factor_name"]
        z_col = f"z__{factor_name}"
        adj_col = f"adj__{factor_name}"
        df[z_col] = preprocess_factor(df, train_mask, factor_name)
        direction_multiplier = 1.0 if row["direction"] == "larger_better" else -1.0
        df[adj_col] = df[z_col] * direction_multiplier
        if row["target_label"] == "y_year_avg_daily_return_close":
            year_factors.append(adj_col)
        else:
            quarter_factors.append(adj_col)

    equal_weight_factors = quarter_factors + year_factors
    ic_weight_map = {
        f"adj__{row['factor_name']}": abs(float(row["validation_rank_ic_mean"])) for row in metadata_rows
    }

    df["combo__equal_weight"] = df[equal_weight_factors].mean(axis=1, skipna=True)

    ic_total = sum(ic_weight_map[col] for col in equal_weight_factors if col in ic_weight_map)
    if ic_total > 0:
        weighted_sum = None
        for col in equal_weight_factors:
            part = df[col] * (ic_weight_map[col] / ic_total)
            weighted_sum = part if weighted_sum is None else (weighted_sum + part)
        df["combo__ic_weight"] = weighted_sum
    else:
        df["combo__ic_weight"] = np.nan

    # Annual bank indicators change slowly, so this mixed score gives the quarterly block
    # the dominant weight while still letting the annual block participate.
    quarterly_mean = df[quarter_factors].mean(axis=1, skipna=True) if quarter_factors else np.nan
    annual_mean = df[year_factors].mean(axis=1, skipna=True) if year_factors else np.nan
    if quarter_factors and year_factors:
        df["combo__quarterly_plus_annual"] = (quarterly_mean * 0.67) + (annual_mean * 0.33)
    elif quarter_factors:
        df["combo__quarterly_plus_annual"] = quarterly_mean
    else:
        df["combo__quarterly_plus_annual"] = annual_mean

    return df, {
        "quarter_factors": quarter_factors,
        "year_factors": year_factors,
        "all_factors": equal_weight_factors,
    }


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def evaluate_combo(df: pd.DataFrame, score_col: str, target_col: str, start: pd.Timestamp, end: pd.Timestamp) -> dict[str, object]:
    window = df[(df["rebalance_date"] >= start) & (df["rebalance_date"] < end)].copy()
    window[score_col] = pd.to_numeric(window[score_col], errors="coerce")
    window[target_col] = pd.to_numeric(window[target_col], errors="coerce")
    window = window.dropna(subset=[score_col, target_col])

    ic_values: list[float] = []
    top_minus_bottom: list[float] = []
    top_group_returns: list[float] = []
    bottom_group_returns: list[float] = []

    for _, group in window.groupby("rebalance_date"):
        if len(group) < 5:
            continue
        ic = group[score_col].rank(method="average").corr(group[target_col].rank(method="average"), method="pearson")
        if pd.isna(ic):
            continue
        ic_values.append(float(ic))
        group = group.copy()
        group["_bucket"] = assign_groups(group[score_col], 5)
        bucket_means = group.groupby("_bucket")[target_col].mean().to_dict()
        if 1 in bucket_means and 5 in bucket_means:
            top_group_returns.append(float(bucket_means[5]))
            bottom_group_returns.append(float(bucket_means[1]))
            top_minus_bottom.append(float(bucket_means[5] - bucket_means[1]))

    if not ic_values:
        return {
            "rows": len(window),
            "dates": window["rebalance_date"].nunique(),
            "rank_ic_mean": "",
            "rank_ic_ir": "",
            "top_minus_bottom": "",
            "top_group_mean": "",
            "bottom_group_mean": "",
        }

    ic_array = np.array(ic_values, dtype=float)
    ic_mean = float(ic_array.mean())
    ic_std = float(ic_array.std(ddof=0))
    return {
        "rows": len(window),
        "dates": window["rebalance_date"].nunique(),
        "rank_ic_mean": round(ic_mean, 6),
        "rank_ic_ir": round(ic_mean / ic_std, 6) if ic_std > 0 else "",
        "top_minus_bottom": round(float(np.mean(top_minus_bottom)), 8) if top_minus_bottom else "",
        "top_group_mean": round(float(np.mean(top_group_returns)), 8) if top_group_returns else "",
        "bottom_group_mean": round(float(np.mean(bottom_group_returns)), 8) if bottom_group_returns else "",
    }


def write_panel(df: pd.DataFrame) -> None:
    keep_cols = [
        "rebalance_date",
        "code",
        "y_quarter_avg_daily_return_close",
        "y_year_avg_daily_return_close",
        "combo__equal_weight",
        "combo__ic_weight",
        "combo__quarterly_plus_annual",
    ]
    z_cols = [col for col in df.columns if col.startswith("adj__")]
    out = df[keep_cols + z_cols].copy()
    out.to_csv(OUTPUT_PANEL_PATH, index=False, encoding="utf-8-sig")


def write_summary(metadata_rows: list[dict[str, str]], factor_groups: dict[str, list[str]], summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Multifactor Core V2 Summary",
        "",
        "Core factors used:",
    ]
    for row in metadata_rows:
        lines.append(f"- `{row['factor_name']}` | target=`{row['target_label']}` | direction=`{row['direction']}`")
    lines.extend(
        [
            "",
            f"- Quarterly factor count: `{len(factor_groups['quarter_factors'])}`",
            f"- Annual factor count: `{len(factor_groups['year_factors'])}`",
            "",
            "Combo evaluation:",
        ]
    )
    for row in summary_rows:
        lines.append(
            f"- `{row['combo_name']}` `{row['window_name']}` | ic=`{row['rank_ic_mean']}` | ic_ir=`{row['rank_ic_ir']}` | top-bottom=`{row['top_minus_bottom']}`"
        )
    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_PANEL_PATH.name}]({OUTPUT_PANEL_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_df = load_panel(PANEL_PATH)
    metadata_rows = prepare_factor_metadata()
    scored_df, factor_groups = build_scored_panel(panel_df, metadata_rows)
    write_panel(scored_df)

    summary_rows: list[dict[str, object]] = []
    combo_targets = {
        "combo__equal_weight": "y_quarter_avg_daily_return_close",
        "combo__ic_weight": "y_quarter_avg_daily_return_close",
        "combo__quarterly_plus_annual": "y_quarter_avg_daily_return_close",
    }
    for combo_name, target_col in combo_targets.items():
        train_metrics = evaluate_combo(scored_df, combo_name, target_col, TRAIN_START, TRAIN_END)
        train_metrics["combo_name"] = combo_name
        train_metrics["window_name"] = "train"
        summary_rows.append(train_metrics)

        validation_metrics = evaluate_combo(scored_df, combo_name, target_col, VALIDATION_START, VALIDATION_END)
        validation_metrics["combo_name"] = combo_name
        validation_metrics["window_name"] = "validation"
        summary_rows.append(validation_metrics)

    write_summary(metadata_rows, factor_groups, summary_rows)
    print(f"factors={len(metadata_rows)}")
    print(OUTPUT_PANEL_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
