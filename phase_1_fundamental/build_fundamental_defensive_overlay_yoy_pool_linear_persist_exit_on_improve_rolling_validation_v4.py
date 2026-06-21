from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_BASE,
    add_combo_scores,
    build_scenario_rows,
    build_scored_panel,
    build_yearly_folds,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
    select_factor_rows,
)
from build_pre2021_rolling_validation_v1 import assign_groups


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
MOMENTUM_DIR = ROOT_DIR / "phase_2_momentum"

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "fundamental_defensive_overlay_yoy_pool_linear_persist_exit_on_improve_rolling_validation_v4_config_results.csv"
OUTPUT_CHOSEN_PATH = SCRIPT_DIR / "fundamental_defensive_overlay_yoy_pool_linear_persist_exit_on_improve_rolling_validation_v4_chosen.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "fundamental_defensive_overlay_yoy_pool_linear_persist_exit_on_improve_rolling_validation_v4.md"

TARGET_COMBO = "combo__ic_weight_train"
TARGET_TARGET_COL = "y_quarter_avg_daily_return_close"
BASELINE_CONFIG_KEY = "baseline__100pct_equity"

STOCK_DETERIORATION_THRESHOLDS = [0.60]
MIN_VALID_FACTOR_COUNT = 2
DEFENSIVE_ASSET_NAME = "treasury_etf_511010"
DEFENSIVE_ASSET_PATH = MOMENTUM_DIR / "bond_defensive_panel_full_v1.csv"
DEFENSIVE_ASSET_RETURN_COL = "period_total_return"
PERSISTENCE_ADD_2 = 0.10
PERSISTENCE_ADD_3P = 0.20
DEFENSIVE_WEIGHT_CAP = 0.60


def load_asset_returns() -> pd.Series:
    if not DEFENSIVE_ASSET_PATH.exists():
        return pd.Series(dtype="float64")
    df = pd.read_csv(DEFENSIVE_ASSET_PATH, encoding="utf-8-sig")
    if "rebalance_date" not in df.columns or DEFENSIVE_ASSET_RETURN_COL not in df.columns:
        return pd.Series(dtype="float64")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df[DEFENSIVE_ASSET_RETURN_COL] = pd.to_numeric(df[DEFENSIVE_ASSET_RETURN_COL], errors="coerce")
    return (
        df.dropna(subset=["rebalance_date", DEFENSIVE_ASSET_RETURN_COL])
        .drop_duplicates(subset=["rebalance_date"])
        .set_index("rebalance_date")[DEFENSIVE_ASSET_RETURN_COL]
        .sort_index()
    )


