from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_BASE,
    add_combo_scores,
    apply_layer_caps,
    build_scenario_rows,
    build_scored_panel,
    build_yearly_folds,
    evaluate_factor_window,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
)
from build_pre2021_rolling_validation_v1 import assign_groups


SCRIPT_DIR = Path(__file__).resolve().parent

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "base_core_7_leave_one_out_rolling_validation_v1_config_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "base_core_7_leave_one_out_rolling_validation_v1.md"

TARGET_COMBO = "combo__ic_weight_train"
BASELINE_CONFIG_KEY = "baseline__base_core_7"
GROUP_COUNT = 5
HOLD_BUCKET = 5

BASE_CORE_FACTOR_NAMES = [
    "indicator__roe",
    "indicator__eps",
    "derived__log_total_assets",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]


def build_config_key(excluded_factor: str | None) -> str:
    if not excluded_factor:
        return BASELINE_CONFIG_KEY
    return f"loo__minus__{excluded_factor}"


def select_factor_rows_with_universe(
    panel_df: pd.DataFrame,
    universe_rows: list[dict[str, str]],
    fold: dict[str, object],
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])

    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)

    selection_rows: list[dict[str, object]] = []
    for factor_row in universe_rows:
        evaluated = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
        selection_rows.append(evaluated | {"fold_id": fold["fold_id"]})
    return apply_layer_caps(selection_rows, universe_rows)


def build_master_rows_for_variant(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
    excluded_factor: str | None,
) -> list[dict[str, object]]:
    filtered_base_rows = [row for row in base_rows if row["factor_name"] != excluded_factor]
    filtered_enhanced_rows = [row for row in enhanced_rows if row["factor_name"] != excluded_factor]
    filtered_universe_rows = [row for row in universe_rows if row["factor_name"] != excluded_factor]

    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

    context_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

    selected_rows, _ = select_factor_rows_with_universe(panel_df, filtered_universe_rows, fold)
    scenario_map = build_scenario_rows(selected_rows, filtered_base_rows, filtered_enhanced_rows)
    factor_specs = scenario_map.get(SCENARIO_BASE, [])
    if not factor_specs:
        return []

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
        panel_df[context_mask].copy(),
        factor_specs,
        train_mask[context_mask],
    )
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty:
        return []

    rows: list[dict[str, object]] = []
    scored_df["rebalance_date"] = pd.to_datetime(scored_df["rebalance_date"])

    for rebalance_date, group in scored_df.groupby("rebalance_date"):
        group = group.dropna(subset=[TARGET_COMBO, "y_quarter_avg_daily_return_close"]).copy()
        if len(group) < GROUP_COUNT:
            continue
        group["bucket"] = assign_groups(group[TARGET_COMBO], GROUP_COUNT)
        group = group.dropna(subset=["bucket"]).copy()
        if group.empty:
            continue
        top_group = group[group["bucket"] == HOLD_BUCKET].copy()
        if top_group.empty:
            continue

        rebalance_date = pd.Timestamp(rebalance_date)
        window_label = (
            "train" if rebalance_date < test_start else
            ("test" if rebalance_date < review_start else "review")
        )
        rows.append(
            {
                "fold_id": fold["fold_id"],
                "config_key": build_config_key(excluded_factor),
                "excluded_factor": excluded_factor or "",
                "rebalance_date": rebalance_date,
                "window_label": window_label,
                "selected_factor_count": int(len(factor_specs)),
                "top_bucket_count": int(len(top_group)),
                "top_bucket_return": float(top_group["y_quarter_avg_daily_return_close"].mean()),
            }
        )
    return rows


def summarize_window_returns(returns: pd.Series) -> dict[str, object]:
    series = pd.to_numeric(returns, errors="coerce").dropna()
    if series.empty:
        return {
            "snapshot_count": int(len(returns)),
            "covered_snapshot_count": 0,
            "coverage_ratio": 0.0,
            "mean_period_return": np.nan,
            "cum_portfolio_return": np.nan,
        }
    return {
        "snapshot_count": int(len(returns)),
        "covered_snapshot_count": int(len(series)),
        "coverage_ratio": float(len(series) / len(returns)) if len(returns) > 0 else 0.0,
        "mean_period_return": float(series.mean()),
        "cum_portfolio_return": float((1.0 + series).prod() - 1.0),
    }


def flatten_window_metrics(window_metrics: dict[str, dict[str, object]]) -> dict[str, object]:
    flattened: dict[str, object] = {}
    for window_label, metrics in window_metrics.items():
        for key, value in metrics.items():
            flattened[f"{window_label}__{key}"] = value
    return flattened


