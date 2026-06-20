from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
STATE_SCORE_PATH = SCRIPT_DIR / "momentum_forward_state_score_v1.csv"
OUT_RESULTS_PATH = SCRIPT_DIR / "momentum_state_switch_midstate_test_v1.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "momentum_state_switch_midstate_test_v1.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5
GROUP_COUNT = 5
HOLD_BUCKET = 5
TRAIN_MONTHS = 48
TEST_MONTHS = 12

RULE_SPECS = [
    {
        "rule_name": "high_only_mom6_baseline",
        "high_factor": "mom_6_1",
        "mid_factor": "mom_12_1",
        "low_factor": "mom_12_1",
    },
    {
        "rule_name": "high_mid_use_mom6",
        "high_factor": "mom_6_1",
        "mid_factor": "mom_6_1",
        "low_factor": "mom_12_1",
    },
    {
        "rule_name": "high_use_mom6_low_blend",
        "high_factor": "mom_6_1",
        "mid_factor": "mom_12_1",
        "low_factor": "blend_50_50",
    },
    {
        "rule_name": "high_use_mom6_mid_blend",
        "high_factor": "mom_6_1",
        "mid_factor": "blend_50_50",
        "low_factor": "mom_12_1",
    },
    {
        "rule_name": "all_non_low_blend",
        "high_factor": "blend_50_50",
        "mid_factor": "blend_50_50",
        "low_factor": "mom_12_1",
    },
]


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
    return df[df["rebalance_date"] < pd.Timestamp("2021-01-01")][["rebalance_date", "state_score_v1"]].copy()


