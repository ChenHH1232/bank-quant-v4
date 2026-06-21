from __future__ import annotations

import csv
from pathlib import Path
import warnings

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

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "fundamental_defensive_overlay_rolling_validation_v1_config_results.csv"
OUTPUT_CHOSEN_PATH = SCRIPT_DIR / "fundamental_defensive_overlay_rolling_validation_v1_chosen.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "fundamental_defensive_overlay_rolling_validation_v1.md"

TARGET_COMBO = "combo__ic_weight_train"
TARGET_TARGET_COL = "y_quarter_avg_daily_return_close"
BASELINE_CONFIG_KEY = "baseline__100pct_equity"

METRIC_SPECS = {
    "npl": {"column": "bank_indicator__Nonperforming_loan_rate", "higher_is_worse": True},
    "capital": {"column": "bank_indicator__capital_adequacy_ratio", "higher_is_worse": False},
    "coverage": {"column": "bank_indicator__non_performing_loan_provision_coverage", "higher_is_worse": False},
    "roe": {"column": "indicator__roe", "higher_is_worse": False},
    "profit_growth": {"column": "indicator__inc_net_profit_to_shareholders_annual", "higher_is_worse": False},
}

METRIC_COMBOS = {
    "all_5": ["npl", "capital", "coverage", "roe", "profit_growth"],
    "bank_core_3": ["npl", "capital", "coverage"],
    "bank_core_3_plus_roe_profit": ["npl", "capital", "coverage", "roe", "profit_growth"],
    "quality_2": ["npl", "coverage"],
    "earnings_2": ["roe", "profit_growth"],
}

WARNING_THRESHOLDS = [0.40, 0.45]
SEVERE_THRESHOLDS = [0.55, 0.60]
WARNING_EQUITY_WEIGHTS = [0.60, 0.80]
SEVERE_EQUITY_WEIGHTS = [0.20, 0.40]

ASSET_SPECS = {
    "cash": {
        "path": None,
        "return_col": None,
    },
    "treasury_etf_511010": {
        "path": MOMENTUM_DIR / "bond_defensive_panel_full_v1.csv",
        "return_col": "period_total_return",
    },
    "short_bond_etf_511260": {
        "path": MOMENTUM_DIR / "short_bond_defensive_panel_v1.csv",
        "return_col": "period_total_return",
    },
}


def make_config_key(
    metric_combo_name: str,
    warning_threshold: float,
    severe_threshold: float,
    warning_equity_weight: float,
    severe_equity_weight: float,
    asset_name: str,
) -> str:
    return (
        f"{metric_combo_name}"
        f"__wthr_{int(round(warning_threshold * 100))}"
        f"__sthr_{int(round(severe_threshold * 100))}"
        f"__weq_{int(round(warning_equity_weight * 100))}"
        f"__seq_{int(round(severe_equity_weight * 100))}"
        f"__asset_{asset_name}"
    )


def load_asset_returns() -> dict[str, pd.Series]:
    asset_returns: dict[str, pd.Series] = {}
    for asset_name, spec in ASSET_SPECS.items():
        if asset_name == "cash":
            asset_returns[asset_name] = pd.Series(dtype="float64")
            continue
        path = spec["path"]
        if path is None or not path.exists():
            asset_returns[asset_name] = pd.Series(dtype="float64")
            continue
        df = pd.read_csv(path, encoding="utf-8-sig")
        if "rebalance_date" not in df.columns or spec["return_col"] not in df.columns:
            asset_returns[asset_name] = pd.Series(dtype="float64")
            continue
        df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
        df[spec["return_col"]] = pd.to_numeric(df[spec["return_col"]], errors="coerce")
        asset_returns[asset_name] = (
            df.dropna(subset=["rebalance_date", spec["return_col"]])
            .drop_duplicates(subset=["rebalance_date"])
            .set_index("rebalance_date")[spec["return_col"]]
            .sort_index()
        )
    return asset_returns


