from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
STATE_SCORE_PATH = SCRIPT_DIR / "momentum_forward_state_score_v1.csv"
OUT_CSV_PATH = SCRIPT_DIR / "momentum_state_switch_validation_v1.csv"
OUT_MD_PATH = SCRIPT_DIR / "momentum_state_switch_validation_v1.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5
GROUP_COUNT = 5
HOLD_BUCKET = 5


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[(df[POOL_FLAG] == 1) & (df["rebalance_date"] < pd.Timestamp("2021-01-01"))].copy()
    for col in ["mom_6_1", "mom_12_1", TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_state_scores() -> pd.DataFrame:
    df = pd.read_csv(STATE_SCORE_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    return df[["rebalance_date", "state_score_v1"]].copy()


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def score_series(values: pd.Series) -> pd.Series:
    raw = pd.to_numeric(values, errors="coerce")
    non_null = raw.dropna()
    if non_null.empty:
        return pd.Series(index=raw.index, data=np.nan)
    lower = float(non_null.quantile(0.01))
    upper = float(non_null.quantile(0.99))
    clipped = raw.clip(lower=lower, upper=upper)
    clipped_non_null = clipped.dropna()
    if clipped_non_null.empty:
        return pd.Series(index=raw.index, data=np.nan)
    mean_value = float(clipped_non_null.mean())
    std_value = float(clipped_non_null.std(ddof=0))
    if pd.isna(std_value) or std_value <= 1e-12:
        return pd.Series(index=raw.index, data=np.nan)
    return (clipped - mean_value) / std_value


def build_monthly_returns(panel_df: pd.DataFrame, factor_col: str) -> pd.DataFrame:
    rows = []
    for rebalance_date, group in panel_df.groupby("rebalance_date", sort=True):
        work = group[[factor_col, TARGET_COL]].copy()
        work[factor_col] = pd.to_numeric(work[factor_col], errors="coerce")
        work[TARGET_COL] = pd.to_numeric(work[TARGET_COL], errors="coerce")
        work = work.dropna(subset=[factor_col, TARGET_COL])
        if len(work) < MIN_NAMES_PER_DATE:
            continue
        work["score"] = score_series(work[factor_col])
        work = work.dropna(subset=["score"]).copy()
        if len(work) < MIN_NAMES_PER_DATE:
            continue
        work["bucket"] = assign_groups(work["score"], GROUP_COUNT)
        work = work.dropna(subset=["bucket"]).copy()
        long_df = work[work["bucket"] == HOLD_BUCKET].copy()
        if len(long_df) == 0:
            continue
        rows.append(
            {
                "rebalance_date": rebalance_date,
                f"{factor_col}_portfolio_return": float(long_df[TARGET_COL].mean()),
                f"{factor_col}_name_count": int(len(long_df)),
            }
        )
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def build_switch_frame(panel_df: pd.DataFrame, state_df: pd.DataFrame) -> pd.DataFrame:
    mom6 = build_monthly_returns(panel_df, "mom_6_1")
    mom12 = build_monthly_returns(panel_df, "mom_12_1")
    out = state_df.merge(mom6, on="rebalance_date", how="left").merge(mom12, on="rebalance_date", how="left")

    q_low = float(out["state_score_v1"].quantile(0.33))
    q_high = float(out["state_score_v1"].quantile(0.67))
    out["state_bucket"] = np.where(
        out["state_score_v1"] >= q_high,
        "high_use_mom6",
        np.where(out["state_score_v1"] <= q_low, "low_use_mom12", "mid_use_mom12"),
    )
    out["selected_factor"] = np.where(out["state_bucket"] == "high_use_mom6", "mom_6_1", "mom_12_1")
    out["selected_return"] = np.where(
        out["selected_factor"] == "mom_6_1",
        out["mom_6_1_portfolio_return"],
        out["mom_12_1_portfolio_return"],
    )
    return out


def summarize_switch(out: pd.DataFrame) -> dict[str, object]:
    usable = out.dropna(subset=["selected_return"]).copy()
    if len(usable) == 0:
        return {}

    def annualized(ret: pd.Series) -> float:
        ret = pd.to_numeric(ret, errors="coerce").dropna()
        if len(ret) == 0:
            return np.nan
        nav = float((1.0 + ret).prod())
        years = len(ret) / 12.0
        if years <= 0 or nav <= 0:
            return np.nan
        return nav ** (1.0 / years) - 1.0

    return {
        "months": int(len(usable)),
        "switch_total_return": float((1.0 + usable["selected_return"]).prod() - 1.0),
        "switch_annualized_return": annualized(usable["selected_return"]),
        "mom6_total_return": float((1.0 + usable["mom_6_1_portfolio_return"].dropna()).prod() - 1.0),
        "mom12_total_return": float((1.0 + usable["mom_12_1_portfolio_return"].dropna()).prod() - 1.0),
        "mom6_annualized_return": annualized(usable["mom_6_1_portfolio_return"]),
        "mom12_annualized_return": annualized(usable["mom_12_1_portfolio_return"]),
        "high_bucket_months": int((usable["state_bucket"] == "high_use_mom6").sum()),
        "mid_bucket_months": int((usable["state_bucket"] == "mid_use_mom12").sum()),
        "low_bucket_months": int((usable["state_bucket"] == "low_use_mom12").sum()),
    }


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(summary: dict[str, object]) -> None:
    lines = [
        "# Momentum State Switch Validation V1",
        "",
        "Scope:",
        "- sample window: `2014-01-01` to `2020-12-31`",
        "- switching rule: high `state_score_v1` months use `mom_6_1`, all other months use `mom_12_1`",
        "- purpose: test whether a simple forward state filter can make medium-term momentum more deployable than pure `mom_6_1`",
        "",
        "Result summary:",
        f"- months: `{summary.get('months', 'nan')}`",
        f"- switch total return: `{format_float(summary.get('switch_total_return'))}`",
        f"- switch annualized return: `{format_float(summary.get('switch_annualized_return'))}`",
        f"- pure `mom_6_1` total return: `{format_float(summary.get('mom6_total_return'))}`",
        f"- pure `mom_6_1` annualized return: `{format_float(summary.get('mom6_annualized_return'))}`",
        f"- pure `mom_12_1` total return: `{format_float(summary.get('mom12_total_return'))}`",
        f"- pure `mom_12_1` annualized return: `{format_float(summary.get('mom12_annualized_return'))}`",
        f"- high-state months using `mom_6_1`: `{summary.get('high_bucket_months', 'nan')}`",
        f"- mid-state months using `mom_12_1`: `{summary.get('mid_bucket_months', 'nan')}`",
        f"- low-state months using `mom_12_1`: `{summary.get('low_bucket_months', 'nan')}`",
        "",
        "Interpretation:",
        "- if the switch line beats pure `mom_6_1`, then state filtering is a viable path for medium-term momentum deployment",
        "- if it also competes with or beats pure `mom_12_1`, then the state score is strong enough to justify further refinement",
        "- this remains a pre-2021 research validation, not an out-of-sample deployment result",
        "",
        "Output:",
        f"- [{OUT_CSV_PATH.name}]({OUT_CSV_PATH})",
    ]
    OUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    state_df = load_state_scores()
    out = build_switch_frame(panel_df, state_df)
    out.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8-sig")
    summary = summarize_switch(out)
    write_summary(summary)
    print(f"saved switch csv -> {OUT_CSV_PATH}")
    print(f"saved switch md -> {OUT_MD_PATH}")


if __name__ == "__main__":
    main()
