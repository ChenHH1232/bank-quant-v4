from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
OUT_SCORE_PATH = SCRIPT_DIR / "momentum_forward_state_score_v2.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "momentum_forward_state_score_v2.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5

SCORE_COMPONENTS = [
    ("cross_mcap_median", 1.0),
    ("cross_target_dispersion", 1.0),
    ("cross_mom6_top_bottom_spread", 1.0),
    ("cross_money_median", -1.0),
]


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[(df[POOL_FLAG] == 1) & (df["rebalance_date"] < pd.Timestamp("2021-01-01"))].copy()
    num_cols = [
        "mom_6_1",
        "mom_12_1",
        "avg_money_20d_pre_rebalance",
        "avg_market_cap_20d_pre_rebalance",
        TARGET_COL,
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
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


def build_proxy_table(panel_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rebalance_date, group in panel_df.groupby("rebalance_date", sort=True):
        if len(group) < MIN_NAMES_PER_DATE:
            continue
        mom6 = group["mom_6_1"].dropna()
        mom12 = group["mom_12_1"].dropna()
        target = group[TARGET_COL].dropna()
        money = group["avg_money_20d_pre_rebalance"].dropna()
        mcap = group["avg_market_cap_20d_pre_rebalance"].dropna()
        if len(mom6) < MIN_NAMES_PER_DATE or len(target) < MIN_NAMES_PER_DATE:
            continue
        rows.append(
            {
                "rebalance_date": rebalance_date,
                "forward_pool_mean_return": float(group[TARGET_COL].mean()),
                "cross_factor_ic_mom6": compute_rank_ic(group["mom_6_1"], group[TARGET_COL]),
                "cross_factor_ic_mom12": compute_rank_ic(group["mom_12_1"], group[TARGET_COL]),
                "cross_mcap_median": float(mcap.median()) if len(mcap) > 0 else np.nan,
                "cross_target_dispersion": float(target.quantile(0.8) - target.quantile(0.2)),
                "cross_mom6_top_bottom_spread": float(mom6.quantile(0.8) - mom6.quantile(0.2)) if len(mom6) > 0 else np.nan,
                "cross_money_median": float(money.median()) if len(money) > 0 else np.nan,
                "cross_mom6_positive_ratio": float((mom6 > 0).mean()),
                "cross_mom6_mean": float(mom6.mean()) if len(mom6) > 0 else np.nan,
                "cross_mom6_median": float(mom6.median()) if len(mom6) > 0 else np.nan,
                "cross_money_mean": float(money.mean()) if len(money) > 0 else np.nan,
                "cross_mom12_median": float(mom12.median()) if len(mom12) > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def add_state_score(proxy_df: pd.DataFrame) -> pd.DataFrame:
    out = proxy_df.copy()
    parts = []
    for col, sign in SCORE_COMPONENTS:
        values = pd.to_numeric(out[col], errors="coerce")
        mean_value = float(values.mean())
        std_value = float(values.std(ddof=0))
        if pd.isna(std_value) or std_value <= 1e-12:
            z = pd.Series(index=values.index, data=np.nan)
        else:
            z = (values - mean_value) / std_value
        out[f"z__{col}"] = z
        parts.append(z * float(sign))
    out["state_score_v2"] = sum(parts) / float(len(parts))
    return out


def evaluate_score(df: pd.DataFrame, score_col: str) -> dict[str, object]:
    sample = df[[score_col, "forward_pool_mean_return", "cross_factor_ic_mom6", "cross_factor_ic_mom12"]].dropna(subset=[score_col]).copy()
    sample["_bucket"] = assign_groups(sample[score_col], 3)
    top = sample[sample["_bucket"] == 3]
    bottom = sample[sample["_bucket"] == 1]
    return {
        "score_col": score_col,
        "corr_forward_mean": float(sample[score_col].corr(sample["forward_pool_mean_return"])) if sample["forward_pool_mean_return"].notna().sum() > 1 else np.nan,
        "corr_mom6_ic": float(sample[score_col].corr(sample["cross_factor_ic_mom6"])) if sample["cross_factor_ic_mom6"].notna().sum() > 1 else np.nan,
        "corr_mom12_ic": float(sample[score_col].corr(sample["cross_factor_ic_mom12"])) if sample["cross_factor_ic_mom12"].notna().sum() > 1 else np.nan,
        "top_third_forward_mean": float(top["forward_pool_mean_return"].mean()) if len(top) > 0 else np.nan,
        "bottom_third_forward_mean": float(bottom["forward_pool_mean_return"].mean()) if len(bottom) > 0 else np.nan,
        "top_third_mom6_ic": float(top["cross_factor_ic_mom6"].mean()) if len(top) > 0 else np.nan,
        "bottom_third_mom6_ic": float(bottom["cross_factor_ic_mom6"].mean()) if len(bottom) > 0 else np.nan,
        "top_third_mom12_ic": float(top["cross_factor_ic_mom12"].mean()) if len(top) > 0 else np.nan,
        "bottom_third_mom12_ic": float(bottom["cross_factor_ic_mom12"].mean()) if len(bottom) > 0 else np.nan,
    }


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(eval_row: dict[str, object]) -> None:
    component_lines = [f"- `{col}` with sign `{int(sign)}`" for col, sign in SCORE_COMPONENTS]
    gap = np.nan
    if not pd.isna(eval_row["corr_mom6_ic"]) and not pd.isna(eval_row["corr_mom12_ic"]):
        gap = float(eval_row["corr_mom6_ic"]) - float(eval_row["corr_mom12_ic"])
    lines = [
        "# Momentum Forward State Score V2",
        "",
        "Scope:",
        "- sample window: `2014-01-01` to `2020-12-31`",
        "- objective: build a more `mom_6_1`-specific forward state score than V1",
        "- selection logic: keep only components that looked helpful in rolling switch testing and avoid pushing too much weight onto broad momentum breadth",
        "",
        "Score construction:",
        *component_lines,
        "",
        "Composite score results:",
        f"- corr to next-period pool mean return: `{format_float(eval_row['corr_forward_mean'])}`",
        f"- corr to next-period `mom_6_1` IC: `{format_float(eval_row['corr_mom6_ic'])}`",
        f"- corr to next-period `mom_12_1` IC: `{format_float(eval_row['corr_mom12_ic'])}`",
        f"- `mom_6_1` minus `mom_12_1` IC correlation gap: `{format_float(gap)}`",
        f"- top-third score months avg forward return: `{format_float(eval_row['top_third_forward_mean'])}`",
        f"- bottom-third score months avg forward return: `{format_float(eval_row['bottom_third_forward_mean'])}`",
        f"- top-third score months avg `mom_6_1` IC: `{format_float(eval_row['top_third_mom6_ic'])}`",
        f"- bottom-third score months avg `mom_6_1` IC: `{format_float(eval_row['bottom_third_mom6_ic'])}`",
        f"- top-third score months avg `mom_12_1` IC: `{format_float(eval_row['top_third_mom12_ic'])}`",
        f"- bottom-third score months avg `mom_12_1` IC: `{format_float(eval_row['bottom_third_mom12_ic'])}`",
        "",
        "Interpretation:",
        "- compared with V1, this version is intended to sharpen the high-state month definition rather than broaden it",
        "- `cross_mom6_top_bottom_spread` is kept because it better reflects cross-sectional medium-term momentum separation",
        "- this score still remains a research-layer score until the rolling switch test confirms promotion value",
        "",
        "Output:",
        f"- [{OUT_SCORE_PATH.name}]({OUT_SCORE_PATH})",
    ]
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    proxy_df = build_proxy_table(panel_df)
    score_df = add_state_score(proxy_df)
    score_df.to_csv(OUT_SCORE_PATH, index=False, encoding="utf-8-sig")
    eval_row = evaluate_score(score_df, "state_score_v2")
    write_summary(eval_row)
    print(f"saved score csv -> {OUT_SCORE_PATH}")
    print(f"saved score md -> {OUT_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
