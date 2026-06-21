from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_state_proxy_comparison_rolling_validation_v1 as base

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "deterioration_state_proxy_refinement_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "deterioration_state_proxy_refinement_v1.md"
FULL_DETERIORATION_PATH = SCRIPT_DIR / "fundamental_deterioration_date_panel_v1.csv"

CANDIDATE_SPECS = [
    {"candidate_name": "fixed_blend_60_40", "mode": "fixed", "fundamental_budget": 0.6, "momentum_budget": 0.4},
    {"candidate_name": "v1_base", "mode": "state", "formula": [(-1.0, "deterioration_ratio"), (1.0, "score_delta_mean"), (1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "breadth_only", "mode": "state", "formula": [(-1.0, "deterioration_ratio")]},
    {"candidate_name": "severe_breadth_only", "mode": "state", "formula": [(-1.0, "severe_deterioration_ratio")]},
    {"candidate_name": "delta_mean_only", "mode": "state", "formula": [(1.0, "score_delta_mean")]},
    {"candidate_name": "delta_median_only", "mode": "state", "formula": [(1.0, "score_delta_median")]},
    {"candidate_name": "bottom_quartile_only", "mode": "state", "formula": [(1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "top_bottom_spread_only", "mode": "state", "formula": [(1.0, "score_delta_top_bottom_spread")]},
    {"candidate_name": "breadth_plus_mean", "mode": "state", "formula": [(-1.0, "deterioration_ratio"), (1.0, "score_delta_mean")]},
    {"candidate_name": "breadth_plus_median", "mode": "state", "formula": [(-1.0, "deterioration_ratio"), (1.0, "score_delta_median")]},
    {"candidate_name": "breadth_plus_bottom", "mode": "state", "formula": [(-1.0, "deterioration_ratio"), (1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "severe_plus_mean", "mode": "state", "formula": [(-1.0, "severe_deterioration_ratio"), (1.0, "score_delta_mean")]},
    {"candidate_name": "severe_plus_bottom", "mode": "state", "formula": [(-1.0, "severe_deterioration_ratio"), (1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "mean_plus_bottom", "mode": "state", "formula": [(1.0, "score_delta_mean"), (1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "median_plus_bottom", "mode": "state", "formula": [(1.0, "score_delta_median"), (1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "breadth_mean_bottom", "mode": "state", "formula": [(-1.0, "deterioration_ratio"), (1.0, "score_delta_mean"), (1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "breadth_median_bottom", "mode": "state", "formula": [(-1.0, "deterioration_ratio"), (1.0, "score_delta_median"), (1.0, "score_delta_bottom_quartile_mean")]},
    {"candidate_name": "breadth_mean_stdneg", "mode": "state", "formula": [(-1.0, "deterioration_ratio"), (1.0, "score_delta_mean"), (-1.0, "score_delta_std")]},
]


def format_formula(formula: list[tuple[float, str]]) -> str:
    parts = []
    for weight, column_name in formula:
        parts.append(f"{weight:+.1f}*{column_name}")
    return " ".join(parts).replace("+", "+ ").replace("-", "- ").strip()


def build_candidate_raw_score(df: pd.DataFrame, formula: list[tuple[float, str]]) -> pd.Series:
    out = pd.Series(index=df.index, data=0.0, dtype="float64")
    valid_any = pd.Series(index=df.index, data=False)
    for weight, column_name in formula:
        values = pd.to_numeric(df[column_name], errors="coerce")
        out = out + weight * values.fillna(0.0)
        valid_any = valid_any | values.notna()
    out.loc[~valid_any] = pd.NA
    return pd.to_numeric(out, errors="coerce")


def build_full_joint_panel() -> pd.DataFrame:
    panel_df = base.build_joint_panel().copy()
    extra_df = pd.read_csv(FULL_DETERIORATION_PATH, encoding="utf-8-sig")
    extra_df["rebalance_date"] = pd.to_datetime(extra_df["rebalance_date"])
    keep_cols = [
        "rebalance_date",
        "severe_deterioration_ratio",
        "score_delta_median",
        "score_delta_std",
        "score_delta_top_bottom_spread",
    ]
    panel_df = panel_df.merge(extra_df[keep_cols], on="rebalance_date", how="left")
    return panel_df


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
        validation_df = scored_df[validation_mask].copy()
        if validation_df.empty:
            continue

        candidate_cut_map: dict[str, tuple[float, float]] = {}
        for spec in CANDIDATE_SPECS:
            if spec["mode"] != "state":
                continue
            raw_col = "raw__" + spec["candidate_name"]
            z_col = "z__" + spec["candidate_name"]
            scored_df[raw_col] = build_candidate_raw_score(scored_df, spec["formula"])
            scored_df[z_col] = base.preprocess_state_series(scored_df, train_mask, raw_col)
            train_state_df = scored_df.loc[train_mask, ["rebalance_date", z_col]].drop_duplicates().dropna().copy()
            if train_state_df.empty:
                continue
            candidate_cut_map[spec["candidate_name"]] = (
                float(train_state_df[z_col].quantile(0.33)),
                float(train_state_df[z_col].quantile(0.67)),
            )

        validation_df = scored_df[validation_mask].copy()
        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[base.FUNDAMENTAL_COMBO, "score__mom12", base.FUNDAMENTAL_TARGET_COL]).copy()
            if len(group) < 5:
                continue

            for spec in CANDIDATE_SPECS:
                if spec["mode"] == "fixed":
                    state_bucket = "fixed"
                    fundamental_budget = float(spec["fundamental_budget"])
                    momentum_budget = float(spec["momentum_budget"])
                    state_score = pd.NA
                    low_cut = pd.NA
                    high_cut = pd.NA
                    formula_text = "fixed_60_40"
                else:
                    candidate_name = spec["candidate_name"]
                    z_col = "z__" + candidate_name
                    if candidate_name not in candidate_cut_map or z_col not in group.columns:
                        continue
                    group_valid = group.dropna(subset=[z_col]).copy()
                    if group_valid.empty:
                        continue
                    state_score = float(group_valid[z_col].iloc[0])
                    low_cut, high_cut = candidate_cut_map[candidate_name]
                    state_bucket = base.classify_state(state_score, low_cut, high_cut)
                    fundamental_budget, momentum_budget = base.get_state_budgets(state_bucket)
                    formula_text = format_formula(spec["formula"])

                evaluated = base.evaluate_group(group, fundamental_budget, momentum_budget)
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "candidate_name": spec["candidate_name"],
                        "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                        "train_start": fold["train_start"],
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "formula": formula_text,
                        "universe_count": int(len(group)),
                        "state_score": round(float(state_score), 6) if pd.notna(state_score) else pd.NA,
                        "low_cut": round(float(low_cut), 6) if pd.notna(low_cut) else pd.NA,
                        "high_cut": round(float(high_cut), 6) if pd.notna(high_cut) else pd.NA,
                        "state_bucket": state_bucket,
                        "fundamental_budget": fundamental_budget,
                        "momentum_budget": momentum_budget,
                        "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                        "invested_weight": round(float(evaluated["invested_weight"]), 6),
                        "cash_weight": round(float(evaluated["cash_weight"]), 6),
                        "fundamental_stock_count": int(evaluated["fundamental_stock_count"]),
                        "momentum_stock_count": int(evaluated["momentum_stock_count"]),
                        "final_stock_count": int(evaluated["final_stock_count"]),
                        "overlap_stock_count": int(evaluated["overlap_stock_count"]),
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
        "# Deterioration State Proxy Refinement V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- objective = refine only the deterioration-based observable state family",
        "- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`",
        "- momentum engine = deployment-safe `mom_12_1`",
        "- train-set terciles define `weak_down / neutral_flat / strong_up`",
        "- state allocation mapping:",
        "- `strong_up` => `60%` fundamental + `40%` momentum",
        "- `neutral_flat` => `80%` fundamental + `20%` momentum",
        "- `weak_down` => `100%` fundamental + `0%` momentum",
        "",
        f"- fold count: `{len(folds)}`",
        f"- candidate count: `{df['candidate_name'].nunique() if not df.empty else 0}`",
        "",
    ]
    if not df.empty:
        summary_df = (
            df.groupby(["candidate_name", "formula"], dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_cash_weight=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        lines.append("Candidate ranking:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['candidate_name']}` | formula=`{row['formula']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{base.format_float(row['mean_return'])}` | cum_return=`{base.format_float(row['cumulative_return'])}` | "
                f"mean_cash=`{base.format_float(row['mean_cash_weight'])}`"
            )

        top_names = list(summary_df["candidate_name"].head(5))
        lines.extend(["", "Top candidate state mix:"])
        for candidate_name in top_names:
            subset_df = df[df["candidate_name"] == candidate_name].copy()
            for state_bucket in ["strong_up", "neutral_flat", "weak_down"]:
                subset = subset_df[subset_df["state_bucket"] == state_bucket].copy()
                if subset.empty:
                    continue
                lines.append(
                    f"- `{candidate_name}` `{state_bucket}` | snapshots=`{len(subset)}` | "
                    f"mean_return=`{base.format_float(pd.to_numeric(subset['portfolio_return'], errors='coerce').mean())}` | "
                    f"mean_f_budget=`{base.format_float(pd.to_numeric(subset['fundamental_budget'], errors='coerce').mean(), 2)}` | "
                    f"mean_m_budget=`{base.format_float(pd.to_numeric(subset['momentum_budget'], errors='coerce').mean(), 2)}`"
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
