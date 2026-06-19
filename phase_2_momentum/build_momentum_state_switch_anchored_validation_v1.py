from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
STATE_SCORE_PATH = SCRIPT_DIR / "momentum_forward_state_score_v1.csv"
OUT_CSV_PATH = SCRIPT_DIR / "momentum_state_switch_anchored_validation_v1.csv"
OUT_MD_PATH = SCRIPT_DIR / "momentum_state_switch_anchored_validation_v1.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5
GROUP_COUNT = 5
HOLD_BUCKET = 5

TRAIN_END = pd.Timestamp("2018-12-31")
VALIDATION_START = pd.Timestamp("2019-01-01")
VALIDATION_END = pd.Timestamp("2019-12-31")
REVIEW_START = pd.Timestamp("2020-01-01")
REVIEW_END = pd.Timestamp("2020-12-31")


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
        if long_df.empty:
            continue
        rows.append(
            {
                "rebalance_date": rebalance_date,
                f"{factor_col}_portfolio_return": float(long_df[TARGET_COL].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def annualized(values: pd.Series) -> float:
    vals = pd.to_numeric(values, errors="coerce").dropna()
    if len(vals) == 0:
        return np.nan
    nav = float((1.0 + vals).prod())
    years = len(vals) / 12.0
    if years <= 0 or nav <= 0:
        return np.nan
    return nav ** (1.0 / years) - 1.0


def summarize_period(df: pd.DataFrame, col: str) -> dict[str, object]:
    vals = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(vals) == 0:
        return {"months": 0, "total_return": np.nan, "annualized_return": np.nan}
    return {
        "months": int(len(vals)),
        "total_return": float((1.0 + vals).prod() - 1.0),
        "annualized_return": annualized(vals),
    }


def main() -> None:
    panel_df = load_panel()
    state_df = load_state_scores()
    mom6_df = build_monthly_returns(panel_df, "mom_6_1")
    mom12_df = build_monthly_returns(panel_df, "mom_12_1")
    out = state_df.merge(mom6_df, on="rebalance_date", how="left").merge(mom12_df, on="rebalance_date", how="left")

    train_scores = pd.to_numeric(out.loc[out["rebalance_date"] <= TRAIN_END, "state_score_v1"], errors="coerce").dropna()
    q_low = float(train_scores.quantile(0.33))
    q_high = float(train_scores.quantile(0.67))

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

    out["period"] = np.where(
        (out["rebalance_date"] >= VALIDATION_START) & (out["rebalance_date"] <= VALIDATION_END),
        "validation_2019",
        np.where(
            (out["rebalance_date"] >= REVIEW_START) & (out["rebalance_date"] <= REVIEW_END),
            "review_2020",
            np.where(out["rebalance_date"] <= TRAIN_END, "train_2015_2018", "other"),
        ),
    )

    validation_df = out[out["period"] == "validation_2019"].copy()
    review_df = out[out["period"] == "review_2020"].copy()

    val_switch = summarize_period(validation_df, "selected_return")
    val_mom6 = summarize_period(validation_df, "mom_6_1_portfolio_return")
    val_mom12 = summarize_period(validation_df, "mom_12_1_portfolio_return")
    rev_switch = summarize_period(review_df, "selected_return")
    rev_mom6 = summarize_period(review_df, "mom_6_1_portfolio_return")
    rev_mom12 = summarize_period(review_df, "mom_12_1_portfolio_return")

    out.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8-sig")

    lines = [
        "# Momentum State Switch Anchored Validation V1",
        "",
        "Protocol:",
        "- train period: `2015-01` to `2018-12`",
        "- validation period: `2019-01` to `2019-12`",
        "- review period: `2020-01` to `2020-12`",
        "- thresholds are estimated only from the train-period `state_score_v1` distribution",
        "- switching rule: high state uses `mom_6_1`, otherwise use `mom_12_1`",
        "",
        "Train thresholds:",
        f"- q33=`{q_low:.6f}`",
        f"- q67=`{q_high:.6f}`",
        "",
        "Validation 2019:",
        f"- switch total return=`{val_switch['total_return']:.6f}`",
        f"- switch annualized=`{val_switch['annualized_return']:.6f}`",
        f"- pure mom_6_1 total return=`{val_mom6['total_return']:.6f}`",
        f"- pure mom_12_1 total return=`{val_mom12['total_return']:.6f}`",
        f"- high-state months=`{int((validation_df['state_bucket'] == 'high_use_mom6').sum())}`",
        "",
        "Review 2020:",
        f"- switch total return=`{rev_switch['total_return']:.6f}`",
        f"- switch annualized=`{rev_switch['annualized_return']:.6f}`",
        f"- pure mom_6_1 total return=`{rev_mom6['total_return']:.6f}`",
        f"- pure mom_12_1 total return=`{rev_mom12['total_return']:.6f}`",
        f"- high-state months=`{int((review_df['state_bucket'] == 'high_use_mom6').sum())}`",
        "",
        "Interpretation:",
        "- if the switch line beats pure `mom_6_1` in both 2019 validation and 2020 review, the state filter has real promise",
        "- if it only helps in validation but not review, the score is still informative but not robust enough yet",
        "",
        "Output:",
        f"- [{OUT_CSV_PATH.name}]({OUT_CSV_PATH})",
    ]
    OUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_CSV_PATH)
    print(OUT_MD_PATH)


if __name__ == "__main__":
    main()