def build_master_frame(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
    asset_returns: pd.Series,
) -> pd.DataFrame:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)
    context_start = train_start - pd.DateOffset(years=1)

    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    context_mask = (panel_df["rebalance_date"] >= context_start) & (panel_df["rebalance_date"] < review_end)

    selected_rows, _ = select_factor_rows(panel_df, universe_rows, fold)
    scenario_map = build_scenario_rows(selected_rows, base_rows, enhanced_rows)
    factor_specs = scenario_map.get(SCENARIO_BASE, [])
    if not factor_specs:
        return pd.DataFrame()

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df[context_mask].copy(), factor_specs, train_mask[context_mask])
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty:
        return pd.DataFrame()

    work = scored_df.copy()
    work["rebalance_date"] = pd.to_datetime(work["rebalance_date"])
    work = work.sort_values(["code", "rebalance_date"]).copy()

    factor_names = [spec["factor_name"] for spec in factor_specs]
    direction_map = {
        spec["factor_name"]: (1 if str(spec.get("direction", "")).lower() == "larger_better" else -1)
        for spec in factor_specs
    }
    valid_factor_names = [name for name in factor_names if name in work.columns]
    if not valid_factor_names:
        return pd.DataFrame()

    for factor_name in valid_factor_names:
        work[f"yoy_prev__{factor_name}"] = work.groupby("code")[factor_name].shift(3)
        current = pd.to_numeric(work[factor_name], errors="coerce")
        prev = pd.to_numeric(work[f"yoy_prev__{factor_name}"], errors="coerce")
        if direction_map[factor_name] > 0:
            flag = np.where(current.notna() & prev.notna(), (current < prev).astype(float), np.nan)
        else:
            flag = np.where(current.notna() & prev.notna(), (current > prev).astype(float), np.nan)
        work[f"flag__{factor_name}"] = flag

    rows: list[dict[str, object]] = []
    min_required = min(MIN_VALID_FACTOR_COUNT, len(valid_factor_names))
    eval_mask = (work["rebalance_date"] >= train_start) & (work["rebalance_date"] < review_end)
    for rebalance_date, group in work[eval_mask].groupby("rebalance_date", sort=True):
        equity_group = group.dropna(subset=[TARGET_COMBO, TARGET_TARGET_COL]).copy()
        if len(equity_group) < 5:
            continue
        equity_group["bucket"] = assign_groups(equity_group[TARGET_COMBO], 5)
        equity_group = equity_group.dropna(subset=["bucket"]).copy()
        top_group = equity_group[equity_group["bucket"] == 5].copy()
        if top_group.empty:
            continue

        pool_group = group.dropna(subset=[TARGET_COMBO]).copy()
        if "liquidity_top_80_flag" in pool_group.columns:
            pool_group = pool_group[pd.to_numeric(pool_group["liquidity_top_80_flag"], errors="coerce") == 1].copy()
        if "market_cap_top_80_flag" in pool_group.columns:
            pool_group = pool_group[pd.to_numeric(pool_group["market_cap_top_80_flag"], errors="coerce") == 1].copy()
        flag_cols = [f"flag__{name}" for name in valid_factor_names if f"flag__{name}" in pool_group.columns]
        if not flag_cols:
            continue
        flag_frame = pool_group[flag_cols].apply(pd.to_numeric, errors="coerce")
        pool_group["valid_factor_count"] = flag_frame.notna().sum(axis=1)
        pool_group["deteriorated_factor_count"] = flag_frame.fillna(0.0).sum(axis=1)
        pool_group["deterioration_ratio"] = pool_group["deteriorated_factor_count"] / pool_group["valid_factor_count"].replace({0: np.nan})
        eligible = pool_group[pool_group["valid_factor_count"] >= min_required].copy()
        if eligible.empty:
            continue

        row: dict[str, object] = {
            "rebalance_date": pd.Timestamp(rebalance_date),
            "equity_return": float(pd.to_numeric(top_group[TARGET_TARGET_COL], errors="coerce").mean()),
            "selected_count": int(len(top_group)),
            "pool_stock_count": int(len(pool_group)),
            "eligible_stock_count": int(len(eligible)),
        }
        for threshold in STOCK_DETERIORATION_THRESHOLDS:
            stock_flag = pd.to_numeric(eligible["deterioration_ratio"], errors="coerce") >= float(threshold)
            row[f"signal_ratio__thr_{int(round(threshold * 100))}"] = float(stock_flag.mean()) if len(stock_flag) > 0 else np.nan
            row[f"deteriorated_count__thr_{int(round(threshold * 100))}"] = int(stock_flag.sum())
        rows.append(row)

    master = pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)
    if master.empty:
        return master
    master["asset_return"] = master["rebalance_date"].map(asset_returns.to_dict()) if not asset_returns.empty else np.nan
    master["window_label"] = np.where(
        master["rebalance_date"] < test_start,
        "train",
        np.where(master["rebalance_date"] < review_start, "test", "review"),
    )
    return master


def summarize_baseline_window(df: pd.DataFrame) -> dict[str, object]:
    work = df.copy()
    work["equity_return"] = pd.to_numeric(work["equity_return"], errors="coerce")
    covered = work[work["equity_return"].notna()].copy()
    if covered.empty:
        return {
            "snapshot_count": int(len(work)),
            "covered_snapshot_count": 0,
            "coverage_ratio": 0.0,
            "mean_portfolio_return": np.nan,
            "cum_portfolio_return": np.nan,
        }
    returns = pd.to_numeric(covered["equity_return"], errors="coerce")
    return {
        "snapshot_count": int(len(work)),
        "covered_snapshot_count": int(len(covered)),
        "coverage_ratio": float(len(covered) / len(work)) if len(work) > 0 else 0.0,
        "mean_portfolio_return": float(returns.mean()),
        "cum_portfolio_return": float((1.0 + returns).prod() - 1.0),
    }