def build_config_rows(detail_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not detail_rows:
        return []
    detail_df = pd.DataFrame(detail_rows)
    rows: list[dict[str, object]] = []
    for (fold_id, config_key, excluded_factor), group in detail_df.groupby(["fold_id", "config_key", "excluded_factor"], sort=True):
        window_metrics = {
            label: summarize_window_returns(group.loc[group["window_label"] == label, "top_bucket_return"])
            for label in ["train", "test", "review"]
        }
        rows.append(
            {
                "fold_id": fold_id,
                "config_key": config_key,
                "excluded_factor": excluded_factor,
                **flatten_window_metrics(window_metrics),
                "mean_selected_factor_count": float(pd.to_numeric(group["selected_factor_count"], errors="coerce").mean()),
                "mean_top_bucket_count": float(pd.to_numeric(group["top_bucket_count"], errors="coerce").mean()),
            }
        )
    return rows


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


def write_summary(config_rows: list[dict[str, object]]) -> None:
    config_df = pd.DataFrame(config_rows)
    if config_df.empty:
        OUTPUT_SUMMARY_PATH.write_text("# Base Core 7 Leave-One-Out Rolling Validation V1\n\n- no rows\n", encoding="utf-8")
        return

    baseline_df = config_df[config_df["config_key"] == BASELINE_CONFIG_KEY].copy()
    baseline_train_mean = float(pd.to_numeric(baseline_df["train__cum_portfolio_return"], errors="coerce").mean())
    baseline_test_mean = float(pd.to_numeric(baseline_df["test__cum_portfolio_return"], errors="coerce").mean())
    baseline_review_mean = float(pd.to_numeric(baseline_df["review__cum_portfolio_return"], errors="coerce").mean())

    variant_df = config_df[config_df["config_key"] != BASELINE_CONFIG_KEY].copy()
    summary_df = (
        variant_df.groupby(["config_key", "excluded_factor"], dropna=False)
        .agg(
            folds=("fold_id", "count"),
            mean_train_cum=("train__cum_portfolio_return", "mean"),
            mean_test_cum=("test__cum_portfolio_return", "mean"),
            mean_review_cum=("review__cum_portfolio_return", "mean"),
            mean_selected_factor_count=("mean_selected_factor_count", "mean"),
        )
        .reset_index()
    )
    summary_df["delta_train_vs_baseline"] = summary_df["mean_train_cum"] - baseline_train_mean
    summary_df["delta_test_vs_baseline"] = summary_df["mean_test_cum"] - baseline_test_mean
    summary_df["delta_review_vs_baseline"] = summary_df["mean_review_cum"] - baseline_review_mean
    summary_df = summary_df.sort_values(
        ["delta_test_vs_baseline", "delta_review_vs_baseline", "delta_train_vs_baseline"],
        ascending=[False, False, False],
    )

    lines = [
        "# Base Core 7 Leave-One-Out Rolling Validation V1",
        "",
        "Protocol:",
        "- baseline factor shell = annual pure-fundamental `base_core_7 + combo__ic_weight_train`",
        "- each leave-one-out variant removes exactly one resident `base_core` factor from the executable universe",
        "- annual factor-refresh rules, layer caps, and combo scoring stay unchanged",
        "- strategy readout uses the same top-bucket return logic on each rebalance snapshot",
        "",
        "Resident factor set tested:",
    ]
    for factor_name in BASE_CORE_FACTOR_NAMES:
        lines.append(f"- `{factor_name}`")

    lines.extend(
        [
            "",
            "Baseline means:",
            f"- mean_train_cum=`{format_float(baseline_train_mean)}`",
            f"- mean_test_cum=`{format_float(baseline_test_mean)}`",
            f"- mean_review_cum=`{format_float(baseline_review_mean)}`",
            "",
            "Leave-one-out ranking:",
        ]
    )

    for _, row in summary_df.iterrows():
        lines.append(
            f"- remove `{row['excluded_factor']}` | folds=`{int(row['folds'])}` | "
            f"mean_train_cum=`{format_float(row['mean_train_cum'])}` | "
            f"mean_test_cum=`{format_float(row['mean_test_cum'])}` | "
            f"mean_review_cum=`{format_float(row['mean_review_cum'])}` | "
            f"delta_test=`{format_float(row['delta_test_vs_baseline'])}` | "
            f"delta_review=`{format_float(row['delta_review_vs_baseline'])}` | "
            f"mean_selected_factor_count=`{format_float(row['mean_selected_factor_count'])}`"
        )

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_CONFIG_RESULTS_PATH.name}]({OUTPUT_CONFIG_RESULTS_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = load_panel()
    panel_df["rebalance_date"] = pd.to_datetime(panel_df["rebalance_date"])
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds(may_dates)

    detail_rows: list[dict[str, object]] = []
    variant_factors: list[str | None] = [None] + BASE_CORE_FACTOR_NAMES
    for excluded_factor in variant_factors:
        for fold in folds:
            detail_rows.extend(
                build_master_rows_for_variant(
                    panel_df=panel_df,
                    fold=fold,
                    base_rows=base_rows,
                    enhanced_rows=enhanced_rows,
                    universe_rows=universe_rows,
                    excluded_factor=excluded_factor,
                )
            )

    config_rows = build_config_rows(detail_rows)
    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_summary(config_rows)
    print(OUTPUT_CONFIG_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