def build_folds(dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    span = TRAIN_MONTHS + TEST_MONTHS
    for start_idx in range(0, len(dates) - span + 1):
        train_dates = dates[start_idx : start_idx + TRAIN_MONTHS]
        test_dates = dates[start_idx + TRAIN_MONTHS : start_idx + span]
        if len(train_dates) != TRAIN_MONTHS or len(test_dates) != TEST_MONTHS:
            continue
        folds.append(
            {
                "fold_id": f"mom_sswitch_mid_fold_{len(folds) + 1:03d}",
                "train_start": train_dates[0].strftime("%Y-%m-%d"),
                "train_end": train_dates[-1].strftime("%Y-%m-%d"),
                "test_start": test_dates[0].strftime("%Y-%m-%d"),
                "test_end": test_dates[-1].strftime("%Y-%m-%d"),
            }
        )
    return folds


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


def build_factor_monthly_returns(panel_df: pd.DataFrame, factor_col: str) -> pd.DataFrame:
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


def annualized(monthly_returns: pd.Series) -> float:
    values = pd.to_numeric(monthly_returns, errors="coerce").dropna()
    if len(values) == 0:
        return np.nan
    nav = float((1.0 + values).prod())
    years = len(values) / 12.0
    if years <= 0 or nav <= 0:
        return np.nan
    return nav ** (1.0 / years) - 1.0


def summarize_period(df: pd.DataFrame, ret_col: str) -> dict[str, object]:
    values = pd.to_numeric(df[ret_col], errors="coerce").dropna()
    if len(values) == 0:
        return {"months": 0, "total_return": np.nan, "annualized_return": np.nan}
    return {
        "months": int(len(values)),
        "total_return": float((1.0 + values).prod() - 1.0),
        "annualized_return": annualized(values),
    }


def choose_return_series(frame: pd.DataFrame, factor_name: str) -> pd.Series:
    if factor_name == "mom_6_1":
        return frame["mom_6_1_portfolio_return"]
    if factor_name == "mom_12_1":
        return frame["mom_12_1_portfolio_return"]
    if factor_name == "blend_50_50":
        return 0.5 * frame["mom_6_1_portfolio_return"] + 0.5 * frame["mom_12_1_portfolio_return"]
    raise ValueError(f"Unsupported factor_name: {factor_name}")


def build_rule_frame(return_df: pd.DataFrame, score_df: pd.DataFrame, q_low: float, q_high: float, rule: dict[str, str]) -> pd.DataFrame:
    out = score_df.merge(return_df, on="rebalance_date", how="left").copy()
    out["state_bucket"] = np.where(
        out["state_score_v1"] >= q_high,
        "high",
        np.where(out["state_score_v1"] <= q_low, "low", "mid"),
    )
    out["selected_factor"] = np.where(
        out["state_bucket"] == "high",
        rule["high_factor"],
        np.where(out["state_bucket"] == "mid", rule["mid_factor"], rule["low_factor"]),
    )
    selected = pd.Series(index=out.index, dtype="float64")
    for factor_name in sorted(set(out["selected_factor"].dropna().tolist())):
        mask = out["selected_factor"] == factor_name
        selected.loc[mask] = choose_return_series(out.loc[mask], factor_name)
    out["selected_return"] = selected
    return out


def build_result_rows(full_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        train_end = pd.Timestamp(fold["train_end"])
        test_start = pd.Timestamp(fold["test_start"])
        test_end = pd.Timestamp(fold["test_end"])

        train_mask = (full_df["rebalance_date"] >= train_start) & (full_df["rebalance_date"] <= train_end)
        test_mask = (full_df["rebalance_date"] >= test_start) & (full_df["rebalance_date"] <= test_end)

        train_scores = pd.to_numeric(full_df.loc[train_mask, "state_score_v1"], errors="coerce").dropna()
        if len(train_scores) == 0:
            continue
        q_low = float(train_scores.quantile(0.33))
        q_high = float(train_scores.quantile(0.67))

        base_return_df = full_df[["rebalance_date", "mom_6_1_portfolio_return", "mom_12_1_portfolio_return"]].copy()
        score_df = full_df[["rebalance_date", "state_score_v1"]].copy()
        test_base = base_return_df[test_mask].copy()
        test_mom6 = summarize_period(test_base, "mom_6_1_portfolio_return")
        test_mom12 = summarize_period(test_base, "mom_12_1_portfolio_return")

        for rule in RULE_SPECS:
            ruled = build_rule_frame(base_return_df, score_df, q_low=q_low, q_high=q_high, rule=rule)
            test_df = ruled[test_mask].copy()
            test_rule = summarize_period(test_df, "selected_return")

            rows.append(
                {
                    "fold_id": fold["fold_id"],
                    "rule_name": rule["rule_name"],
                    "train_start": fold["train_start"],
                    "train_end": fold["train_end"],
                    "test_start": fold["test_start"],
                    "test_end": fold["test_end"],
                    "train_q33": round(q_low, 6),
                    "train_q67": round(q_high, 6),
                    "test_rule_total_return": round(float(test_rule["total_return"]), 8) if not pd.isna(test_rule["total_return"]) else "",
                    "test_rule_annualized": round(float(test_rule["annualized_return"]), 8) if not pd.isna(test_rule["annualized_return"]) else "",
                    "test_mom6_total_return": round(float(test_mom6["total_return"]), 8) if not pd.isna(test_mom6["total_return"]) else "",
                    "test_mom12_total_return": round(float(test_mom12["total_return"]), 8) if not pd.isna(test_mom12["total_return"]) else "",
                    "test_high_months": int((test_df["state_bucket"] == "high").sum()),
                    "test_mid_months": int((test_df["state_bucket"] == "mid").sum()),
                    "test_low_months": int((test_df["state_bucket"] == "low").sum()),
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


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(result_rows: list[dict[str, object]]) -> None:
    df = pd.DataFrame(result_rows)
    lines = [
        "# Momentum State Switch Mid-State Test V1",
        "",
        "Protocol:",
        "- monthly sample = bank pool monthly rebalance dates before 2021",
        "- fold structure = `48m train + 12m test`",
        "- each fold estimates only the train-period `q33` and `q67` thresholds from `state_score_v1`",
        "- objective = compare how middle-state months should be routed under the same state definition",
        "",
    ]
    if not df.empty:
        lines.append("Rule summary:")
        summary_df = (
            df.groupby("rule_name", dropna=False)
            .agg(
                folds=("fold_id", "count"),
                mean_rule_return=("test_rule_total_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_rule_annualized=("test_rule_annualized", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_mom6_return=("test_mom6_total_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_mom12_return=("test_mom12_total_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                win_vs_mom6=("test_rule_total_return", lambda s: int((pd.to_numeric(s, errors="coerce") > pd.to_numeric(df.loc[s.index, "test_mom6_total_return"], errors="coerce")).sum())),
                win_vs_mom12=("test_rule_total_return", lambda s: int((pd.to_numeric(s, errors="coerce") > pd.to_numeric(df.loc[s.index, "test_mom12_total_return"], errors="coerce")).sum())),
            )
            .reset_index()
            .sort_values(["mean_rule_return", "win_vs_mom12"], ascending=[False, False])
        )
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['rule_name']}` | folds=`{int(row['folds'])}` | mean_test_return=`{format_float(row['mean_rule_return'])}` | mean_test_annualized=`{format_float(row['mean_rule_annualized'])}` | win_vs_mom6=`{int(row['win_vs_mom6'])}` | win_vs_mom12=`{int(row['win_vs_mom12'])}`"
            )

        best_row = summary_df.iloc[0]
        lines.extend(
            [
                "",
                "Current best-by-mean-return rule:",
                f"- `{best_row['rule_name']}` with mean test return `{format_float(best_row['mean_rule_return'])}`",
            ]
        )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUT_RESULTS_PATH.name}]({OUT_RESULTS_PATH})",
        ]
    )
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    state_df = load_state_scores()
    mom6_df = build_factor_monthly_returns(panel_df, "mom_6_1")
    mom12_df = build_factor_monthly_returns(panel_df, "mom_12_1")
    full_df = state_df.merge(mom6_df, on="rebalance_date", how="left").merge(mom12_df, on="rebalance_date", how="left")
    unique_dates = sorted(full_df["rebalance_date"].dropna().unique().tolist())
    folds = build_folds(unique_dates)
    result_rows = build_result_rows(full_df, folds)
    write_csv(OUT_RESULTS_PATH, result_rows)
    write_summary(result_rows)
    print(OUT_RESULTS_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
