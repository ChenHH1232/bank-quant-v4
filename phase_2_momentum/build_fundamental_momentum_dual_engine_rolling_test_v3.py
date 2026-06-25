from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
FUNDAMENTAL_DIR = ROOT_DIR / "phase_1_fundamental"

if str(FUNDAMENTAL_DIR) not in sys.path:
    sys.path.insert(0, str(FUNDAMENTAL_DIR))

from build_pre2021_rolling_validation_v1 import (  # type: ignore
    add_combo_scores,
    build_scored_panel,
    load_panel as load_fundamental_panel,
    load_rows,
)

MOMENTUM_PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
SHORT_BOND_PANEL_PATH = SCRIPT_DIR / "short_bond_defensive_panel_v1.csv"
FUNDAMENTAL_FOLDS_PATH = FUNDAMENTAL_DIR / "pre2021_rolling_validation_v1_folds.csv"
FACTOR_POOL_PATH = FUNDAMENTAL_DIR / "final_core_factor_pool_v3.csv"
CORE_RESULTS_PATH = FUNDAMENTAL_DIR / "single_factor_test_results_core_v2.csv"
IMPROVEMENT_RESULTS_PATH = FUNDAMENTAL_DIR / "improvement_factor_test_results_v1.csv"

OUT_DETAIL_PATH = SCRIPT_DIR / "fundamental_momentum_dual_engine_rolling_test_v3_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "fundamental_momentum_dual_engine_rolling_test_v3.md"

ENGINE_STOCK_CAP = 0.05
FINAL_STOCK_CAP = 0.08
FUNDAMENTAL_COMBO = "combo__ic_weight_train"
FUNDAMENTAL_TARGET_COL = "y_quarter_avg_daily_return_close"
MOMENTUM_FACTOR_COL = "mom_12_1"

BALANCED_FACTOR_SET = [
    "indicator__roe",
    "indicator__eps",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]

CORE_LEVEL_FACTOR_SET = [
    "indicator__roe",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
    "bank_indicator__core_level_capital_adequacy_ratio",
]

FUNDAMENTAL_BRANCH_SPECS = [
    {
        "branch_name": "balanced",
        "factor_names": BALANCED_FACTOR_SET,
        "overlay_mode": "none",
    },
    {
        "branch_name": "core_level_shadow",
        "factor_names": CORE_LEVEL_FACTOR_SET,
        "overlay_mode": "none",
    },
    {
        "branch_name": "balanced_shortbond_6040_4055",
        "factor_names": BALANCED_FACTOR_SET,
        "overlay_mode": "shortbond_6040_4055",
    },
]

BASE_STRATEGY_SPECS = [
    {"strategy_name": "fundamental_only", "fundamental_budget": 1.0, "momentum_budget": 0.0},
    {"strategy_name": "blend_80_20", "fundamental_budget": 0.8, "momentum_budget": 0.2},
    {"strategy_name": "blend_70_30", "fundamental_budget": 0.7, "momentum_budget": 0.3},
    {"strategy_name": "blend_60_40", "fundamental_budget": 0.6, "momentum_budget": 0.4},
]

REGIME_METRICS = {
    "npl": {"column": "bank_indicator__Nonperforming_loan_rate", "higher_is_worse": True},
    "capital": {"column": "bank_indicator__capital_adequacy_ratio", "higher_is_worse": False},
    "coverage": {"column": "bank_indicator__non_performing_loan_provision_coverage", "higher_is_worse": False},
}


