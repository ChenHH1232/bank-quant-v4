from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
RESULT_CSV_PATH = SCRIPT_DIR / "momentum_pre2021_mechanism_review_v1.csv"
SUMMARY_MD_PATH = SCRIPT_DIR / "momentum_pre2021_mechanism_review_v1.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5
FACTOR_COLS = ["mom_3_1", "mom_6_1", "mom_12_1"]
STYLE_COLS = [
    "log_avg_money",
    "log_avg_market_cap",
    "pb_ratio",
    "pe_ratio",
]


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df[POOL_FLAG] == 1].copy()
    df = df[df["rebalance_date"] < pd.Timestamp("2021-01-01")].copy()
    df["year"] = df["rebalance_date"].dt.year
    df["log_avg_money"] = np.log(pd.to_numeric(df["avg_money_20d_pre_rebalance"], errors="coerce").clip(lower=1.0))
    df["log_avg_market_cap"] = np.log(pd.to_numeric(df["avg_market_cap_20d_pre_rebalance"], errors="coerce").clip(lower=1.0))
    return df


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


def compute_spearman_like(x: pd.Series, y: pd.Series) -> float:
    rx = x.rank(method="average")
    ry = y.rank(method="average")
    value = rx.corr(ry, method="pearson")
    return float(value) if not pd.isna(value) else np.nan


def compute_year_factor_metrics(df: pd.DataFrame, factor_col: str) -> dict[str, object]:
    sample = df[["rebalance_date", factor_col, TARGET_COL]].copy()
    sample[factor_col] = pd.to_numeric(sample[factor_col], errors="coerce")
    sample[TARGET_COL] = pd.to_numeric(sample[TARGET_COL], errors="coerce")
    sample = sample.dropna(subset=[factor_col, TARGET_COL])

    per_date = []
    spreads = []
    for rebalance_date, group in sample.groupby("rebalance_date"):
        if len(group) < MIN_NAMES_PER_DATE:
            continue
        ic = compute_rank_ic(group[factor_col], group[TARGET_COL])
        if pd.isna(ic):
            continue
        per_date.append(float(ic))

        work = group.copy()
        work["_bucket"] = assign_groups(work[factor_col], 5)
        work = work.dropna(subset=["_bucket"])
        bucket_means = work.groupby("_bucket")[TARGET_COL].mean().to_dict()
        if 1 in bucket_means and 5 in bucket_means:
            spreads.append(float(bucket_means[5] - bucket_means[1]))

    if len(per_date) == 0:
        return {
            "usable_dates": 0,
            "rank_ic_mean": np.nan,
            "positive_ic_ratio": np.nan,
            "top_minus_bottom": np.nan,
        }

    ic_values = np.array(per_date, dtype=float)
    return {
        "usable_dates": int(len(per_date)),
        "rank_ic_mean": float(np.mean(ic_values)),
        "positive_ic_ratio": float((ic_values > 0).mean()),
        "top_minus_bottom": float(np.mean(spreads)) if len(spreads) > 0 else np.nan,
    }


def compute_year_style_metrics(df: pd.DataFrame, factor_col: str) -> dict[str, object]:
    metrics: dict[str, object] = {}
    for style_col in STYLE_COLS:
        corr_values = []
        sample = df[[factor_col, style_col, "rebalance_date"]].copy()
        sample[factor_col] = pd.to_numeric(sample[factor_col], errors="coerce")
        sample[style_col] = pd.to_numeric(sample[style_col], errors="coerce")
        sample = sample.dropna(subset=[factor_col, style_col])
        for _, group in sample.groupby("rebalance_date"):
            if len(group) < MIN_NAMES_PER_DATE:
                continue
            corr = compute_spearman_like(group[factor_col], group[style_col])
            if not pd.isna(corr):
                corr_values.append(float(corr))
        metrics[f"{style_col}_spearman_mean"] = float(np.mean(corr_values)) if corr_values else np.nan
    return metrics