def summarize_window(df: pd.DataFrame, stock_threshold: float) -> dict[str, object]:
    work = df.copy()
    threshold_key = int(round(stock_threshold * 100))
    signal_col = f"signal_ratio__thr_{threshold_key}"
    work["signal_value"] = pd.to_numeric(work[signal_col], errors="coerce")
    bad_streaks: list[int] = []
    persistence_adds: list[float] = []
    defensive_weights: list[float] = []
    current_streak = 0
    previous_signal = np.nan
    for signal_value in pd.to_numeric(work["signal_value"], errors="coerce").tolist():
        if pd.isna(signal_value):
            current_streak = 0
            persistence_add = 0.0
            defensive_weight = np.nan
        elif pd.notna(previous_signal) and signal_value < previous_signal:
            current_streak = 0
            persistence_add = 0.0
            defensive_weight = 0.0
        elif signal_value > 0:
            current_streak += 1
            if current_streak >= 3:
                persistence_add = PERSISTENCE_ADD_3P
            elif current_streak >= 2:
                persistence_add = PERSISTENCE_ADD_2
            else:
                persistence_add = 0.0
            defensive_weight = min(DEFENSIVE_WEIGHT_CAP, max(0.0, float(signal_value) + float(persistence_add)))
        else:
            current_streak = 0
            persistence_add = 0.0
            defensive_weight = 0.0
        bad_streaks.append(current_streak)
        persistence_adds.append(persistence_add)
        defensive_weights.append(defensive_weight)
        previous_signal = signal_value if pd.notna(signal_value) else previous_signal
    work["bad_streak"] = bad_streaks
    work["persistence_add"] = persistence_adds
    work["defensive_weight"] = defensive_weights
    work["equity_weight"] = 1.0 - work["defensive_weight"]
    work["defensive_return"] = pd.to_numeric(work["asset_return"], errors="coerce")
    coverage_mask = work["equity_return"].notna() & work["defensive_return"].notna() & work["signal_value"].notna()
    covered = work[coverage_mask].copy()
    if covered.empty:
        return {
            "snapshot_count": int(len(work)),
            "covered_snapshot_count": 0,
            "coverage_ratio": 0.0,
            "mean_portfolio_return": np.nan,
            "cum_portfolio_return": np.nan,
            "mean_equity_return": np.nan,
            "cum_equity_return": np.nan,
            "mean_signal_value": np.nan,
            "mean_equity_weight": np.nan,
            "mean_defensive_weight": np.nan,
            "mean_persistence_add": np.nan,
            "max_bad_streak": np.nan,
        }

    covered["portfolio_return"] = (
        covered["equity_weight"] * pd.to_numeric(covered["equity_return"], errors="coerce")
        + covered["defensive_weight"] * pd.to_numeric(covered["defensive_return"], errors="coerce")
    )
    equity_returns = pd.to_numeric(covered["equity_return"], errors="coerce")
    portfolio_returns = pd.to_numeric(covered["portfolio_return"], errors="coerce")
    return {
        "snapshot_count": int(len(work)),
        "covered_snapshot_count": int(len(covered)),
        "coverage_ratio": float(len(covered) / len(work)) if len(work) > 0 else 0.0,
        "mean_portfolio_return": float(portfolio_returns.mean()),
        "cum_portfolio_return": float((1.0 + portfolio_returns).prod() - 1.0),
        "mean_equity_return": float(equity_returns.mean()),
        "cum_equity_return": float((1.0 + equity_returns).prod() - 1.0),
        "mean_signal_value": float(pd.to_numeric(covered["signal_value"], errors="coerce").mean()),
        "mean_equity_weight": float(pd.to_numeric(covered["equity_weight"], errors="coerce").mean()),
        "mean_defensive_weight": float(pd.to_numeric(covered["defensive_weight"], errors="coerce").mean()),
        "mean_persistence_add": float(pd.to_numeric(covered["persistence_add"], errors="coerce").mean()),
        "max_bad_streak": int(pd.to_numeric(covered["bad_streak"], errors="coerce").max()),
    }


def flatten_window_metrics(window_metrics: dict[str, dict[str, object]]) -> dict[str, object]:
    flattened: dict[str, object] = {}
    for window_label, metrics in window_metrics.items():
        for key, value in metrics.items():
            flattened[f"{window_label}__{key}"] = value
    return flattened


