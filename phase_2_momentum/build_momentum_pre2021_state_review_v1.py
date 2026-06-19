from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
OUT_CSV_PATH = SCRIPT_DIR / "momentum_pre2021_state_review_v1.csv"
OUT_MD_PATH = SCRIPT_DIR / "momentum_pre2021_state_review_v1.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5
FACTOR_COLS = ["mom_3_1", "mom_6_1", "mom_12_1"]


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[(df[POOL_FLAG] == 1) & (df["rebalance_date"] < pd.Timestamp("2021-01-01"))].copy()
    df["year"] = df["rebalance_date"].dt.year
    return df


def classify_year_state(avg_forward_return: float) -> str:
    if pd.isna(avg_forward_return):
        return "unknown"
    if avg_forward_return >= 0.01:
        return "trend_up"
    if avg_forward_return < 0.0:
        return "weak_down"
    return "mixed_flat"


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


def build_year_state_table(panel_df: pd.DataFrame) -> pd.DataFrame:
    monthly_pool = (
        panel_df.groupby("rebalance_date")[TARGET_COL]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "pool_forward_mean", "median": "pool_forward_median", "count": "name_count"})
    )
    monthly_pool["year"] = monthly_pool["rebalance_date"].dt.year
    year_state = (
        monthly_pool.groupby("year")
        .agg(
            avg_month_forward_return=("pool_forward_mean", "mean"),
            median_month_forward_return=("pool_forward_mean", "median"),
            positive_month_ratio=("pool_forward_mean", lambda s: float((pd.to_numeric(s, errors="coerce") > 0).mean())),
            month_count=("rebalance_date", "count"),
        )
        .reset_index()
    )
    year_state["year_state"] = year_state["avg_month_forward_return"].apply(classify_year_state)
    return year_state


def compute_factor_metrics(df: pd.DataFrame, factor_col: str) -> dict[str, object]:
    sample = df[["rebalance_date", factor_col, TARGET_COL]].copy()
    sample[factor_col] = pd.to_numeric(sample[factor_col], errors="coerce")
    sample[TARGET_COL] = pd.to_numeric(sample[TARGET_COL], errors="coerce")
    sample = sample.dropna(subset=[factor_col, TARGET_COL])

    ic_list = []
    spread_list = []
    for _, group in sample.groupby("rebalance_date"):
        if len(group) < MIN_NAMES_PER_DATE:
            continue
        ic = compute_rank_ic(group[factor_col], group[TARGET_COL])
        if pd.isna(ic):
            continue
        ic_list.append(float(ic))
        work = group.copy()
        work["_bucket"] = assign_groups(work[factor_col], 5)
        work = work.dropna(subset=["_bucket"])
        bucket_means = work.groupby("_bucket")[TARGET_COL].mean().to_dict()
        if 1 in bucket_means and 5 in bucket_means:
            spread_list.append(float(bucket_means[5] - bucket_means[1]))

    if len(ic_list) == 0:
        return {
            "usable_dates": 0,
            "rank_ic_mean": np.nan,
            "positive_ic_ratio": np.nan,
            "top_minus_bottom": np.nan,
        }
    ic_values = np.array(ic_list, dtype=float)
    return {
        "usable_dates": int(len(ic_values)),
        "rank_ic_mean": float(np.mean(ic_values)),
        "positive_ic_ratio": float((ic_values > 0).mean()),
        "top_minus_bottom": float(np.mean(spread_list)) if len(spread_list) > 0 else np.nan,
    }


def build_state_factor_table(panel_df: pd.DataFrame, year_state_df: pd.DataFrame) -> pd.DataFrame:
    merged = panel_df.merge(year_state_df[["year", "year_state"]], on="year", how="left")
    rows: list[dict[str, object]] = []
    for state_name, state_df in merged.groupby("year_state"):
        for factor_col in FACTOR_COLS:
            metrics = compute_factor_metrics(state_df, factor_col)
            rows.append(
                {
                    "slice_type": "state",
                    "slice_name": state_name,
                    "factor_name": factor_col,
                    "years": "|".join(str(int(y)) for y in sorted(state_df["year"].dropna().unique().tolist())),
                    "pool_rows": int(len(state_df)),
                    **metrics,
                }
            )
    for year, year_df in merged.groupby("year"):
        for factor_col in FACTOR_COLS:
            metrics = compute_factor_metrics(year_df, factor_col)
            rows.append(
                {
                    "slice_type": "year",
                    "slice_name": str(int(year)),
                    "factor_name": factor_col,
                    "years": str(int(year)),
                    "pool_rows": int(len(year_df)),
                    **metrics,
                }
            )
    return pd.DataFrame(rows)


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(year_state_df: pd.DataFrame, state_factor_df: pd.DataFrame) -> None:
    year_lines = []
    for _, row in year_state_df.sort_values("year").iterrows():
        year_lines.append(
            "- `{year}` | state=`{state}` | avg_month_forward=`{avg}` | positive_month_ratio=`{pos}`".format(
                year=int(row["year"]),
                state=row["year_state"],
                avg=format_float(row["avg_month_forward_return"]),
                pos=format_float(row["positive_month_ratio"]),
            )
        )

    state_lines = []
    for state_name in ["trend_up", "mixed_flat", "weak_down"]:
        sub = state_factor_df[(state_factor_df["slice_type"] == "state") & (state_factor_df["slice_name"] == state_name)].copy()
        sub = sub.sort_values(["rank_ic_mean", "top_minus_bottom"], ascending=[False, False])
        for _, row in sub.iterrows():
            state_lines.append(
                "- `{state}` | `{factor}` | years=`{years}` | ic=`{ic}` | pos=`{pos}` | spread=`{spread}`".format(
                    state=state_name,
                    factor=row["factor_name"],
                    years=row["years"],
                    ic=format_float(row["rank_ic_mean"]),
                    pos=format_float(row["positive_ic_ratio"]),
                    spread=format_float(row["top_minus_bottom"]),
                )
            )

    lines = [
        "# Momentum Pre-2021 State Review V1",
        "",
        "Scope:",
        "- sample window: `2014-01-01` to `2020-12-31`",
        "- classification unit: annual state buckets built from monthly bank-pool average forward returns",
        "- state rule: `trend_up` if annual average monthly forward return >= 1%, `weak_down` if < 0, otherwise `mixed_flat`",
        "",
        "Year-state classification:",
        *year_lines,
        "",
        "Factor performance by state bucket:",
        *state_lines,
        "",
        "Interpretation:",
        "- if `mom_6_1` is clearly strongest only inside `trend_up` years, then its research edge is state-dependent rather than all-weather",
        "- if `mom_12_1` is less explosive but relatively less damaged in `mixed_flat` or `weak_down` years, it supports the slow-style-filter interpretation",
        "- this review is still pre-2021 only and can be used for mechanism explanation without contaminating the out-of-sample deployment window",
        "",
        "Outputs:",
        f"- [{OUT_CSV_PATH.name}]({OUT_CSV_PATH})",
    ]
    OUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    year_state_df = build_year_state_table(panel_df)
    state_factor_df = build_state_factor_table(panel_df, year_state_df)
    merged_out = state_factor_df.sort_values(["slice_type", "slice_name", "factor_name"]).reset_index(drop=True)
    merged_out.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8-sig")
    write_summary(year_state_df, merged_out)
    print(f"saved state csv -> {OUT_CSV_PATH}")
    print(f"saved state md -> {OUT_MD_PATH}")


if __name__ == "__main__":
    main()
