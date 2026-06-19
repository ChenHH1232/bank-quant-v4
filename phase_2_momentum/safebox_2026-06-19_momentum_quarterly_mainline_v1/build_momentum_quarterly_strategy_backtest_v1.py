from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_quarterly_rebalance_panel_v1.csv"
ROLLING_RESULTS_PATH = SCRIPT_DIR / "momentum_quarterly_rolling_validation_v1_results.csv"

OUTPUT_DETAIL_PATH = SCRIPT_DIR / "momentum_quarterly_strategy_backtest_v1_detail.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "momentum_quarterly_strategy_backtest_v1.md"

GROUP_COUNT = 5
HOLD_BUCKET = 5


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["next_rebalance_date"] = pd.to_datetime(df["next_rebalance_date"])
    return df[df["rebalance_stock_pool_flag"] == 1].copy()


def load_strategy_plan() -> pd.DataFrame:
    df = pd.read_csv(ROLLING_RESULTS_PATH, encoding="utf-8-sig")
    df = df[df["scenario_name"] == "alpha_only"].copy()
    df["review_start"] = pd.to_datetime(df["review_start"])
    df["review_end"] = pd.to_datetime(df["review_end"])
    return df.sort_values("review_start").reset_index(drop=True)


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def score_series(values: pd.Series, direction: str) -> pd.Series:
    raw = pd.to_numeric(values, errors="coerce")
    non_null = raw.dropna()
    if non_null.empty:
        return raw * np.nan
    lower = float(non_null.quantile(0.01))
    upper = float(non_null.quantile(0.99))
    clipped = raw.clip(lower=lower, upper=upper)
    mean_value = float(clipped.dropna().mean())
    std_value = float(clipped.dropna().std(ddof=0))
    if std_value <= 0 or pd.isna(std_value):
        z = clipped * np.nan
    else:
        z = (clipped - mean_value) / std_value
    mult = 1.0 if direction == "larger_better" else -1.0
    return z * mult