def load_momentum_panel() -> pd.DataFrame:
    df = pd.read_csv(MOMENTUM_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_stock_pool_flag_v2"] == 1].copy()
    df[MOMENTUM_FACTOR_COL] = pd.to_numeric(df[MOMENTUM_FACTOR_COL], errors="coerce")
    return df[["rebalance_date", "code", MOMENTUM_FACTOR_COL]].copy()


def load_short_bond_returns() -> pd.Series:
    df = pd.read_csv(SHORT_BOND_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["period_total_return"] = pd.to_numeric(df["period_total_return"], errors="coerce")
    return (
        df.dropna(subset=["rebalance_date", "period_total_return"])
        .drop_duplicates(subset=["rebalance_date"])
        .set_index("rebalance_date")["period_total_return"]
        .sort_index()
    )


def load_folds() -> list[dict[str, object]]:
    df = pd.read_csv(FUNDAMENTAL_FOLDS_PATH, encoding="utf-8-sig")
    return df.to_dict("records")


def load_factor_metadata_map() -> dict[str, dict[str, str]]:
    factor_pool_rows = load_rows(FACTOR_POOL_PATH)
    core_results = {row["factor_name"]: row for row in load_rows(CORE_RESULTS_PATH)}
    improvement_results = {row["factor_name"]: row for row in load_rows(IMPROVEMENT_RESULTS_PATH)}

    pool_meta = {
        row["factor_name"]: {
            "factor_name": row["factor_name"],
            "factor_family": row["factor_family"],
            "layer": row["layer"],
        }
        for row in factor_pool_rows
    }

    metadata_map: dict[str, dict[str, str]] = {}
    for factor_name, meta in pool_meta.items():
        factor_result = core_results.get(factor_name) or improvement_results.get(factor_name)
        if factor_result is None:
            continue
        metadata_map[factor_name] = {
            "factor_name": factor_name,
            "factor_family": meta["factor_family"],
            "layer": meta["layer"],
            "direction": factor_result["direction"],
            "target_label": factor_result["target_label"],
        }
    return metadata_map


def get_branch_metadata_rows(branch_spec: dict[str, object], metadata_map: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for factor_name in branch_spec["factor_names"]:
        meta = metadata_map.get(str(factor_name))
        if meta is None:
            raise KeyError(f"Missing metadata for {factor_name}")
        rows.append(meta.copy())
    return rows


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

    merged = fundamental_df.merge(momentum_df, on=["rebalance_date", "code"], how="inner")
    merged[FUNDAMENTAL_TARGET_COL] = pd.to_numeric(merged[FUNDAMENTAL_TARGET_COL], errors="coerce")
    merged = merged.dropna(subset=[FUNDAMENTAL_TARGET_COL]).copy()
    return merged


def build_regime_ratio_frame(panel_df: pd.DataFrame) -> pd.DataFrame:
    required_cols = ["rebalance_date", "code"] + [spec["column"] for spec in REGIME_METRICS.values()]
    work = panel_df[required_cols].copy()
    work["rebalance_date"] = pd.to_datetime(work["rebalance_date"])
    work = work.sort_values(["code", "rebalance_date"]).copy()

    for metric_name, spec in REGIME_METRICS.items():
        col = spec["column"]
        work[col] = pd.to_numeric(work[col], errors="coerce")
        prev_col = f"prev__{metric_name}"
        flag_col = f"flag__{metric_name}"
        work[prev_col] = work.groupby("code")[col].shift(1)
        if spec["higher_is_worse"]:
            work[flag_col] = np.where(
                work[col].notna() & work[prev_col].notna(),
                (work[col] > work[prev_col]).astype(float),
                np.nan,
            )
        else:
            work[flag_col] = np.where(
                work[col].notna() & work[prev_col].notna(),
                (work[col] < work[prev_col]).astype(float),
                np.nan,
            )

    rows: list[dict[str, object]] = []
    for rebalance_date, group in work.groupby("rebalance_date", sort=True):
        row: dict[str, object] = {"rebalance_date": pd.Timestamp(rebalance_date)}
        signal_values = []
        for metric_name in REGIME_METRICS:
            valid = pd.to_numeric(group[f"flag__{metric_name}"], errors="coerce").dropna()
            ratio = float(valid.mean()) if not valid.empty else np.nan
            row[f"ratio__{metric_name}"] = ratio
            signal_values.append(ratio)
        valid_signal_values = [value for value in signal_values if pd.notna(value)]
        row["signal_value"] = float(np.mean(valid_signal_values)) if valid_signal_values else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def classify_overlay(signal_value: float) -> tuple[str, float]:
    if pd.isna(signal_value):
        return "normal", 1.0
    if signal_value >= 0.55:
        return "severe", 0.40
    if signal_value >= 0.40:
        return "warning", 0.60
    return "normal", 1.0


def build_fundamental_score_frame(
    panel_df: pd.DataFrame,
    train_mask: pd.Series,
    branch_spec: dict[str, object],
    metadata_map: dict[str, dict[str, str]],
) -> pd.DataFrame:
    metadata_rows = get_branch_metadata_rows(branch_spec, metadata_map)
    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, metadata_rows, train_mask)
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

        active_index = [
            idx for idx in active_index
            if idx not in capped_this_round and float(weights.loc[idx]) < engine_cap - 1e-12
        ]
    return weights


def cap_final_weights(raw_weights: pd.Series, final_cap: float) -> pd.Series:
    return pd.to_numeric(raw_weights, errors="coerce").fillna(0.0).clip(lower=0.0, upper=final_cap)


def evaluate_group(
    group: pd.DataFrame,
    branch_spec: dict[str, object],
    fundamental_budget: float,
    momentum_budget: float,
    short_bond_returns: pd.Series,
) -> dict[str, object]:
    work = group.copy()
    overlay_mode = str(branch_spec["overlay_mode"])
    fundamental_equity_budget = float(fundamental_budget)
    defensive_budget = 0.0
    overlay_regime = "none"
    overlay_signal = np.nan
    short_bond_return = np.nan

    if overlay_mode == "shortbond_6040_4055":
        overlay_signal = pd.to_numeric(work["signal_value"], errors="coerce").dropna().iloc[0] if work["signal_value"].notna().any() else np.nan
        overlay_regime, equity_weight = classify_overlay(float(overlay_signal) if pd.notna(overlay_signal) else np.nan)
        fundamental_equity_budget = float(fundamental_budget) * equity_weight
        defensive_budget = float(fundamental_budget) * (1.0 - equity_weight)
        rebalance_date = pd.Timestamp(work["rebalance_date"].iloc[0])
        short_bond_return = float(short_bond_returns.get(rebalance_date, np.nan))

    work["fundamental_weight"] = build_engine_weights(
        work, FUNDAMENTAL_COMBO, fundamental_equity_budget, ENGINE_STOCK_CAP
    )
    work["momentum_weight"] = build_engine_weights(
        work, "score__mom12", momentum_budget, ENGINE_STOCK_CAP
    )
    work["raw_final_weight"] = work["fundamental_weight"] + work["momentum_weight"]
    work["final_weight"] = cap_final_weights(work["raw_final_weight"], FINAL_STOCK_CAP)
    work["weighted_return"] = (
        work["final_weight"] * pd.to_numeric(work[FUNDAMENTAL_TARGET_COL], errors="coerce").fillna(0.0)
    )
    stock_return = float(work["weighted_return"].sum())
    defensive_return = defensive_budget * short_bond_return if pd.notna(short_bond_return) else 0.0
    portfolio_return = stock_return + defensive_return
    invested_weight = float(work["final_weight"].sum()) + defensive_budget

    return {
        "portfolio_return": float(portfolio_return),
        "stock_return_component": float(stock_return),
        "defensive_return_component": float(defensive_return),
        "invested_weight": float(invested_weight),
        "cash_weight": float(max(0.0, 1.0 - invested_weight)),
        "fundamental_stock_count": int((work["fundamental_weight"] > 0).sum()),
        "momentum_stock_count": int((work["momentum_weight"] > 0).sum()),
        "final_stock_count": int((work["final_weight"] > 0).sum()),
        "overlap_stock_count": int(((work["fundamental_weight"] > 0) & (work["momentum_weight"] > 0)).sum()),
        "max_final_weight": float(work["final_weight"].max()) if len(work) > 0 else np.nan,
        "defensive_weight": float(defensive_budget),
        "overlay_regime": overlay_regime,
        "overlay_signal": overlay_signal,
        "short_bond_return": short_bond_return,
    }


def build_detail_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    metadata_map = load_factor_metadata_map()
    short_bond_returns = load_short_bond_returns()
    regime_df = build_regime_ratio_frame(panel_df)

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)
        validation_mask = (panel_df["rebalance_date"] >= validation_start) & (panel_df["rebalance_date"] <= validation_end)

        for branch_spec in FUNDAMENTAL_BRANCH_SPECS:
            scored_df = build_fundamental_score_frame(panel_df, train_mask, branch_spec, metadata_map)
            scored_df["score__mom12"] = preprocess_momentum_factor(scored_df, train_mask)
            scored_df = scored_df.merge(regime_df, on="rebalance_date", how="left")

            validation_df = scored_df[validation_mask].copy()
            for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
                group = group.dropna(subset=[FUNDAMENTAL_COMBO, "score__mom12", FUNDAMENTAL_TARGET_COL]).copy()
                if len(group) < 5:
                    continue

                for spec in BASE_STRATEGY_SPECS:
                    evaluated = evaluate_group(
                        group=group,
                        branch_spec=branch_spec,
                        fundamental_budget=float(spec["fundamental_budget"]),
                        momentum_budget=float(spec["momentum_budget"]),
                        short_bond_returns=short_bond_returns,
                    )
                    rows.append(
                        {
                            "branch_name": branch_spec["branch_name"],
                            "fold_id": fold["fold_id"],
                            "strategy_name": spec["strategy_name"],
                            "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                            "train_start": fold["train_start"],
                            "train_end": fold["train_end"],
                            "validation_start": fold["validation_start"],
                            "validation_end": fold["validation_end"],
                            "universe_count": int(len(group)),
                            "fundamental_budget": spec["fundamental_budget"],
                            "momentum_budget": spec["momentum_budget"],
                            "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                            "stock_return_component": round(float(evaluated["stock_return_component"]), 10),
                            "defensive_return_component": round(float(evaluated["defensive_return_component"]), 10),
                            "invested_weight": round(float(evaluated["invested_weight"]), 6),
                            "cash_weight": round(float(evaluated["cash_weight"]), 6),
                            "defensive_weight": round(float(evaluated["defensive_weight"]), 6),
                            "fundamental_stock_count": int(evaluated["fundamental_stock_count"]),
                            "momentum_stock_count": int(evaluated["momentum_stock_count"]),
                            "final_stock_count": int(evaluated["final_stock_count"]),
                            "overlap_stock_count": int(evaluated["overlap_stock_count"]),
                            "max_final_weight": round(float(evaluated["max_final_weight"]), 6),
                            "overlay_regime": evaluated["overlay_regime"],
                            "overlay_signal": round(float(evaluated["overlay_signal"]), 6) if pd.notna(evaluated["overlay_signal"]) else "",
                            "short_bond_return": round(float(evaluated["short_bond_return"]), 10) if pd.notna(evaluated["short_bond_return"]) else "",
                        }
                    )

    momentum_only_rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])
        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)
        panel_copy = panel_df.copy()
        panel_copy["score__mom12"] = preprocess_momentum_factor(panel_copy, train_mask)
        validation_df = panel_copy[(panel_copy["rebalance_date"] >= validation_start) & (panel_copy["rebalance_date"] <= validation_end)].copy()
        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=["score__mom12", FUNDAMENTAL_TARGET_COL]).copy()
            if len(group) < 5:
                continue
            weights = build_engine_weights(group, "score__mom12", 1.0, ENGINE_STOCK_CAP)
            final_weights = cap_final_weights(weights, FINAL_STOCK_CAP)
            portfolio_return = float((final_weights * pd.to_numeric(group[FUNDAMENTAL_TARGET_COL], errors="coerce").fillna(0.0)).sum())
            invested_weight = float(final_weights.sum())
            momentum_only_rows.append(
                {
                    "branch_name": "shared_momentum_baseline",
                    "fold_id": fold["fold_id"],
                    "strategy_name": "momentum_only",
                    "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                    "train_start": fold["train_start"],
                    "train_end": fold["train_end"],
                    "validation_start": fold["validation_start"],
                    "validation_end": fold["validation_end"],
                    "universe_count": int(len(group)),
                    "fundamental_budget": 0.0,
                    "momentum_budget": 1.0,
                    "portfolio_return": round(float(portfolio_return), 10),
                    "stock_return_component": round(float(portfolio_return), 10),
                    "defensive_return_component": 0.0,
                    "invested_weight": round(float(invested_weight), 6),
                    "cash_weight": round(float(max(0.0, 1.0 - invested_weight)), 6),
                    "defensive_weight": 0.0,
                    "fundamental_stock_count": 0,
                    "momentum_stock_count": int((weights > 0).sum()),
                    "final_stock_count": int((final_weights > 0).sum()),
                    "overlap_stock_count": 0,
                    "max_final_weight": round(float(final_weights.max()), 6),
                    "overlay_regime": "none",
                    "overlay_signal": "",
                    "short_bond_return": "",
                }
            )
    rows.extend(momentum_only_rows)
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


