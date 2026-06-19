from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
MONTHLY_PANEL_PATH = SCRIPT_DIR / "mean_reversion_monthly_rebalance_panel_v1.csv"
OUT_CSV_PATH = SCRIPT_DIR / "mean_reversion_anchored_validation_v1.csv"
OUT_MD_PATH = SCRIPT_DIR / "mean_reversion_anchored_validation_v1.md"

TRAIN_END = pd.Timestamp("2018-12-31")
VALIDATION_START = pd.Timestamp("2019-01-01")
VALIDATION_END = pd.Timestamp("2019-12-31")
REVIEW_START = pd.Timestamp("2020-01-01")
REVIEW_END = pd.Timestamp("2020-12-31")
TARGET_COL = "y_month_total_return_close"
GROUP_COUNT = 5
HOLD_BUCKET = 5


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(MONTHLY_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    return df[df["mean_reversion_ready_v1"] == 1].copy()


def score_series_with_train(values: pd.Series, train_mask: pd.Series) -> pd.Series:
    raw = pd.to_numeric(values, errors="coerce")
    train_values = raw[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=raw.index, data=np.nan)
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = raw.clip(lower=lower, upper=upper)
    train_clipped = clipped[train_mask].dropna()
    mean_value = float(train_clipped.mean())
    std_value = float(train_clipped.std(ddof=0))
    if pd.isna(std_value) or std_value <= 1e-12:
        return pd.Series(index=raw.index, data=np.nan)
    return (clipped - mean_value) / std_value


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def build_monthly_returns(panel_df: pd.DataFrame) -> pd.DataFrame:
    panel_df = panel_df.copy()
    train_mask_full = panel_df["rebalance_date"] <= TRAIN_END
    panel_df["z_rev_5d"] = score_series_with_train(panel_df["rev_5d"], train_mask_full)
    panel_df["z_abnvol"] = score_series_with_train(panel_df["abnormal_volume_ratio"], train_mask_full)
    panel_df["score_rev5_abnvol"] = (-0.7 * panel_df["z_rev_5d"] + 0.3 * panel_df["z_abnvol"]) / 1.0
    panel_df["score_rev_5d"] = -1.0 * panel_df["z_rev_5d"]

    rows = []
    for rebalance_date, group in panel_df.groupby("rebalance_date", sort=True):
        work = group[["score_rev5_abnvol", "score_rev_5d", TARGET_COL]].copy()
        work[TARGET_COL] = pd.to_numeric(work[TARGET_COL], errors="coerce")

        combo = work.dropna(subset=["score_rev5_abnvol", TARGET_COL]).copy()
        raw5 = work.dropna(subset=["score_rev_5d", TARGET_COL]).copy()
        if len(combo) >= 5:
            combo["bucket"] = assign_groups(combo["score_rev5_abnvol"], GROUP_COUNT)
            combo_long = combo[combo["bucket"] == HOLD_BUCKET].copy()
            combo_ret = float(combo_long[TARGET_COL].mean()) if len(combo_long) > 0 else np.nan
        else:
            combo_ret = np.nan
        if len(raw5) >= 5:
            raw5["bucket"] = assign_groups(raw5["score_rev_5d"], GROUP_COUNT)
            raw5_long = raw5[raw5["bucket"] == HOLD_BUCKET].copy()
            raw5_ret = float(raw5_long[TARGET_COL].mean()) if len(raw5_long) > 0 else np.nan
        else:
            raw5_ret = np.nan

        rows.append(
            {
                "rebalance_date": rebalance_date,
                "rev5_abnvol_return": combo_ret,
                "rev_5d_return": raw5_ret,
            }
        )
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def summarize(values: pd.Series) -> dict[str, float]:
    vals = pd.to_numeric(values, errors="coerce").dropna()
    if len(vals) == 0:
        return {"total_return": np.nan, "annualized_return": np.nan}
    total_return = float((1.0 + vals).prod() - 1.0)
    years = len(vals) / 12.0
    annualized_return = total_return if years == 1 else ((1.0 + total_return) ** (1.0 / years) - 1.0)
    return {"total_return": total_return, "annualized_return": annualized_return}


def main() -> None:
    panel_df = load_panel()
    monthly_ret = build_monthly_returns(panel_df)
    monthly_ret["period"] = np.where(
        (monthly_ret["rebalance_date"] >= VALIDATION_START) & (monthly_ret["rebalance_date"] <= VALIDATION_END),
        "validation_2019",
        np.where(
            (monthly_ret["rebalance_date"] >= REVIEW_START) & (monthly_ret["rebalance_date"] <= REVIEW_END),
            "review_2020",
            np.where(monthly_ret["rebalance_date"] <= TRAIN_END, "train_2015_2018", "other"),
        ),
    )

    validation_df = monthly_ret[monthly_ret["period"] == "validation_2019"].copy()
    review_df = monthly_ret[monthly_ret["period"] == "review_2020"].copy()
    val_combo = summarize(validation_df["rev5_abnvol_return"])
    val_raw = summarize(validation_df["rev_5d_return"])
    rev_combo = summarize(review_df["rev5_abnvol_return"])
    rev_raw = summarize(review_df["rev_5d_return"])

    monthly_ret.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8-sig")
    lines = [
        "# Mean Reversion Anchored Validation V1",
        "",
        "Protocol:",
        "- train period: `2015-01` to `2018-12`",
        "- validation period: `2019-01` to `2019-12`",
        "- review period: `2020-01` to `2020-12`",
        "- compare `rev5_abnvol` against raw `rev_5d` using train-period normalization only",
        "",
        "Validation 2019:",
        f"- `rev5_abnvol` total return=`{val_combo['total_return']:.6f}`",
        f"- raw `rev_5d` total return=`{val_raw['total_return']:.6f}`",
        "",
        "Review 2020:",
        f"- `rev5_abnvol` total return=`{rev_combo['total_return']:.6f}`",
        f"- raw `rev_5d` total return=`{rev_raw['total_return']:.6f}`",
        "",
        "Interpretation:",
        "- if `rev5_abnvol` beats raw `rev_5d` in both validation and review, then abnormal-volume filtering is a robust enhancement",
        "- if it only wins in validation but not review, then the enhancement is still promising but not yet robust enough",
        "",
        "Output:",
        f"- [{OUT_CSV_PATH.name}]({OUT_CSV_PATH})",
    ]
    OUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_CSV_PATH)
    print(OUT_MD_PATH)


if __name__ == "__main__":
    main()
