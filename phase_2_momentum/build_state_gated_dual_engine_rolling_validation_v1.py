from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
FUNDAMENTAL_DIR = ROOT_DIR / "phase_1_fundamental"
MOMENTUM_DIR = SCRIPT_DIR

if str(FUNDAMENTAL_DIR) not in sys.path:
    sys.path.insert(0, str(FUNDAMENTAL_DIR))

from build_pre2021_rolling_validation_v1 import (  # type: ignore
    add_combo_scores,
    build_scored_panel,
    load_panel as load_fundamental_panel,
    prepare_factor_metadata,
)

MOMENTUM_PANEL_PATH = MOMENTUM_DIR / "momentum_monthly_rebalance_panel_v2.csv"
FUNDAMENTAL_FOLDS_PATH = FUNDAMENTAL_DIR / "pre2021_rolling_validation_v1_folds.csv"
STATE_PROXY_PATH = MOMENTUM_DIR / "momentum_forward_state_score_v1.csv"
OUT_DETAIL_PATH = MOMENTUM_DIR / "state_gated_dual_engine_rolling_validation_v1_detail.csv"
OUT_SUMMARY_PATH = MOMENTUM_DIR / "state_gated_dual_engine_rolling_validation_v1.md"

ENGINE_STOCK_CAP = 0.05
FINAL_STOCK_CAP = 0.08
FUNDAMENTAL_COMBO = "combo__equal_weight"
FUNDAMENTAL_TARGET_COL = "y_quarter_avg_daily_return_close"
MOMENTUM_FACTOR_COL = "mom_12_1"

BASELINE_STRATEGIES = [
    {"strategy_name": "fundamental_only", "mode": "fixed", "fundamental_budget": 1.0, "momentum_budget": 0.0},
    {"strategy_name": "blend_80_20", "mode": "fixed", "fundamental_budget": 0.8, "momentum_budget": 0.2},
    {"strategy_name": "blend_60_40", "mode": "fixed", "fundamental_budget": 0.6, "momentum_budget": 0.4},
    {"strategy_name": "state_gated_dual_engine", "mode": "state_gated"},
]


