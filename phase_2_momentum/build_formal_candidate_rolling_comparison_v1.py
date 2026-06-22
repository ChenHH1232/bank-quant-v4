from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DETAIL_PATH = SCRIPT_DIR / "slow_fundamental_fast_exit_execution_validation_v1_detail.csv"
QUARTERLY_DETAIL_PATH = SCRIPT_DIR / "quarterly_fundamental_monthly_momentum_rolling_validation_v1_detail.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "formal_candidate_rolling_comparison_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "formal_candidate_rolling_comparison_v1.md"

FIXED_NAME = "fixed_60_40"
STATE_NAME = "annual_entry_monthly_exit_slow_fundamental"
GATED_NAME = "quarterly_top20_mom12_top6"


def load_state_family() -> pd.DataFrame:
    df = pd.read_csv(STATE_DETAIL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_name"].isin([FIXED_NAME, STATE_NAME])].copy()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["portfolio_return"] = pd.to_numeric(df["portfolio_return"], errors="coerce")
    df["cash_weight"] = pd.to_numeric(df["cash_weight"], errors="coerce")
    df["invested_weight"] = pd.to_numeric(df["final_invested_weight"], errors="coerce")
    return df[
        [
            "fold_id",
            "strategy_name",
            "rebalance_date",
            "validation_start",
            "validation_end",
            "portfolio_return",
            "invested_weight",
            "cash_weight",
        ]
    ].copy()


def load_gated_family() -> pd.DataFrame:
    df = pd.read_csv(QUARTERLY_DETAIL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_name"] == GATED_NAME].copy()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["portfolio_return"] = pd.to_numeric(df["portfolio_return"], errors="coerce")
    df["holding_count"] = pd.to_numeric(df["holding_count"], errors="coerce")
    df["invested_weight"] = 1.0
    df["cash_weight"] = 0.0
    return df[
        [
            "fold_id",
            "strategy_name",
            "rebalance_date",
            "validation_start",
            "validation_end",
            "portfolio_return",
            "invested_weight",
            "cash_weight",
            "holding_count",
            "candidate_count",
            "candidate_pool_size",
        ]
    ].copy()


def build_common_sample() -> pd.DataFrame:
    state_df = load_state_family()
    gated_df = load_gated_family()

    state_dates = (
        state_df[["fold_id", "rebalance_date"]]
        .drop_duplicates()
        .assign(in_state=1)
    )
    gated_dates = (
        gated_df[["fold_id", "rebalance_date"]]
        .drop_duplicates()
        .assign(in_gated=1)
    )
    common_dates = state_dates.merge(gated_dates, on=["fold_id", "rebalance_date"], how="inner")

    state_common = state_df.merge(common_dates[["fold_id", "rebalance_date"]], on=["fold_id", "rebalance_date"], how="inner")
    gated_common = gated_df.merge(common_dates[["fold_id", "rebalance_date"]], on=["fold_id", "rebalance_date"], how="inner")

    state_common["candidate_role"] = state_common["strategy_name"].map(
        {
            FIXED_NAME: "fixed_dual_engine_baseline",
            STATE_NAME: "state_switch_candidate",
        }
    )
    gated_common["candidate_role"] = "fundamental_gate_then_momentum_rank"

    state_common["holding_count"] = pd.NA
    state_common["candidate_count"] = pd.NA
    state_common["candidate_pool_size"] = pd.NA

    combined = pd.concat([state_common, gated_common], axis=0, ignore_index=True)
    combined["month_key"] = combined["rebalance_date"].dt.strftime("%Y-%m")
    return combined.sort_values(["fold_id", "rebalance_date", "strategy_name"]).reset_index(drop=True)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    if df.empty:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(df.columns))
        writer.writeheader()
        writer.writerows(df.to_dict("records"))


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(df: pd.DataFrame) -> None:
    lines = [
        "# Formal Candidate Rolling Comparison V1",
        "",
        "Objective:",
        "- close the current phase-2 candidate race inside one fixed rolling comparison frame",
        "- compare only the current formal candidates, not every historical branch",
        "- use a common monthly sample so the fixed baseline, state-switch candidate, and gated momentum candidate are directly comparable",
        "",
        "Included candidates:",
        f"- `{FIXED_NAME}` = fixed dual-engine baseline",
        f"- `{STATE_NAME}` = annual-entry monthly-exit state-switch candidate",
        f"- `{GATED_NAME}` = quarterly fundamental gate then monthly momentum ranking",
        "",
        "Protocol:",
        "- research scope = pre-2021 rolling validation only",
        "- sample = common monthly dates present in both the state-machine detail table and the quarterly gate detail table",
        "- fold alignment = preserve original fold ids and validation windows",
        "- return aggregation = compound `portfolio_return` inside each fold and then summarize across folds",
        "",
    ]

    if df.empty:
        lines.extend(["No common-sample rows were produced."])
        OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    common_dates = df[["fold_id", "rebalance_date"]].drop_duplicates()
    lines.append(f"- fold count: `{df['fold_id'].nunique()}`")
    lines.append(f"- common monthly snapshots: `{len(common_dates)}`")
    lines.append("")

    summary_df = (
        df.groupby(["strategy_name", "candidate_role"], dropna=False)
        .agg(
            snapshot_count=("rebalance_date", "count"),
            mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
            mean_invested_weight=("invested_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            mean_cash_weight=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            positive_months=("portfolio_return", lambda s: int((pd.to_numeric(s, errors="coerce") > 0).sum())),
        )
        .reset_index()
        .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
    )

    lines.append("Candidate summary:")
    for _, row in summary_df.iterrows():
        lines.append(
            f"- `{row['strategy_name']}` | role=`{row['candidate_role']}` | snapshots=`{int(row['snapshot_count'])}` | "
            f"mean_return=`{format_float(row['mean_return'])}` | cum_return=`{format_float(row['cumulative_return'])}` | "
            f"mean_invested=`{format_float(row['mean_invested_weight'])}` | mean_cash=`{format_float(row['mean_cash_weight'])}` | "
            f"positive_months=`{int(row['positive_months'])}`"
        )

    lines.extend(["", "Fold summary:"])
    for fold_id in sorted(df["fold_id"].unique()):
        fold_df = df[df["fold_id"] == fold_id].copy()
        lines.append(f"- `{fold_id}`")
        for strategy_name in [FIXED_NAME, STATE_NAME, GATED_NAME]:
            subset = fold_df[fold_df["strategy_name"] == strategy_name].copy()
            if subset.empty:
                continue
            cum_return = float((1.0 + pd.to_numeric(subset["portfolio_return"], errors="coerce")).prod() - 1.0)
            mean_cash = pd.to_numeric(subset["cash_weight"], errors="coerce").mean()
            lines.append(
                f"- `{strategy_name}` | validation=`{subset['validation_start'].iloc[0]}` to `{subset['validation_end'].iloc[0]}` | "
                f"months=`{len(subset)}` | cum_return=`{format_float(cum_return)}` | mean_cash=`{format_float(mean_cash)}`"
            )

    ordered_names = summary_df["strategy_name"].tolist()
    if len(ordered_names) >= 3:
        leader = ordered_names[0]
        middle = ordered_names[1]
        laggard = ordered_names[2]
        lines.extend(
            [
                "",
                "Current reading:",
                f"- `{leader}` is the strongest current formal candidate on the common monthly rolling sample",
                f"- `{middle}` is the second-line formal candidate and should be read mainly as a structural alternative rather than a promoted replacement",
                f"- `{laggard}` currently trails on the same common sample and should stay archived as a coherent but weaker branch",
            ]
        )

    fixed_row = summary_df[summary_df["strategy_name"] == FIXED_NAME]
    state_row = summary_df[summary_df["strategy_name"] == STATE_NAME]
    gated_row = summary_df[summary_df["strategy_name"] == GATED_NAME]
    if not fixed_row.empty and not state_row.empty and not gated_row.empty:
        fixed_cum = float(fixed_row["cumulative_return"].iloc[0])
        state_cum = float(state_row["cumulative_return"].iloc[0])
        gated_cum = float(gated_row["cumulative_return"].iloc[0])
        lines.extend(
            [
                "",
                "Increment versus fixed baseline:",
                f"- `{STATE_NAME}` minus `{FIXED_NAME}` cum_return_delta=`{format_float(state_cum - fixed_cum)}`",
                f"- `{GATED_NAME}` minus `{FIXED_NAME}` cum_return_delta=`{format_float(gated_cum - fixed_cum)}`",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = build_common_sample()
    write_csv(OUT_DETAIL_PATH, df)
    write_summary(df)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
