from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_state_proxy_comparison_rolling_validation_v1 as base

SCRIPT_DIR = Path(__file__).resolve().parent
FULL_DETERIORATION_PATH = SCRIPT_DIR / "fundamental_deterioration_date_panel_v1.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "deterioration_state_threshold_sensitivity_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "deterioration_state_threshold_sensitivity_v1.md"

CANDIDATES = [
    {"candidate_name": "delta_median_only", "formula": [(1.0, "score_delta_median")]},
    {"candidate_name": "breadth_only", "formula": [(-1.0, "deterioration_ratio")]},
    {"candidate_name": "fixed_blend_60_40", "formula": None},
]

THRESHOLD_SPECS = [
    {"threshold_name": "q30_q70", "low_q": 0.30, "high_q": 0.70},
    {"threshold_name": "q33_q67", "low_q": 0.33, "high_q": 0.67},
    {"threshold_name": "q25_q75", "low_q": 0.25, "high_q": 0.75},
    {"threshold_name": "q20_q80", "low_q": 0.20, "high_q": 0.80},
]


def format_formula(formula: list[tuple[float, str]] | None) -> str:
    if formula is None:
        return "fixed_60_40"
    parts = []
    for weight, column_name in formula:
        parts.append(f"{weight:+.1f}*{column_name}")
    return " ".join(parts).replace("+", "+ ").replace("-", "- ").strip()


def build_full_joint_panel() -> pd.DataFrame:
    panel_df = base.build_joint_panel().copy()
    extra_df = pd.read_csv(FULL_DETERIORATION_PATH, encoding="utf-8-sig")
    extra_df["rebalance_date"] = pd.to_datetime(extra_df["rebalance_date"])
    keep_cols = ["rebalance_date", "deterioration_ratio", "score_delta_median"]
    panel_df = panel_df.merge(extra_df[keep_cols], on="rebalance_date", how="left", suffixes=("", "_dup"))
    dup_cols = [col for col in panel_df.columns if col.endswith("_dup")]
    if dup_cols:
        panel_df = panel_df.drop(columns=dup_cols)
    return panel_df


def build_candidate_raw_score(df: pd.DataFrame, formula: list[tuple[float, str]]) -> pd.Series:
    out = pd.Series(index=df.index, data=0.0, dtype="float64")
    valid_any = pd.Series(index=df.index, data=False)
    for weight, column_name in formula:
        values = pd.to_numeric(df[column_name], errors="coerce")
        out = out + weight * values.fillna(0.0)
        valid_any = valid_any | values.notna()
    out.loc[~valid_any] = pd.NA
    return pd.to_numeric(out, errors="coerce")


def build_detail_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)
        validation_mask = (panel_df["rebalance_date"] >= validation_start) & (panel_df["rebalance_date"] <= validation_end)

        scored_df = base.build_fundamental_score_frame(panel_df, train_mask)
        scored_df["score__mom12"] = base.preprocess_momentum_factor(scored_df, train_mask)

        for candidate in CANDIDATES:
            candidate_name = candidate["candidate_name"]
            formula = candidate["formula"]
            if formula is not None:
                raw_col = "raw__" + candidate_name
                z_col = "z__" + candidate_name
                scored_df[raw_col] = build_candidate_raw_score(scored_df, formula)
                scored_df[z_col] = base.preprocess_state_series(scored_df, train_mask, raw_col)

        validation_df = scored_df[validation_mask].copy()
        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[base.FUNDAMENTAL_COMBO, "score__mom12", base.FUNDAMENTAL_TARGET_COL]).copy()
            if len(group) < 5:
                continue

            for candidate in CANDIDATES:
                candidate_name = candidate["candidate_name"]
                formula = candidate["formula"]
                if formula is None:
                    evaluated = base.evaluate_group(group, 0.6, 0.4)
                    rows.append(
                        {
                            "fold_id": fold["fold_id"],
                            "candidate_name": candidate_name,
                            "threshold_name": "fixed",
                            "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                            "formula": format_formula(formula),
                            "low_q": pd.NA,
                            "high_q": pd.NA,
                            "state_score": pd.NA,
                            "low_cut": pd.NA,
                            "high_cut": pd.NA,
                            "state_bucket": "fixed",
                            "fundamental_budget": 0.6,
                            "momentum_budget": 0.4,
                            "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                            "cash_weight": round(float(evaluated["cash_weight"]), 6),
                        }
                    )
                    continue

                z_col = "z__" + candidate_name
                train_state_df = scored_df.loc[train_mask, ["rebalance_date", z_col]].drop_duplicates().dropna().copy()
                if train_state_df.empty:
                    continue
                group_valid = group.dropna(subset=[z_col]).copy()
                if group_valid.empty:
                    continue
                state_score = float(group_valid[z_col].iloc[0])

                for threshold in THRESHOLD_SPECS:
                    low_cut = float(train_state_df[z_col].quantile(threshold["low_q"]))
                    high_cut = float(train_state_df[z_col].quantile(threshold["high_q"]))
                    state_bucket = base.classify_state(state_score, low_cut, high_cut)
                    fundamental_budget, momentum_budget = base.get_state_budgets(state_bucket)
                    evaluated = base.evaluate_group(group, fundamental_budget, momentum_budget)
                    rows.append(
                        {
                            "fold_id": fold["fold_id"],
                            "candidate_name": candidate_name,
                            "threshold_name": threshold["threshold_name"],
                            "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                            "formula": format_formula(formula),
                            "low_q": threshold["low_q"],
                            "high_q": threshold["high_q"],
                            "state_score": round(state_score, 6),
                            "low_cut": round(low_cut, 6),
                            "high_cut": round(high_cut, 6),
                            "state_bucket": state_bucket,
                            "fundamental_budget": fundamental_budget,
                            "momentum_budget": momentum_budget,
                            "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                            "cash_weight": round(float(evaluated["cash_weight"]), 6),
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


def write_summary(rows: list[dict[str, object]], folds: list[dict[str, object]]) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# Deterioration State Threshold Sensitivity V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- candidates = `delta_median_only`, `breadth_only`, plus fixed `60/40` baseline",
        "- objective = test whether the deterioration-state edge survives different train-set quantile cuts",
        "- state allocation mapping:",
        "- `strong_up` => `60%` fundamental + `40%` momentum",
        "- `neutral_flat` => `80%` fundamental + `20%` momentum",
        "- `weak_down` => `100%` fundamental + `0%` momentum",
        "",
        f"- fold count: `{len(folds)}`",
        "",
    ]
    if not df.empty:
        summary_df = (
            df.groupby(["candidate_name", "threshold_name", "formula"], dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_cash=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        lines.append("Ranking:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['candidate_name']}` `{row['threshold_name']}` | formula=`{row['formula']}` | "
                f"snapshots=`{int(row['snapshot_count'])}` | mean_return=`{base.format_float(row['mean_return'])}` | "
                f"cum_return=`{base.format_float(row['cumulative_return'])}` | mean_cash=`{base.format_float(row['mean_cash'])}`"
            )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = build_full_joint_panel()
    folds = base.load_folds()
    rows = build_detail_rows(panel_df, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