def compute_max_drawdown_from_returns(returns: pd.Series) -> float:
    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if clean.empty:
        return np.nan
    nav = (1.0 + clean).cumprod()
    running_peak = nav.cummax()
    drawdown = (nav / running_peak) - 1.0
    return float(drawdown.min())


def compute_excess_metrics(
    strategy_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
) -> tuple[float, float, float]:
    merged = strategy_df.merge(
        baseline_df[["rebalance_date", "portfolio_return"]].rename(
            columns={"portfolio_return": "baseline_return"}
        ),
        on="rebalance_date",
        how="inner",
    )
    if merged.empty:
        return np.nan, np.nan, np.nan

    strategy_returns = pd.to_numeric(merged["portfolio_return"], errors="coerce")
    baseline_returns = pd.to_numeric(merged["baseline_return"], errors="coerce")
    clean = pd.DataFrame(
        {
            "strategy_return": strategy_returns,
            "baseline_return": baseline_returns,
        }
    ).dropna()
    if clean.empty:
        return np.nan, np.nan, np.nan

    strategy_nav = (1.0 + clean["strategy_return"]).cumprod()
    baseline_nav = (1.0 + clean["baseline_return"]).cumprod()
    excess_nav = strategy_nav / baseline_nav
    excess_return = float(excess_nav.iloc[-1] - 1.0)
    running_peak = excess_nav.cummax()
    excess_drawdown = (excess_nav / running_peak) - 1.0
    excess_max_drawdown = float(excess_drawdown.min())
    mean_excess_return = float((clean["strategy_return"] - clean["baseline_return"]).mean())
    return excess_return, excess_max_drawdown, mean_excess_return


