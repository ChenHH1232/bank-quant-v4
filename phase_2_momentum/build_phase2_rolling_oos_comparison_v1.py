from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
DUAL_PATH = SCRIPT_DIR / "fundamental_momentum_dual_engine_rolling_test_v1_detail.csv"
STATE_PATH = SCRIPT_DIR / "slow_fundamental_fast_exit_execution_validation_v1_detail.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "phase2_rolling_oos_comparison_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "phase2_rolling_oos_comparison_v1.md"


def load_dual_df() -> pd.DataFrame:
    df = pd.read_csv(DUAL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_name"].isin(["fundamental_only", "momentum_only", "blend_60_40"])].copy()
    for col in ["portfolio_return", "cash_weight", "invested_weight"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["source_family"] = "dual_engine_common_sample"
    df["strategy_group"] = df["strategy_name"]
    return df[
        [
            "fold_id",
            "strategy_group",
            "rebalance_date",
            "validation_start",
            "validation_end",
            "portfolio_return",
            "cash_weight",
            "invested_weight",
            "source_family",
        ]
    ].copy()


def load_state_df() -> pd.DataFrame:
    df = pd.read_csv(STATE_PATH, encoding="utf-8-sig")
    df = df[df["strategy_name"].isin(["annual_entry_monthly_exit_slow_fundamental"])].copy()
    for col in ["portfolio_return", "cash_weight", "final_invested_weight"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["source_family"] = "state_machine_common_sample"
    df["strategy_group"] = df["strategy_name"]
    df = df.rename(columns={"final_invested_weight": "invested_weight"})
    return df[
        [
            "fold_id",
            "strategy_group",
            "rebalance_date",
            "validation_start",
            "validation_end",
            "portfolio_return",
            "cash_weight",
            "invested_weight",
            "source_family",
        ]
    ].copy()


def build_detail() -> pd.DataFrame:
    dual_df = load_dual_df()
    state_df = load_state_df()
    combined = pd.concat([dual_df, state_df], axis=0, ignore_index=True)
    combined["rebalance_date"] = pd.to_datetime(combined["rebalance_date"])
    return combined.sort_values(["strategy_group", "fold_id", "rebalance_date"]).reset_index(drop=True)


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
        "# Phase 2 Rolling OOS Comparison V1",
        "",
        "Objective:",
        "- place the current phase-2 candidate lines into one rolling out-of-sample comparison frame",
        "- make the current comparable evidence explicit before final report writing",
        "",
        "Included lines:",
        "- `fundamental_only`",
        "- `momentum_only`",
        "- `blend_60_40`",
        "- `annual_entry_monthly_exit_slow_fundamental`",
        "",
        "Important comparability note:",
        "- all lines below are drawn from the same pre-2021 rolling family",
        "- but `momentum_only` currently collapses to the same realized result as `fundamental_only` in the common-sample capped framework",
        "- and the state-machine branch is evaluated on a denser monthly sequence than the sparse common snapshots used by the basic dual-engine table",
        "- so the current table is best read as a project-level checkpoint, not as the final clean independent-engine horse race",
        "",
    ]

    if not df.empty:
        summary_df = (
            df.groupby(["strategy_group", "source_family"], dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_cash=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_invested=("invested_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )

        lines.append("Strategy summary:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['strategy_group']}` | source=`{row['source_family']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{format_float(row['mean_return'])}` | cum_return=`{format_float(row['cumulative_return'])}` | "
                f"mean_cash=`{format_float(row['mean_cash'])}` | mean_invested=`{format_float(row['mean_invested'])}`"
            )

        lines.extend(["", "Fold summary:"])
        for fold_id in sorted(df["fold_id"].unique()):
            fold_df = df[df["fold_id"] == fold_id].copy()
            lines.append(f"- `{fold_id}`")
            for strategy_name in [
                "fundamental_only",
                "momentum_only",
                "blend_60_40",
                "annual_entry_monthly_exit_slow_fundamental",
            ]:
                subset = fold_df[fold_df["strategy_group"] == strategy_name].copy()
                if subset.empty:
                    continue
                cum_return = float((1.0 + pd.to_numeric(subset["portfolio_return"], errors="coerce")).prod() - 1.0)
                mean_cash = pd.to_numeric(subset["cash_weight"], errors="coerce").mean()
                lines.append(
                    f"- `{fold_id}` `{strategy_name}` | validation=`{subset['validation_start'].iloc[0]}` to `{subset['validation_end'].iloc[0]}` | "
                    f"dates=`{len(subset)}` | cum_return=`{format_float(cum_return)}` | mean_cash=`{format_float(mean_cash)}`"
                )

        lines.extend(
            [
                "",
                "Current project-level reading:",
                "- `blend_60_40` remains the strongest practical rolling baseline among the currently comparable lines",
                "- `annual_entry_monthly_exit_slow_fundamental` remains the strongest current state-machine challenger",
                "- the state-machine branch still improves over its weaker internal variants, but it should be compared to `blend_60_40` only with the snapshot-density caveat kept explicit",
                "- the current pure-engine common-sample comparison is still structurally limited by cap-induced selection collapse",
            ]
        )

        lines.extend(
            [
                "",
                "What this means for the next step:",
                "- this unified frame is already sufficient for report-level sequencing and candidate hierarchy",
                "- but a final independent `pure momentum vs pure fundamental` statement should not rely only on this capped common-sample table",
                "- that separation still needs the broader momentum branch evidence already archived elsewhere",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = build_detail()
    write_csv(OUT_DETAIL_PATH, df)
    write_summary(df)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