def compute_selection_score(window_metrics: dict[str, dict[str, object]]) -> float:
    train_cum = window_metrics["train"]["cum_portfolio_return"]
    test_cum = window_metrics["test"]["cum_portfolio_return"]
    train_cov = window_metrics["train"]["coverage_ratio"]
    test_cov = window_metrics["test"]["coverage_ratio"]
    if any(pd.isna(value) for value in [train_cum, test_cum]) or train_cov < 1.0 or test_cov < 1.0:
        return np.nan
    return float(test_cum * 1000.0 + train_cum)


def build_config_rows(master_df: pd.DataFrame, fold: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    baseline_by_window = {
        window_label: summarize_baseline_window(master_df[master_df["window_label"] == window_label].copy())
        for window_label in ["train", "test", "review"]
    }
    rows.append(
        {
            "fold_id": fold["fold_id"],
            "config_key": BASELINE_CONFIG_KEY,
            "stock_deterioration_threshold": "",
            "asset_name": "cash",
            "selection_status": "baseline",
            **flatten_window_metrics(baseline_by_window),
            "selection_score": np.nan,
        }
    )

    for threshold in STOCK_DETERIORATION_THRESHOLDS:
        window_metrics = {
            window_label: summarize_window(master_df[master_df["window_label"] == window_label].copy(), threshold)
            for window_label in ["train", "test", "review"]
        }
        rows.append(
            {
                "fold_id": fold["fold_id"],
                "config_key": f"yoy_pool_linear_persist__thr_{int(round(threshold * 100))}__asset_{DEFENSIVE_ASSET_NAME}",
                "stock_deterioration_threshold": threshold,
                "asset_name": DEFENSIVE_ASSET_NAME,
                "selection_status": "candidate",
                **flatten_window_metrics(window_metrics),
                "selection_score": compute_selection_score(window_metrics),
            }
        )
    return rows


def choose_best_configs(config_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    df = pd.DataFrame(config_rows)
    chosen_rows: list[dict[str, object]] = []
    for fold_id, fold_df in df.groupby("fold_id", sort=True):
        baseline_row = fold_df[fold_df["config_key"] == BASELINE_CONFIG_KEY].iloc[0].to_dict()
        candidate_df = fold_df[
            (fold_df["config_key"] != BASELINE_CONFIG_KEY)
            & (fold_df["test__coverage_ratio"] >= 1.0)
            & (fold_df["review__coverage_ratio"] >= 1.0)
            & pd.to_numeric(fold_df["selection_score"], errors="coerce").notna()
        ].copy()
        if candidate_df.empty:
            baseline_row["selection_status"] = "chosen_baseline_no_candidate"
            chosen_rows.append(baseline_row)
            continue

        baseline_train = pd.to_numeric(pd.Series([baseline_row["train__cum_portfolio_return"]]), errors="coerce").iloc[0]
        baseline_test = pd.to_numeric(pd.Series([baseline_row["test__cum_portfolio_return"]]), errors="coerce").iloc[0]
        candidate_df["train__cum_portfolio_return"] = pd.to_numeric(candidate_df["train__cum_portfolio_return"], errors="coerce")
        candidate_df["test__cum_portfolio_return"] = pd.to_numeric(candidate_df["test__cum_portfolio_return"], errors="coerce")
        admissible = candidate_df[
            (candidate_df["train__cum_portfolio_return"] >= baseline_train)
            & (candidate_df["test__cum_portfolio_return"] > baseline_test)
        ].copy()
        pool = admissible if not admissible.empty else candidate_df
        pool["selection_score"] = pd.to_numeric(pool["selection_score"], errors="coerce")
        chosen = pool.sort_values(
            ["selection_score", "test__cum_portfolio_return", "train__cum_portfolio_return"],
            ascending=[False, False, False],
        ).iloc[0].to_dict()
        chosen["selection_status"] = "chosen_overlay" if not admissible.empty else "chosen_best_available"
        chosen_rows.append(chosen)
    return chosen_rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key in seen:
                continue
            seen.add(key)
            fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.{digits}f}"


def write_summary(config_rows: list[dict[str, object]], chosen_rows: list[dict[str, object]]) -> None:
    config_df = pd.DataFrame(config_rows)
    chosen_df = pd.DataFrame(chosen_rows)
    threshold_text = " / ".join(f"{int(round(v * 100))}%" for v in STOCK_DETERIORATION_THRESHOLDS)
    lines = [
        "# Fundamental Defensive Overlay YOY Pool Linear Persist Exit-On-Improve Rolling Validation V4",
        "",
        "Protocol:",
        "- base execution line = annual pure-fundamental `base_core_7 + combo__ic_weight_train`",
        "- overlay compares each active annual factor against the same seasonal point one year earlier",
        "- deterioration is measured inside the candidate pool after score availability plus liquidity and market-cap filters",
        "- one stock is counted as deteriorated when its deteriorated-factor share crosses the tested threshold",
        "- treasury weight starts from deteriorated-stock ratio",
        "- consecutive bad rebalances add `+10%` on streak 2 and `+20%` on streak 3+",
        "- if the current deterioration signal improves versus the previous rebalance, defense exits immediately",
        f"- treasury weight cap = `{int(round(DEFENSIVE_WEIGHT_CAP * 100))}%`",
        f"- tested stock deterioration thresholds = `{threshold_text}`",
        f"- defensive asset = `{DEFENSIVE_ASSET_NAME}`",
        "",
        "Chosen fold results:",
    ]
    for _, row in chosen_df.sort_values("fold_id").iterrows():
        lines.append(
            f"- `{row['fold_id']}` | status=`{row['selection_status']}` | config=`{row['config_key']}` | "
            f"threshold=`{row.get('stock_deterioration_threshold', 'n/a')}` | "
            f"train_cum=`{format_float(row.get('train__cum_portfolio_return'))}` | "
            f"test_cum=`{format_float(row.get('test__cum_portfolio_return'))}` | "
            f"review_cum=`{format_float(row.get('review__cum_portfolio_return'))}` | "
            f"review_mean_signal=`{format_float(row.get('review__mean_signal_value'))}` | "
            f"review_mean_treasury_weight=`{format_float(row.get('review__mean_defensive_weight'))}` | "
            f"review_mean_persist_add=`{format_float(row.get('review__mean_persistence_add'))}` | "
            f"review_max_bad_streak=`{row.get('review__max_bad_streak', 'n/a')}`"
        )

    baseline_df = config_df[config_df["config_key"] == BASELINE_CONFIG_KEY].copy()
    if not baseline_df.empty and not chosen_df.empty:
        joined = chosen_df.merge(
            baseline_df[["fold_id", "review__cum_portfolio_return", "review__mean_portfolio_return"]].rename(
                columns={
                    "review__cum_portfolio_return": "baseline_review_cum",
                    "review__mean_portfolio_return": "baseline_review_mean",
                }
            ),
            on="fold_id",
            how="left",
        )
        joined["review_cum_advantage"] = pd.to_numeric(joined["review__cum_portfolio_return"], errors="coerce") - pd.to_numeric(joined["baseline_review_cum"], errors="coerce")
        joined["review_mean_advantage"] = pd.to_numeric(joined["review__mean_portfolio_return"], errors="coerce") - pd.to_numeric(joined["baseline_review_mean"], errors="coerce")
        lines.extend(
            [
                "",
                "Chosen-vs-baseline review summary:",
                f"- mean review cumulative advantage = `{format_float(joined['review_cum_advantage'].mean())}`",
                f"- mean review mean-return advantage = `{format_float(joined['review_mean_advantage'].mean())}`",
                f"- overlay beats baseline on review cumulative in `{int((joined['review_cum_advantage'] > 0).sum())}/{len(joined)}` folds",
            ]
        )
    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_CONFIG_RESULTS_PATH.name}]({OUTPUT_CONFIG_RESULTS_PATH})",
            f"- [{OUTPUT_CHOSEN_PATH.name}]({OUTPUT_CHOSEN_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    panel_df["rebalance_date"] = pd.to_datetime(panel_df["rebalance_date"])
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    asset_returns = load_asset_returns()

    config_rows: list[dict[str, object]] = []
    for fold in folds:
        master_df = build_master_frame(
            panel_df=panel_df,
            fold=fold,
            base_rows=base_rows,
            enhanced_rows=enhanced_rows,
            universe_rows=universe_rows,
            asset_returns=asset_returns,
        )
        if master_df.empty:
            continue
        config_rows.extend(build_config_rows(master_df, fold))

    chosen_rows = choose_best_configs(config_rows)
    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_csv(OUTPUT_CHOSEN_PATH, chosen_rows)
    write_summary(config_rows, chosen_rows)
    print(OUTPUT_CONFIG_RESULTS_PATH)
    print(OUTPUT_CHOSEN_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