def write_summary(rows: list[dict[str, object]], folds: list[dict[str, object]]) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# Fundamental Momentum Dual-Engine Rolling Test V3",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- common rebalance dates = intersection of fundamental and momentum panels",
        "- folds reuse the fundamental pre-2021 rolling framework",
        "- momentum sleeve is fixed at deployment-safe `mom_12_1`",
        "- allocation framework is unchanged: separate sleeves, fixed budgets, `5%` engine cap, `8%` final stock cap",
        "- only the fundamental sleeve varies across the three current formal main lines",
        "",
        "Fundamental sleeve candidates:",
        "- `balanced` = `base_core_6 + combo__ic_weight_train`",
        "- `core_level_shadow` = `base_core_6 - eps + core_level_capital_adequacy_ratio`",
        "- `balanced_shortbond_6040_4055` = `balanced` stock sleeve plus short-bond defensive overlay",
        "",
        f"- fold count: `{len(folds)}`",
        f"- rebalance snapshots: `{df[['branch_name', 'strategy_name', 'rebalance_date']].drop_duplicates().shape[0] if not df.empty else 0}`",
        "",
    ]

    if not df.empty:
        baseline_df = (
            df[
                (df["branch_name"] == "shared_momentum_baseline")
                & (df["strategy_name"] == "momentum_only")
            ][["rebalance_date", "portfolio_return"]]
            .copy()
        )
        baseline_df["rebalance_date"] = pd.to_datetime(baseline_df["rebalance_date"])
        lines.append("Strategy summary by branch:")
        summary_rows: list[dict[str, object]] = []
        for (branch_name, strategy_name), subset in df.groupby(["branch_name", "strategy_name"], dropna=False):
            subset = subset.copy().sort_values("rebalance_date")
            subset["rebalance_date"] = pd.to_datetime(subset["rebalance_date"])
            cumulative_return = float((1.0 + pd.to_numeric(subset["portfolio_return"], errors="coerce")).prod() - 1.0)
            strategy_max_drawdown = compute_max_drawdown_from_returns(subset["portfolio_return"])
            excess_return, excess_max_drawdown, mean_excess_return = compute_excess_metrics(subset, baseline_df)
            summary_rows.append(
                {
                    "branch_name": branch_name,
                    "strategy_name": strategy_name,
                    "snapshot_count": int(len(subset)),
                    "mean_return": pd.to_numeric(subset["portfolio_return"], errors="coerce").mean(),
                    "cumulative_return": cumulative_return,
                    "strategy_max_drawdown": strategy_max_drawdown,
                    "excess_return_vs_mom_only": excess_return,
                    "excess_max_drawdown_vs_mom_only": excess_max_drawdown,
                    "mean_excess_return_vs_mom_only": mean_excess_return,
                    "mean_invested_weight": pd.to_numeric(subset["invested_weight"], errors="coerce").mean(),
                    "mean_cash_weight": pd.to_numeric(subset["cash_weight"], errors="coerce").mean(),
                    "mean_defensive_weight": pd.to_numeric(subset["defensive_weight"], errors="coerce").mean(),
                }
            )
        summary_df = pd.DataFrame(summary_rows).sort_values(["strategy_name", "cumulative_return"], ascending=[True, False])
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['branch_name']}` `{row['strategy_name']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{format_float(row['mean_return'])}` | "
                f"cum_return=`{format_float(row['cumulative_return'])}` | "
                f"strategy_mdd=`{format_float(row['strategy_max_drawdown'])}` | "
                f"excess_return_vs_mom=`{format_float(row['excess_return_vs_mom_only'])}` | "
                f"excess_mdd_vs_mom=`{format_float(row['excess_max_drawdown_vs_mom_only'])}` | "
                f"mean_invested_weight=`{format_float(row['mean_invested_weight'])}` | "
                f"mean_cash_weight=`{format_float(row['mean_cash_weight'])}` | "
                f"mean_defensive_weight=`{format_float(row['mean_defensive_weight'])}`"
            )

        lines.extend(["", "Best branch inside each allocation spec:"])
        for strategy_name in ["fundamental_only", "blend_80_20", "blend_70_30", "blend_60_40"]:
            subset = summary_df[summary_df["strategy_name"] == strategy_name].copy()
            if subset.empty:
                continue
            best = subset.sort_values(["cumulative_return", "mean_return"], ascending=[False, False]).iloc[0]
            lines.append(
                f"- `{strategy_name}` best branch = `{best['branch_name']}` | "
                f"cum_return=`{format_float(best['cumulative_return'])}` | "
                f"mean_return=`{format_float(best['mean_return'])}` | "
                f"excess_mdd_vs_mom=`{format_float(best['excess_max_drawdown_vs_mom_only'])}`"
            )

        momentum_subset = summary_df[summary_df["strategy_name"] == "momentum_only"].copy()
        if not momentum_subset.empty:
            row = momentum_subset.iloc[0]
            lines.extend(
                [
                    "",
                    "Shared baseline:",
                    f"- `momentum_only` | snapshots=`{int(row['snapshot_count'])}` | "
                    f"cum_return=`{format_float(row['cumulative_return'])}` | "
                    f"mean_return=`{format_float(row['mean_return'])}` | "
                    f"strategy_mdd=`{format_float(row['strategy_max_drawdown'])}`",
                ]
            )

        lines.extend(
            [
                "",
                "Interpretation targets:",
                "- compare whether updating the fundamental sleeve ranking alone improves the old separate-budget framework",
                "- compare whether `core_level_shadow` helps more on relative path than `balanced` inside the same momentum blend",
                "- compare whether `balanced_shortbond_6040_4055` improves capital preservation enough to justify lower equity exposure inside the blend",
                "- compare whether a branch with slightly lower return still earns credit by reducing excess max drawdown versus the shared momentum baseline",
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
