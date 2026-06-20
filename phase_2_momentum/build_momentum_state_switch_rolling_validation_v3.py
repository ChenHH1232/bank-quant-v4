from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
STATE_V1_PATH = SCRIPT_DIR / "momentum_forward_state_score_v1.csv"
STATE_V2_PATH = SCRIPT_DIR / "momentum_forward_state_score_v2.csv"
OUT_RESULTS_PATH = SCRIPT_DIR / "momentum_state_switch_rolling_validation_v3_results.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "momentum_state_switch_rolling_validation_v3.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5
GROUP_COUNT = 5
HOLD_BUCKET = 5
TRAIN_MONTHS = 48
TEST_MONTHS = 12


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[(df[POOL_FLAG] == 1) & (df["rebalance_date"] < pd.Timestamp("2021-01-01"))].copy()
    for col in ["mom_6_1", "mom_12_1", TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_state_scores(path: Path, score_col: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_date"] < pd.Timestamp("2021-01-01")].copy()
    return df[["rebalance_date", score_col]]


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
                "fold_id": f"mom_sswitch_v3_fold_{len(folds) + 1:03d}",
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


def build_switch_frame(return_df: pd.DataFrame, score_df: pd.DataFrame, score_col: str, q_low: float, q_high: float) -> pd.DataFrame:
    out = score_df.merge(return_df, on="rebalance_date", how="left").copy()
    out["state_bucket"] = np.where(
        out[score_col] >= q_high,
        "high_use_mom6",
        np.where(out[score_col] <= q_low, "low_use_mom12", "mid_use_mom12"),
    )
    out["selected_factor"] = np.where(out["state_bucket"] == "high_use_mom6", "mom_6_1", "mom_12_1")
    out["selected_return"] = np.where(
        out["selected_factor"] == "mom_6_1",
        out["mom_6_1_portfolio_return"],
        out["mom_12_1_portfolio_return"],
    )
    return out


def evaluate_one_score(full_df: pd.DataFrame, score_col: str, folds: list[dict[str, object]], label: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        train_end = pd.Timestamp(fold["train_end"])
        test_start = pd.Timestamp(fold["test_start"])
        test_end = pd.Timestamp(fold["test_end"])

        train_mask = (full_df["rebalance_date"] >= train_start) & (full_df["rebalance_date"] <= train_end)
        test_mask = (full_df["rebalance_date"] >= test_start) & (full_df["rebalance_date"] <= test_end)

        train_scores = pd.to_numeric(full_df.loc[train_mask, score_col], errors="coerce").dropna()
        if len(train_scores) == 0:
            continue
        q_low = float(train_scores.quantile(0.33))
        q_high = float(train_scores.quantile(0.67))

        switched = build_switch_frame(
            full_df[["rebalance_date", "mom_6_1_portfolio_return", "mom_12_1_portfolio_return"]].copy(),
            full_df[["rebalance_date", score_col]].copy(),
            score_col=score_col,
            q_low=q_low,
            q_high=q_high,
        )
        test_df = switched[test_mask].copy()

        t_switch = summarize_period(test_df, "selected_return")
        t_mom6 = summarize_period(test_df, "mom_6_1_portfolio_return")
        t_mom12 = summarize_period(test_df, "mom_12_1_portfolio_return")

        rows.append(
            {
                "score_version": label,
                "fold_id": fold["fold_id"],
                "train_start": fold["train_start"],
                "train_end": fold["train_end"],
                "test_start": fold["test_start"],
                "test_end": fold["test_end"],
                "train_q33": round(q_low, 6),
                "train_q67": round(q_high, 6),
                "test_switch_total_return": round(float(t_switch["total_return"]), 8) if not pd.isna(t_switch["total_return"]) else "",
                "test_switch_annualized": round(float(t_switch["annualized_return"]), 8) if not pd.isna(t_switch["annualized_return"]) else "",
                "test_mom6_total_return": round(float(t_mom6["total_return"]), 8) if not pd.isna(t_mom6["total_return"]) else "",
                "test_mom12_total_return": round(float(t_mom12["total_return"]), 8) if not pd.isna(t_mom12["total_return"]) else "",
                "test_high_state_months": int((test_df["state_bucket"] == "high_use_mom6").sum()),
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
        "# Momentum State Switch Rolling Validation V3",
        "",
        "Protocol:",
        "- monthly sample = bank pool monthly rebalance dates before 2021",
        "- fold structure = `48m train + 12m test`",
        "- switching rule stays fixed: high state uses `mom_6_1`, otherwise use `mom_12_1`",
        "- objective = compare `state_score_v1` and `state_score_v2` under the same rolling protocol",
        "",
    ]
    if not df.empty:
        lines.append("Score-version summary:")
        for score_version, group in df.groupby("score_version", dropna=False):
            switch_returns = pd.to_numeric(group["test_switch_total_return"], errors="coerce")
            mom6_returns = pd.to_numeric(group["test_mom6_total_return"], errors="coerce")
            mom12_returns = pd.to_numeric(group["test_mom12_total_return"], errors="coerce")
            high_months = pd.to_numeric(group["test_high_state_months"], errors="coerce")
            lines.append(
                f"- `{score_version}` | folds=`{len(group)}` | mean_test_return=`{format_float(switch_returns.mean())}` | win_vs_mom6=`{int((switch_returns > mom6_returns).sum())}` | win_vs_mom12=`{int((switch_returns > mom12_returns).sum())}` | avg_high_state_months=`{format_float(high_months.mean(), 2)}`"
            )

        pivot = (
            df.pivot_table(index="fold_id", columns="score_version", values="test_switch_total_return", aggfunc="first")
            .reset_index(drop=False)
        )
        if "state_score_v1" in pivot.columns and "state_score_v2" in pivot.columns:
            v1 = pd.to_numeric(pivot["state_score_v1"], errors="coerce")
            v2 = pd.to_numeric(pivot["state_score_v2"], errors="coerce")
            lines.extend(
                [
                    "",
                    "Direct V2 vs V1 comparison:",
                    f"- v2 better than v1 folds: `{int((v2 > v1).sum())}`",
                    f"- mean(v2 - v1) test return: `{format_float((v2 - v1).mean())}`",
                ]
            )

    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUT_RESULTS_PATH.name}]({OUT_RESULTS_PATH})",
        ]
    )
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    state_v1 = load_state_scores(STATE_V1_PATH, "state_score_v1")
    state_v2 = load_state_scores(STATE_V2_PATH, "state_score_v2")
    mom6_df = build_factor_monthly_returns(panel_df, "mom_6_1")
    mom12_df = build_factor_monthly_returns(panel_df, "mom_12_1")

    full_v1 = state_v1.merge(mom6_df, on="rebalance_date", how="left").merge(mom12_df, on="rebalance_date", how="left")
    full_v2 = state_v2.merge(mom6_df, on="rebalance_date", how="left").merge(mom12_df, on="rebalance_date", how="left")
    unique_dates = sorted(full_v1["rebalance_date"].dropna().unique().tolist())
    folds = build_folds(unique_dates)

    result_rows = []
    result_rows.extend(evaluate_one_score(full_v1, "state_score_v1", folds, "state_score_v1"))
    result_rows.extend(evaluate_one_score(full_v2, "state_score_v2", folds, "state_score_v2"))

    write_csv(OUT_RESULTS_PATH, result_rows)
    write_summary(result_rows)
    print(OUT_RESULTS_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