def build_review_table(panel_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    years = sorted(panel_df["year"].dropna().astype(int).unique().tolist())

    for year in years:
        year_df = panel_df[panel_df["year"] == year].copy()
        date_count = int(year_df["rebalance_date"].nunique())
        pool_rows = int(len(year_df))
        for factor_col in FACTOR_COLS:
            factor_metrics = compute_year_factor_metrics(year_df, factor_col)
            style_metrics = compute_year_style_metrics(year_df, factor_col)
            rows.append(
                {
                    "year": year,
                    "factor_name": factor_col,
                    "pool_rows": pool_rows,
                    "rebalance_dates": date_count,
                    **factor_metrics,
                    **style_metrics,
                }
            )
    return pd.DataFrame(rows)


def build_period_summary(review_df: pd.DataFrame) -> pd.DataFrame:
    train_df = review_df[review_df["year"].between(2015, 2019)].copy()
    val_df = review_df[review_df["year"] == 2020].copy()
    rows = []
    for factor_name in FACTOR_COLS:
        for period_name, sub_df in [("train_2015_2019", train_df), ("validation_2020", val_df), ("full_pre2021", review_df)]:
            one = sub_df[sub_df["factor_name"] == factor_name].copy()
            rows.append(
                {
                    "period": period_name,
                    "factor_name": factor_name,
                    "year_count": int(one["year"].nunique()),
                    "rank_ic_mean": float(one["rank_ic_mean"].mean()) if len(one) > 0 else np.nan,
                    "positive_ic_ratio": float(one["positive_ic_ratio"].mean()) if len(one) > 0 else np.nan,
                    "top_minus_bottom": float(one["top_minus_bottom"].mean()) if len(one) > 0 else np.nan,
                    "log_avg_money_spearman_mean": float(one["log_avg_money_spearman_mean"].mean()) if len(one) > 0 else np.nan,
                    "log_avg_market_cap_spearman_mean": float(one["log_avg_market_cap_spearman_mean"].mean()) if len(one) > 0 else np.nan,
                    "pb_ratio_spearman_mean": float(one["pb_ratio_spearman_mean"].mean()) if len(one) > 0 else np.nan,
                    "pe_ratio_spearman_mean": float(one["pe_ratio_spearman_mean"].mean()) if len(one) > 0 else np.nan,
                }
            )
    return pd.DataFrame(rows)


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(review_df: pd.DataFrame, period_df: pd.DataFrame) -> None:
    best_year_rows = []
    for year, sub_df in review_df.groupby("year"):
        ranked = sub_df.sort_values(["rank_ic_mean", "top_minus_bottom"], ascending=[False, False]).reset_index(drop=True)
        if len(ranked) == 0:
            continue
        top = ranked.iloc[0]
        best_year_rows.append(
            f"- `{int(year)}`: best=`{top['factor_name']}` | ic=`{format_float(top['rank_ic_mean'])}` | spread=`{format_float(top['top_minus_bottom'])}`"
        )

    period_lines = []
    for _, row in period_df.iterrows():
        period_lines.append(
            "- `{period}` | `{factor}` | ic=`{ic}` | pos=`{pos}` | spread=`{spread}` | rho_mcap=`{mcap}` | rho_liq=`{liq}` | rho_pb=`{pb}`".format(
                period=row["period"],
                factor=row["factor_name"],
                ic=format_float(row["rank_ic_mean"]),
                pos=format_float(row["positive_ic_ratio"]),
                spread=format_float(row["top_minus_bottom"]),
                mcap=format_float(row["log_avg_market_cap_spearman_mean"]),
                liq=format_float(row["log_avg_money_spearman_mean"]),
                pb=format_float(row["pb_ratio_spearman_mean"]),
            )
        )

    full_pre2021 = period_df[period_df["period"] == "full_pre2021"].copy()
    full_pre2021 = full_pre2021.sort_values(["rank_ic_mean", "top_minus_bottom"], ascending=[False, False]).reset_index(drop=True)

    lines = [
        "# Momentum Pre-2021 Mechanism Review V1",
        "",
        "Scope:",
        "- sample window: `2014-01-01` to `2020-12-31`",
        "- stock pool: monthly bank pool with `rebalance_stock_pool_flag_v2 == 1`",
        "- target: next monthly rebalance `close-to-close` total return",
        "- purpose: explain pre-2021 why `mom_6_1` looked strong in research while `mom_12_1` may have been more deployment-stable",
        "",
        "Overall factor ranking on full pre-2021 annual review averages:",
    ]

    for _, row in full_pre2021.iterrows():
        lines.append(
            "- `{factor}` | ic=`{ic}` | pos=`{pos}` | spread=`{spread}` | rho_mcap=`{mcap}` | rho_liq=`{liq}` | rho_pb=`{pb}`".format(
                factor=row["factor_name"],
                ic=format_float(row["rank_ic_mean"]),
                pos=format_float(row["positive_ic_ratio"]),
                spread=format_float(row["top_minus_bottom"]),
                mcap=format_float(row["log_avg_market_cap_spearman_mean"]),
                liq=format_float(row["log_avg_money_spearman_mean"]),
                pb=format_float(row["pb_ratio_spearman_mean"]),
            )
        )

    lines.extend(
        [
            "",
            "Period summary:",
            *period_lines,
            "",
            "Per-year best factor by rank IC:",
            *best_year_rows,
            "",
            "Interpretation hints:",
            "- if `mom_6_1` has better average pre-2021 IC but also stronger positive correlation with size or liquidity, it may be partly capturing style exposure rather than pure trend continuation",
            "- if `mom_12_1` is weaker in average IC but more stable across years or less style-loaded, it may behave like a slow bank-style filter",
            "- use this file as pre-2021 evidence only; do not mix it with repeated post-2021 out-of-sample tuning",
            "",
            "Outputs:",
            f"- [{RESULT_CSV_PATH.name}]({RESULT_CSV_PATH})",
        ]
    )

    SUMMARY_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    review_df = build_review_table(panel_df)
    review_df = review_df.sort_values(["year", "factor_name"]).reset_index(drop=True)
    review_df.to_csv(RESULT_CSV_PATH, index=False, encoding="utf-8-sig")

    period_df = build_period_summary(review_df)
    write_summary(review_df, period_df)

    print(f"saved review csv -> {RESULT_CSV_PATH}")
    print(f"saved summary md -> {SUMMARY_MD_PATH}")


if __name__ == "__main__":
    main()