def build_detail_rows(panel_df: pd.DataFrame, plan_df: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    previous_top_codes: set[str] = set()

    review_dates = sorted(plan_df["review_start"].drop_duplicates())
    for review_date in review_dates:
        plan_row = plan_df[plan_df["review_start"] == review_date].iloc[0]
        factor_name = str(plan_row["selected_alpha_factor"])
        direction = str(plan_row["selected_alpha_direction"])

        group = panel_df[panel_df["rebalance_date"] == review_date].copy()
        if group.empty:
            continue

        group["_score"] = score_series(group[factor_name], direction)
        group["y_quarter_total_return_close"] = pd.to_numeric(group["y_quarter_total_return_close"], errors="coerce")
        group = group.dropna(subset=["_score", "y_quarter_total_return_close"])
        if len(group) < GROUP_COUNT:
            continue

        group["bucket"] = assign_groups(group["_score"], GROUP_COUNT)
        group = group.dropna(subset=["bucket"])
        top_group = group[group["bucket"] == HOLD_BUCKET].copy()
        bottom_group = group[group["bucket"] == 1].copy()
        if top_group.empty or bottom_group.empty:
            continue

        top_group = top_group.sort_values(["_score", "code"], ascending=[False, True]).reset_index(drop=True)
        bottom_group = bottom_group.sort_values(["_score", "code"], ascending=[True, True]).reset_index(drop=True)

        top_return = float(top_group["y_quarter_total_return_close"].mean())
        bottom_return = float(bottom_group["y_quarter_total_return_close"].mean())
        long_short = top_return - bottom_return

        top_codes = set(top_group["code"].astype(str))
        if not previous_top_codes:
            top_turnover = ""
        else:
            retained = len(top_codes & previous_top_codes)
            top_turnover = round(1.0 - (retained / len(top_codes)), 6) if top_codes else ""
        previous_top_codes = top_codes

        rows.append(
            {
                "review_start": pd.Timestamp(review_date).strftime("%Y-%m-%d"),
                "review_end": pd.Timestamp(plan_row["review_end"]).strftime("%Y-%m-%d"),
                "selected_alpha_factor": factor_name,
                "selected_alpha_direction": direction,
                "candidate_count": int(len(group)),
                "top_bucket_count": int(len(top_group)),
                "bottom_bucket_count": int(len(bottom_group)),
                "top_bucket_return": round(top_return, 10),
                "bottom_bucket_return": round(bottom_return, 10),
                "long_short_return": round(long_short, 10),
                "top_bucket_turnover": top_turnover,
                "top_bucket_codes": ";".join(top_group["code"].astype(str).tolist()),
                "bottom_bucket_codes": ";".join(bottom_group["code"].astype(str).tolist()),
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_DETAIL_PATH.write_text("", encoding="utf-8")
        return
    with OUTPUT_DETAIL_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, object]], plan_df: pd.DataFrame) -> None:
    if not rows:
        OUTPUT_SUMMARY_PATH.write_text("# Momentum Quarterly Strategy Backtest V1\n\n- no rows", encoding="utf-8")
        return

    df = pd.DataFrame(rows)
    df["review_start"] = pd.to_datetime(df["review_start"])
    df["top_bucket_return"] = pd.to_numeric(df["top_bucket_return"], errors="coerce")
    df["bottom_bucket_return"] = pd.to_numeric(df["bottom_bucket_return"], errors="coerce")
    df["long_short_return"] = pd.to_numeric(df["long_short_return"], errors="coerce")
    df["top_bucket_turnover"] = pd.to_numeric(df["top_bucket_turnover"], errors="coerce")

    top_cum = float((1.0 + df["top_bucket_return"]).prod() - 1.0)
    bottom_cum = float((1.0 + df["bottom_bucket_return"]).prod() - 1.0)
    long_short_cum = float((1.0 + df["long_short_return"]).prod() - 1.0)
    mean_turnover = df["top_bucket_turnover"].dropna().mean()

    lines = [
        "# Momentum Quarterly Strategy Backtest V1",
        "",
        "Definition:",
        "- alpha source = rolling-selected `alpha_only` scenario from `momentum_quarterly_rolling_validation_v1_results.csv`",
        "- current formal line should therefore behave as a quarterly `mom_12_1` strategy",
        "- stock pool keeps the prior-20-trading-day liquidity and market-cap double-top-80% rule",
        "- portfolio bucket = top quintile at each quarterly review date, equal-weight interpretation",
        "",
        f"- scored review rebalances: `{len(df)}`",
        f"- candidate quarterly review dates in plan: `{plan_df['review_start'].nunique()}`",
        f"- top cumulative return: `{round(top_cum, 10)}`",
        f"- bottom cumulative return: `{round(bottom_cum, 10)}`",
        f"- long-short cumulative return: `{round(long_short_cum, 10)}`",
        f"- mean top turnover: `{round(float(mean_turnover), 6) if pd.notna(mean_turnover) else ''}`",
        "",
        "Per-quarter detail:",
    ]

    for row in df.sort_values("review_start").itertuples(index=False):
        lines.append(
            f"- `{row.review_start.strftime('%Y-%m-%d')}` | alpha=`{row.selected_alpha_factor}` | "
            f"top_return=`{row.top_bucket_return}` | bottom_return=`{row.bottom_bucket_return}` | "
            f"long_short=`{row.long_short_return}` | turnover=`{row.top_bucket_turnover if not pd.isna(row.top_bucket_turnover) else ''}`"
        )

    lines.extend(["", "Output:", f"- [{OUTPUT_DETAIL_PATH.name}]({OUTPUT_DETAIL_PATH})"])
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    plan_df = load_strategy_plan()
    rows = build_detail_rows(panel_df, plan_df)
    write_csv(rows)
    write_summary(rows, plan_df)
    print(OUTPUT_DETAIL_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