def build_regime_metric_frame(panel_df: pd.DataFrame) -> pd.DataFrame:
    required_cols = ["rebalance_date", "code"] + [spec["column"] for spec in METRIC_SPECS.values()]
    work = panel_df[required_cols].copy()
    work["rebalance_date"] = pd.to_datetime(work["rebalance_date"])
    work = work.sort_values(["code", "rebalance_date"]).copy()

    for metric_name, spec in METRIC_SPECS.items():
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
        for metric_name in METRIC_SPECS:
            flag_col = f"flag__{metric_name}"
            valid = pd.to_numeric(group[flag_col], errors="coerce").dropna()
            row[f"ratio__{metric_name}"] = float(valid.mean()) if not valid.empty else np.nan
            row[f"coverage__{metric_name}"] = int(len(valid))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def build_equity_return_frame(
    panel_df: pd.DataFrame,
    scenario_rows: list[dict[str, str]],
    train_mask: pd.Series,
) -> pd.DataFrame:
    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, scenario_rows, train_mask)
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)

    rows: list[dict[str, object]] = []
    for rebalance_date, group in scored_df.groupby("rebalance_date", sort=True):
        group = group.dropna(subset=[TARGET_COMBO, TARGET_TARGET_COL]).copy()
        if len(group) < 5:
            continue
        group["bucket"] = assign_groups(group[TARGET_COMBO], 5)
        group = group.dropna(subset=["bucket"]).copy()
        top_group = group[group["bucket"] == 5].copy()
        if top_group.empty:
            continue
        rows.append(
            {
                "rebalance_date": pd.Timestamp(rebalance_date),
                "equity_return": float(pd.to_numeric(top_group[TARGET_TARGET_COL], errors="coerce").mean()),
                "selected_count": int(len(top_group)),
                "score_mean": float(pd.to_numeric(top_group[TARGET_COMBO], errors="coerce").mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def build_master_frame(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
    regime_metric_df: pd.DataFrame,
    asset_returns: dict[str, pd.Series],
) -> pd.DataFrame:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    window_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)

    selected_rows, _ = select_factor_rows(panel_df, universe_rows, fold)
    scenario_map = build_scenario_rows(selected_rows, base_rows, enhanced_rows)
    scenario_rows = scenario_map.get(SCENARIO_BASE, [])
    if not scenario_rows:
        return pd.DataFrame()

    equity_return_df = build_equity_return_frame(panel_df[window_mask].copy(), scenario_rows, train_mask)
    if equity_return_df.empty:
        return pd.DataFrame()

    master = equity_return_df.merge(regime_metric_df, on="rebalance_date", how="left")
    for asset_name, series in asset_returns.items():
        col = f"asset_return__{asset_name}"
        master[col] = master["rebalance_date"].map(series.to_dict()) if not series.empty else np.nan
        if asset_name == "cash":
            master[col] = 0.0
    master["window_label"] = np.where(
        master["rebalance_date"] < test_start,
        "train",
        np.where(master["rebalance_date"] < review_start, "test", "review"),
    )
    return master.sort_values("rebalance_date").reset_index(drop=True)


def classify_regime(signal_value: float, warning_threshold: float, severe_threshold: float) -> str:
    if pd.isna(signal_value):
        return "normal"
    if signal_value >= severe_threshold:
        return "severe"
    if signal_value >= warning_threshold:
        return "warning"
    return "normal"


def summarize_window(
    df: pd.DataFrame,
    asset_name: str,
    warning_threshold: float,
    severe_threshold: float,
    warning_equity_weight: float,
    severe_equity_weight: float,
    metric_names: list[str],
) -> dict[str, object]:
    work = df.copy()
    signal_cols = [f"ratio__{name}" for name in metric_names]
    work[signal_cols] = work[signal_cols].apply(pd.to_numeric, errors="coerce")
    work["signal_value"] = work[signal_cols].mean(axis=1)
    work["regime_name"] = work["signal_value"].apply(
        lambda value: classify_regime(value, warning_threshold, severe_threshold)
    )
    work["equity_weight"] = np.where(
        work["regime_name"] == "normal",
        1.0,
        np.where(work["regime_name"] == "warning", warning_equity_weight, severe_equity_weight),
    )
    work["defensive_weight"] = 1.0 - work["equity_weight"]

    asset_col = f"asset_return__{asset_name}"
    work["defensive_return"] = pd.to_numeric(work[asset_col], errors="coerce")
    coverage_mask = work["equity_return"].notna() & work["defensive_return"].notna()
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
            "warning_count": 0,
            "severe_count": 0,
            "normal_count": 0,
            "mean_signal_value": np.nan,
            "mean_equity_weight": np.nan,
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
        "warning_count": int((covered["regime_name"] == "warning").sum()),
        "severe_count": int((covered["regime_name"] == "severe").sum()),
        "normal_count": int((covered["regime_name"] == "normal").sum()),
        "mean_signal_value": float(pd.to_numeric(covered["signal_value"], errors="coerce").mean()),
        "mean_equity_weight": float(pd.to_numeric(covered["equity_weight"], errors="coerce").mean()),
    }


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


def build_config_rows(master_df: pd.DataFrame, fold: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    baseline_by_window = {}
    for window_label in ["train", "test", "review"]:
        baseline_by_window[window_label] = summarize_baseline_window(
            master_df[master_df["window_label"] == window_label].copy()
        )

    rows.append(
        {
            "fold_id": fold["fold_id"],
            "config_key": BASELINE_CONFIG_KEY,
            "metric_combo_name": "baseline",
            "metric_names": "",
            "warning_threshold": "",
            "severe_threshold": "",
            "warning_equity_weight": "",
            "severe_equity_weight": "",
            "asset_name": "cash",
            "full_review_asset_coverage": 1,
            "selection_status": "baseline",
            **flatten_window_metrics(baseline_by_window),
            "selection_score": np.nan,
        }
    )

    for metric_combo_name, metric_names in METRIC_COMBOS.items():
        for warning_threshold in WARNING_THRESHOLDS:
            for severe_threshold in SEVERE_THRESHOLDS:
                if severe_threshold <= warning_threshold:
                    continue
                for warning_equity_weight in WARNING_EQUITY_WEIGHTS:
                    for severe_equity_weight in SEVERE_EQUITY_WEIGHTS:
                        if severe_equity_weight > warning_equity_weight:
                            continue
                        for asset_name in ASSET_SPECS:
                            config_key = make_config_key(
                                metric_combo_name,
                                warning_threshold,
                                severe_threshold,
                                warning_equity_weight,
                                severe_equity_weight,
                                asset_name,
                            )
                            window_metrics = {}
                            full_review_asset_coverage = 1
                            for window_label in ["train", "test", "review"]:
                                summarized = summarize_window(
                                    master_df[master_df["window_label"] == window_label].copy(),
                                    asset_name=asset_name,
                                    warning_threshold=warning_threshold,
                                    severe_threshold=severe_threshold,
                                    warning_equity_weight=warning_equity_weight,
                                    severe_equity_weight=severe_equity_weight,
                                    metric_names=metric_names,
                                )
                                if window_label == "review" and summarized["coverage_ratio"] < 1.0:
                                    full_review_asset_coverage = 0
                                window_metrics[window_label] = summarized

                            rows.append(
                                {
                                    "fold_id": fold["fold_id"],
                                    "config_key": config_key,
                                    "metric_combo_name": metric_combo_name,
                                    "metric_names": "|".join(metric_names),
                                    "warning_threshold": warning_threshold,
                                    "severe_threshold": severe_threshold,
                                    "warning_equity_weight": warning_equity_weight,
                                    "severe_equity_weight": severe_equity_weight,
                                    "asset_name": asset_name,
                                    "full_review_asset_coverage": full_review_asset_coverage,
                                    "selection_status": "candidate",
                                    **flatten_window_metrics(window_metrics),
                                    "selection_score": compute_selection_score(window_metrics),
                                }
                            )
    return rows


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


def choose_best_configs(config_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    df = pd.DataFrame(config_rows)
    chosen_rows: list[dict[str, object]] = []
    for fold_id, fold_df in df.groupby("fold_id", sort=True):
        baseline_row = fold_df[fold_df["config_key"] == BASELINE_CONFIG_KEY].iloc[0].to_dict()
        candidate_df = fold_df[
            (fold_df["config_key"] != BASELINE_CONFIG_KEY)
            & (fold_df["asset_name"] == "cash")
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
    eligible_counts: dict[str, int] = {}

    warning_threshold_text = " / ".join(f"{int(round(v * 100))}%" for v in WARNING_THRESHOLDS)
    severe_threshold_text = " / ".join(f"{int(round(v * 100))}%" for v in SEVERE_THRESHOLDS)
    warning_weight_text = " / ".join(f"{int(round(v * 100))}%" for v in WARNING_EQUITY_WEIGHTS)
    severe_weight_text = " / ".join(f"{int(round(v * 100))}%" for v in SEVERE_EQUITY_WEIGHTS)

    lines = [
        "# Fundamental Defensive Overlay Rolling Validation V1",
        "",
        "Protocol:",
        "- base execution line = annual pure-fundamental `base_core_7 + combo__ic_weight_train`",
        "- factor selection remains the existing annual `5Y train + 2Y test + 1Y review` process",
        "- overlay is searched only after the base pure-fundamental factor set is frozen inside each fold",
        "- regime signal = cross-sectional deterioration breadth averaged across a chosen metric combination",
        "- deterioration metrics searched:",
        "- `npl`, `capital`, `coverage`, `roe`, `profit_growth`",
        f"- warning threshold grid = `{warning_threshold_text}`",
        f"- severe threshold grid = `{severe_threshold_text}`",
        f"- warning equity weight grid = `{warning_weight_text}`",
        f"- severe equity weight grid = `{severe_weight_text}`",
        "- defensive asset candidates wired into the framework = `cash`, `treasury_etf_511010`, `short_bond_etf_511260`",
        "",
        "Data reality check:",
    ]

    for asset_name in ASSET_SPECS:
        subset = config_df[config_df["asset_name"] == asset_name].copy()
        review_coverage = pd.to_numeric(subset["review__coverage_ratio"], errors="coerce")
        eligible_count = int((review_coverage >= 1.0).sum()) if not subset.empty else 0
        eligible_counts[asset_name] = eligible_count
        lines.append(
            f"- `{asset_name}` full-review-cover candidate rows: `{eligible_count}`"
        )

    lines.extend(
        [
            "",
            "Chosen fold results:",
        ]
    )

    for _, row in chosen_df.sort_values("fold_id").iterrows():
        lines.append(
            f"- `{row['fold_id']}` | status=`{row['selection_status']}` | config=`{row['config_key']}` | "
            f"asset=`{row['asset_name']}` | metric_combo=`{row['metric_combo_name']}` | "
            f"train_cum=`{format_float(row.get('train__cum_portfolio_return'))}` | "
            f"test_cum=`{format_float(row.get('test__cum_portfolio_return'))}` | "
            f"review_cum=`{format_float(row.get('review__cum_portfolio_return'))}` | "
            f"review_mean=`{format_float(row.get('review__mean_portfolio_return'))}`"
        )

    baseline_df = config_df[config_df["config_key"] == BASELINE_CONFIG_KEY].copy()
    if not baseline_df.empty and not chosen_df.empty:
        joined = chosen_df.merge(
            baseline_df[
                [
                    "fold_id",
                    "review__cum_portfolio_return",
                    "review__mean_portfolio_return",
                    "test__cum_portfolio_return",
                ]
            ].rename(
                columns={
                    "review__cum_portfolio_return": "baseline_review_cum",
                    "review__mean_portfolio_return": "baseline_review_mean",
                    "test__cum_portfolio_return": "baseline_test_cum",
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

    overlay_df = config_df[
        (config_df["config_key"] != BASELINE_CONFIG_KEY)
        & pd.to_numeric(config_df["review__coverage_ratio"], errors="coerce").ge(1.0)
    ].copy()
    asset_compare_line = "- asset comparison remains unavailable in this run"
    if not overlay_df.empty:
        asset_compare = (
            overlay_df.groupby("asset_name", dropna=False)["review__cum_portfolio_return"]
            .mean()
            .sort_values(ascending=False)
        )
        asset_compare_line = (
            "- average review cumulative return across full-cover overlay candidates ranks as "
            + " > ".join(
                f"`{asset_name}` ({format_float(value)})"
                for asset_name, value in asset_compare.items()
            )
        )

    if all(eligible_counts.get(asset_name, 0) > 0 for asset_name in ASSET_SPECS):
        asset_availability_line = "- the full annual review comparison is now available across `cash`, `treasury_etf_511010`, and `short_bond_etf_511260`"
    else:
        asset_availability_line = "- asset comparison is still partial because at least one defensive sleeve lacks full review coverage"

    lines.extend(
        [
            "",
            "Interpretation boundary:",
            "- this file validates the annual rolling search frame for trigger rule and equity-weight mapping",
            asset_availability_line,
            asset_compare_line,
            "- fold selection is still driven only by train/test information, so any review-period asset ranking here is diagnostic rather than an input to the chosen config",
            "",
            "Outputs:",
            f"- [{OUTPUT_CONFIG_RESULTS_PATH.name}]({OUTPUT_CONFIG_RESULTS_PATH})",
            f"- [{OUTPUT_CHOSEN_PATH.name}]({OUTPUT_CHOSEN_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    warnings.filterwarnings(
        "ignore",
        message="Boolean Series key will be reindexed to match DataFrame index.",
        category=UserWarning,
    )
    panel_df = load_panel()
    regime_metric_df = build_regime_metric_frame(panel_df)
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)
    asset_returns = load_asset_returns()

    config_rows: list[dict[str, object]] = []
    for fold in folds:
        master_df = build_master_frame(
            panel_df=panel_df,
            fold=fold,
            base_rows=base_rows,
            enhanced_rows=enhanced_rows,
            universe_rows=universe_rows,
            regime_metric_df=regime_metric_df,
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