def load_momentum_panel() -> pd.DataFrame:
    df = pd.read_csv(MOMENTUM_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_stock_pool_flag_v2"] == 1].copy()
    df[MOMENTUM_FACTOR_COL] = pd.to_numeric(df[MOMENTUM_FACTOR_COL], errors="coerce")
    return df[["rebalance_date", "code", MOMENTUM_FACTOR_COL]].copy()


def load_state_proxy() -> pd.DataFrame:
    df = pd.read_csv(STATE_PROXY_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["observable_state_score_v1"] = (
        pd.to_numeric(df["z__cross_mcap_median"], errors="coerce")
        + pd.to_numeric(df["z__cross_mom6_positive_ratio"], errors="coerce")
        - pd.to_numeric(df["z__cross_money_median"], errors="coerce")
    )
    return df[["rebalance_date", "observable_state_score_v1"]].copy()


def load_folds() -> list[dict[str, object]]:
    df = pd.read_csv(FUNDAMENTAL_FOLDS_PATH, encoding="utf-8-sig")
    return df.to_dict("records")


def preprocess_momentum_factor(full_df: pd.DataFrame, train_mask: pd.Series) -> pd.Series:
    values = pd.to_numeric(full_df[MOMENTUM_FACTOR_COL], errors="coerce")
    train_values = values[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=full_df.index, dtype="float64")
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = values.clip(lower=lower, upper=upper)
    train_clipped = clipped[train_mask].dropna()
    mean_value = float(train_clipped.mean())
    std_value = float(train_clipped.std(ddof=0))
    if pd.isna(std_value) or std_value <= 1e-12:
        return pd.Series(index=full_df.index, dtype="float64")
    return (clipped - mean_value) / std_value


def build_joint_panel() -> pd.DataFrame:
    fundamental_df = load_fundamental_panel()
    fundamental_df["rebalance_date"] = pd.to_datetime(fundamental_df["rebalance_date"])
    fundamental_df = fundamental_df[fundamental_df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    momentum_df = load_momentum_panel()
    momentum_df = momentum_df[momentum_df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    state_df = load_state_proxy()
    state_df = state_df[state_df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()

    merged = fundamental_df.merge(momentum_df, on=["rebalance_date", "code"], how="inner")
    merged = merged.merge(state_df, on="rebalance_date", how="inner")
    merged[FUNDAMENTAL_TARGET_COL] = pd.to_numeric(merged[FUNDAMENTAL_TARGET_COL], errors="coerce")
    merged = merged.dropna(subset=[FUNDAMENTAL_TARGET_COL, "observable_state_score_v1"]).copy()
    return merged


def build_fundamental_score_frame(panel_df: pd.DataFrame, train_mask: pd.Series) -> pd.DataFrame:
    _, enhanced_rows = prepare_factor_metadata()
    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, enhanced_rows, train_mask)
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    return scored_df


def build_engine_weights(group: pd.DataFrame, score_col: str, budget: float, engine_cap: float) -> pd.Series:
    weights = pd.Series(index=group.index, data=0.0, dtype="float64")
    if budget <= 0:
        return weights
    work = group.dropna(subset=[score_col]).sort_values([score_col, "code"], ascending=[False, True]).copy()
    if work.empty:
        return weights

    score_values = pd.to_numeric(work[score_col], errors="coerce")
    ranked = score_values.rank(method="first", ascending=False)
    raw_strength = (len(work) + 1 - ranked).astype(float)
    raw_strength = raw_strength / float(raw_strength.sum())

    active_index = list(work.index)
    remaining_budget = float(budget)
    while remaining_budget > 1e-12 and len(active_index) > 0:
        active_strength = raw_strength.loc[active_index]
        strength_sum = float(active_strength.sum())
        if strength_sum <= 1e-12:
            break
        proposed = (active_strength / strength_sum) * remaining_budget
        capped_this_round = []
        if bool((proposed <= engine_cap + 1e-12).all()):
            for idx, value in proposed.items():
                weights.loc[idx] += float(value)
            remaining_budget = 0.0
            break

        for idx, value in proposed.items():
            if float(value) <= engine_cap + 1e-12:
                continue
            additional_room = max(0.0, engine_cap - float(weights.loc[idx]))
            if additional_room > 1e-12:
                weights.loc[idx] += additional_room
                remaining_budget -= additional_room
            capped_this_round.append(idx)

        if len(capped_this_round) == 0:
            for idx, value in proposed.items():
                room = max(0.0, engine_cap - float(weights.loc[idx]))
                add_value = min(float(value), room)
                if add_value > 1e-12:
                    weights.loc[idx] += add_value
                    remaining_budget -= add_value
            break

        active_index = [idx for idx in active_index if idx not in capped_this_round and float(weights.loc[idx]) < engine_cap - 1e-12]
    return weights


def cap_final_weights(raw_weights: pd.Series, final_cap: float) -> pd.Series:
    return pd.to_numeric(raw_weights, errors="coerce").fillna(0.0).clip(lower=0.0, upper=final_cap)


def classify_state(score_value: float, low_cut: float, high_cut: float) -> str:
    if pd.isna(score_value):
        return "neutral_flat"
    if score_value >= high_cut:
        return "strong_up"
    if score_value <= low_cut:
        return "weak_down"
    return "neutral_flat"


def get_state_budgets(state_bucket: str) -> tuple[float, float]:
    if state_bucket == "strong_up":
        return 0.6, 0.4
    if state_bucket == "weak_down":
        return 1.0, 0.0
    return 0.8, 0.2


def evaluate_group(group: pd.DataFrame, fundamental_budget: float, momentum_budget: float) -> dict[str, object]:
    work = group.copy()
    work["fundamental_weight"] = build_engine_weights(work, FUNDAMENTAL_COMBO, fundamental_budget, ENGINE_STOCK_CAP)
    work["momentum_weight"] = build_engine_weights(work, "score__mom12", momentum_budget, ENGINE_STOCK_CAP)
    work["raw_final_weight"] = work["fundamental_weight"] + work["momentum_weight"]
    work["final_weight"] = cap_final_weights(work["raw_final_weight"], FINAL_STOCK_CAP)
    work["weighted_return"] = work["final_weight"] * pd.to_numeric(work[FUNDAMENTAL_TARGET_COL], errors="coerce").fillna(0.0)
    return {
        "portfolio_return": float(work["weighted_return"].sum()),
        "invested_weight": float(work["final_weight"].sum()),
        "cash_weight": float(max(0.0, 1.0 - work["final_weight"].sum())),
        "fundamental_stock_count": int((work["fundamental_weight"] > 0).sum()),
        "momentum_stock_count": int((work["momentum_weight"] > 0).sum()),
        "final_stock_count": int((work["final_weight"] > 0).sum()),
        "overlap_stock_count": int(((work["fundamental_weight"] > 0) & (work["momentum_weight"] > 0)).sum()),
        "max_final_weight": float(work["final_weight"].max()) if len(work) > 0 else np.nan,
    }


def build_detail_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)
        validation_mask = (panel_df["rebalance_date"] >= validation_start) & (panel_df["rebalance_date"] <= validation_end)

        scored_df = build_fundamental_score_frame(panel_df, train_mask)
        scored_df["score__mom12"] = preprocess_momentum_factor(scored_df, train_mask)

        train_state_df = (
            scored_df.loc[train_mask, ["rebalance_date", "observable_state_score_v1"]]
            .drop_duplicates()
            .dropna()
            .copy()
        )
        if train_state_df.empty:
            continue
        low_cut = float(train_state_df["observable_state_score_v1"].quantile(0.33))
        high_cut = float(train_state_df["observable_state_score_v1"].quantile(0.67))

        validation_df = scored_df[validation_mask].copy()
        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[FUNDAMENTAL_COMBO, "score__mom12", FUNDAMENTAL_TARGET_COL, "observable_state_score_v1"]).copy()
            if len(group) < 5:
                continue
            state_score = float(group["observable_state_score_v1"].iloc[0])
            state_bucket = classify_state(state_score, low_cut, high_cut)
            state_fundamental_budget, state_momentum_budget = get_state_budgets(state_bucket)

            for spec in BASELINE_STRATEGIES:
                if spec["mode"] == "state_gated":
                    fundamental_budget = state_fundamental_budget
                    momentum_budget = state_momentum_budget
                else:
                    fundamental_budget = float(spec["fundamental_budget"])
                    momentum_budget = float(spec["momentum_budget"])

                evaluated = evaluate_group(group, fundamental_budget, momentum_budget)
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "strategy_name": spec["strategy_name"],
                        "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                        "train_start": fold["train_start"],
                        "train_end": fold["train_end"],
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "universe_count": int(len(group)),
                        "state_score": round(state_score, 6),
                        "state_low_cut": round(low_cut, 6),
                        "state_high_cut": round(high_cut, 6),
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
                        "max_final_weight": round(float(evaluated["max_final_weight"]), 6),
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


def write_summary(rows: list[dict[str, object]], folds: list[dict[str, object]]) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# State-Gated Dual-Engine Rolling Validation V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- state proxy = observable-only `z_mcap + z_mom6_positive_ratio - z_money`",
        "- train-set terciles define `weak_down / neutral_flat / strong_up`",
        "- allocation mapping:",
        "- `strong_up` => `60%` fundamental + `40%` momentum",
        "- `neutral_flat` => `80%` fundamental + `20%` momentum",
        "- `weak_down` => `100%` fundamental + `0%` momentum",
        "- momentum engine = deployment-safe `mom_12_1`",
        "- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`",
        "- engine stock cap = `5%`",
        "- final stock cap = `8%`",
        "",
        f"- fold count: `{len(folds)}`",
        f"- strategy snapshots: `{df[['fold_id', 'strategy_name', 'rebalance_date']].drop_duplicates().shape[0] if not df.empty else 0}`",
        "",
    ]

    if not df.empty:
        lines.append("Strategy summary:")
        summary_df = (
            df.groupby("strategy_name", dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_invested_weight=("invested_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_cash_weight=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{format_float(row['mean_return'])}` | "
                f"cum_return=`{format_float(row['cumulative_return'])}` | "
                f"mean_invested_weight=`{format_float(row['mean_invested_weight'])}` | "
                f"mean_cash_weight=`{format_float(row['mean_cash_weight'])}`"
            )

        state_mix_df = df[df["strategy_name"] == "state_gated_dual_engine"].copy()
        if not state_mix_df.empty:
            lines.extend(["", "State mix summary:"])
            for state_bucket in ["strong_up", "neutral_flat", "weak_down"]:
                subset = state_mix_df[state_mix_df["state_bucket"] == state_bucket].copy()
                if subset.empty:
                    continue
                lines.append(
                    f"- `{state_bucket}` | snapshots=`{len(subset)}` | "
                    f"mean_return=`{format_float(pd.to_numeric(subset['portfolio_return'], errors='coerce').mean())}` | "
                    f"mean_f_budget=`{format_float(pd.to_numeric(subset['fundamental_budget'], errors='coerce').mean(), 2)}` | "
                    f"mean_m_budget=`{format_float(pd.to_numeric(subset['momentum_budget'], errors='coerce').mean(), 2)}`"
                )

        lines.extend(["", "Fold summary:"])
        for fold_id in sorted(df["fold_id"].unique()):
            fold_df = df[df["fold_id"] == fold_id].copy()
            for strategy_name in ["fundamental_only", "blend_80_20", "blend_60_40", "state_gated_dual_engine"]:
                subset = fold_df[fold_df["strategy_name"] == strategy_name].copy()
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
                "Interpretation:",
                "- this validation asks whether disabling momentum in weak states improves the fixed-budget dual-engine baseline",
                "- the observable state proxy is intentionally simple and leak-free",
                "- if state-gated results do not beat fixed `60/40`, the next step should focus on better state observables rather than more allocation complexity",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = build_joint_panel()
    folds = load_folds()
    rows = build_detail_rows(panel_df, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
