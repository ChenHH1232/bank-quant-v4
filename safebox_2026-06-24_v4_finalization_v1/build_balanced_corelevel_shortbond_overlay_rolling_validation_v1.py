from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    SCENARIO_BASE,
    add_combo_scores,
    build_scored_panel,
    build_scenario_rows,
    evaluate_factor_window,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
)
from build_base_core_6_robustness_validation_v1 import (
    REVIEW_YEAR_COUNT,
    build_yearly_folds_custom,
    format_float,
    load_daily_path,
    simulate_period_return,
)


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
MOMENTUM_DIR = ROOT_DIR / "phase_2_momentum"

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "balanced_corelevel_shortbond_overlay_rolling_validation_v1_config_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "balanced_corelevel_shortbond_overlay_rolling_validation_v1.md"

TRAIN_YEAR_COUNT = 5
TEST_YEAR_COUNT = 2
COMBO_NAME = "combo__ic_weight_train"
HOLD_COUNT = 8

RESIDENT_BASE_SET = [
    "indicator__roe",
    "indicator__eps",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]

METRIC_SPECS = {
    "npl": {"column": "bank_indicator__Nonperforming_loan_rate", "higher_is_worse": True},
    "capital": {"column": "bank_indicator__capital_adequacy_ratio", "higher_is_worse": False},
    "coverage": {"column": "bank_indicator__non_performing_loan_provision_coverage", "higher_is_worse": False},
}

WARNING_THRESHOLD = 0.40
SEVERE_THRESHOLD = 0.55
WARNING_EQUITY_WEIGHT = 0.60
SEVERE_EQUITY_WEIGHT = 0.40
DEFENSIVE_ASSET_NAME = "short_bond_etf_511260"
DEFENSIVE_ASSET_PATH = MOMENTUM_DIR / "short_bond_defensive_panel_v1.csv"
DEFENSIVE_ASSET_RETURN_COL = "period_total_return"


def build_variant_specs() -> list[dict[str, object]]:
    return [
        {
            "strategy_key": "balanced",
            "description": "base_core_6",
            "target_factor_names": RESIDENT_BASE_SET.copy(),
        },
        {
            "strategy_key": "core_level_shadow",
            "description": "base_core_6_replace_eps_with_core_level",
            "target_factor_names": [
                "indicator__roe",
                "bank_indicator__Nonperforming_loan_rate",
                "bank_indicator__non_performing_loan_provision_coverage",
                "bank_indicator__deposit_loan_ratio",
                "bank_indicator__capital_adequacy_ratio",
                "bank_indicator__core_level_capital_adequacy_ratio",
            ],
        },
    ]


def build_variant_base_rows(
    metadata_map: dict[str, dict[str, str]],
    target_factor_names: list[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for factor_name in target_factor_names:
        source_row = metadata_map[factor_name]
        row = source_row.copy()
        row["layer"] = "base_core"
        rows.append(row)
    return rows


def select_factor_rows_variant(
    panel_df: pd.DataFrame,
    variant_base_rows: list[dict[str, str]],
    fold: dict[str, object],
) -> list[dict[str, str]]:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])

    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)
    test_mask = (panel_df["rebalance_date"] >= test_start) & (panel_df["rebalance_date"] < review_start)

    selected_names: set[str] = set()
    for factor_row in variant_base_rows:
        evaluated = evaluate_factor_window(panel_df, factor_row, train_mask, test_mask)
        if int(evaluated["keep_flag"]) == 1:
            selected_names.add(str(evaluated["factor_name"]))

    return [row for row in variant_base_rows if row["factor_name"] in selected_names]


def build_equity_master_frame_for_variant(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    variant_base_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
    strategy_key: str,
) -> pd.DataFrame:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

    context_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

    selected_rows = select_factor_rows_variant(panel_df, variant_base_rows, fold)
    scenario_map = build_scenario_rows(selected_rows, variant_base_rows, [])
    factor_specs = scenario_map.get(SCENARIO_BASE, [])
    if not factor_specs:
        return pd.DataFrame()

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
        panel_df[context_mask].copy(),
        factor_specs,
        train_mask[context_mask],
    )
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty:
        return pd.DataFrame()

    scored_df["rebalance_date"] = pd.to_datetime(scored_df["rebalance_date"])
    all_dates = sorted(scored_df["rebalance_date"].drop_duplicates())
    date_to_next = {date_value: all_dates[idx + 1] for idx, date_value in enumerate(all_dates[:-1])}

    rows: list[dict[str, object]] = []
    for rebalance_date, group in scored_df.groupby("rebalance_date"):
        rebalance_date = pd.Timestamp(rebalance_date)
        next_rebalance_date = date_to_next.get(rebalance_date)
        if next_rebalance_date is None:
            continue
        group = group.dropna(subset=[COMBO_NAME]).copy()
        if group.empty:
            continue
        top_group = group.sort_values(COMBO_NAME, ascending=False).head(HOLD_COUNT).copy()
        top_codes = [str(code) for code in top_group["code"].astype(str).tolist()]
        period_return, metrics = simulate_period_return(
            top_codes=top_codes,
            rebalance_date=rebalance_date,
            next_rebalance_date=next_rebalance_date,
            daily_cache=daily_cache,
        )
        window_label = (
            "train" if rebalance_date < test_start else
            ("test" if rebalance_date < review_start else "review")
        )
        rows.append(
            {
                "fold_id": fold["fold_id"],
                "strategy_key": strategy_key,
                "rebalance_date": rebalance_date,
                "window_label": window_label,
                "equity_return": float(period_return),
                "avg_cash_weight": float(metrics["avg_cash_weight"]),
                "invested_stock_count": float(metrics["invested_stock_count"]),
                "selected_factor_count": int(len(factor_specs)),
            }
        )
    return pd.DataFrame(rows)


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
        ratios = []
        for metric_name in METRIC_SPECS:
            flag_col = f"flag__{metric_name}"
            valid = pd.to_numeric(group[flag_col], errors="coerce").dropna()
            ratio = float(valid.mean()) if not valid.empty else np.nan
            row[f"ratio__{metric_name}"] = ratio
            row[f"coverage__{metric_name}"] = int(len(valid))
            ratios.append(ratio)
        ratio_series = pd.Series(ratios, dtype="float64")
        row["signal_value"] = float(ratio_series.mean()) if ratio_series.notna().any() else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def classify_regime(signal_value: float) -> str:
    if pd.isna(signal_value):
        return "normal"
    if signal_value >= SEVERE_THRESHOLD:
        return "severe"
    if signal_value >= WARNING_THRESHOLD:
        return "warning"
    return "normal"


def apply_overlay(master_df: pd.DataFrame, asset_returns: pd.Series, regime_metric_df: pd.DataFrame) -> pd.DataFrame:
    if master_df.empty:
        return master_df
    out = master_df.merge(regime_metric_df, on="rebalance_date", how="left")
    out["defensive_return"] = out["rebalance_date"].map(asset_returns.to_dict()) if not asset_returns.empty else np.nan
    out["regime_name"] = out["signal_value"].apply(classify_regime)
    out["equity_weight"] = np.where(
        out["regime_name"] == "normal",
        1.0,
        np.where(out["regime_name"] == "warning", WARNING_EQUITY_WEIGHT, SEVERE_EQUITY_WEIGHT),
    )
    out["defensive_weight"] = 1.0 - out["equity_weight"]
    out["overlay_return"] = (
        pd.to_numeric(out["equity_return"], errors="coerce") * pd.to_numeric(out["equity_weight"], errors="coerce")
        + pd.to_numeric(out["defensive_return"], errors="coerce") * pd.to_numeric(out["defensive_weight"], errors="coerce")
    )
    return out


def summarize_return_series(series: pd.Series) -> dict[str, object]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {
            "snapshot_count": 0,
            "mean_return": np.nan,
            "cum_return": np.nan,
        }
    return {
        "snapshot_count": int(len(values)),
        "mean_return": float(values.mean()),
        "cum_return": float((1.0 + values).prod() - 1.0),
    }


def summarize_window_metrics(df: pd.DataFrame, return_col: str) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for window_label in ["train", "test", "review"]:
        window_df = df[df["window_label"] == window_label].copy()
        metrics = summarize_return_series(window_df[return_col])
        if not window_df.empty:
            metrics["mean_equity_weight"] = float(pd.to_numeric(window_df.get("equity_weight"), errors="coerce").mean()) if "equity_weight" in window_df else 1.0
            metrics["mean_defensive_weight"] = float(pd.to_numeric(window_df.get("defensive_weight"), errors="coerce").mean()) if "defensive_weight" in window_df else 0.0
            metrics["mean_signal_value"] = float(pd.to_numeric(window_df.get("signal_value"), errors="coerce").mean()) if "signal_value" in window_df else np.nan
        else:
            metrics["mean_equity_weight"] = np.nan
            metrics["mean_defensive_weight"] = np.nan
            metrics["mean_signal_value"] = np.nan
        out[window_label] = metrics
    return out


def flatten_window_metrics(window_metrics: dict[str, dict[str, object]]) -> dict[str, object]:
    flattened: dict[str, object] = {}
    for window_label, metrics in window_metrics.items():
        for key, value in metrics.items():
            flattened[f"{window_label}__{key}"] = value
    return flattened


def build_config_rows() -> list[dict[str, object]]:
    panel_df = load_panel()
    panel_df["rebalance_date"] = pd.to_datetime(panel_df["rebalance_date"])
    base_rows, enhanced_rows, universe_rows = load_factor_universe()
    metadata_map = {
        str(row["factor_name"]): dict(row)
        for row in (base_rows + enhanced_rows + universe_rows)
    }
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds_custom(
        may_dates=may_dates,
        train_year_count=TRAIN_YEAR_COUNT,
        test_year_count=TEST_YEAR_COUNT,
        review_year_count=REVIEW_YEAR_COUNT,
    )
    unique_codes = sorted({str(code) for code in panel_df["code"].astype(str).tolist()})
    daily_cache = {code: load_daily_path(code) for code in unique_codes}
    asset_returns = load_asset_returns()
    regime_metric_df = build_regime_metric_frame(panel_df)

    rows: list[dict[str, object]] = []
    for spec in build_variant_specs():
        variant_base_rows = build_variant_base_rows(metadata_map, list(spec["target_factor_names"]))
        for fold in folds:
            equity_master = build_equity_master_frame_for_variant(
                panel_df=panel_df,
                fold=fold,
                variant_base_rows=variant_base_rows,
                daily_cache=daily_cache,
                strategy_key=str(spec["strategy_key"]),
            )
            if equity_master.empty:
                continue
            overlay_master = apply_overlay(equity_master, asset_returns, regime_metric_df)
            pure_metrics = summarize_window_metrics(equity_master, "equity_return")
            overlay_metrics = summarize_window_metrics(overlay_master, "overlay_return")
            rows.append(
                {
                    "fold_id": fold["fold_id"],
                    "strategy_key": spec["strategy_key"],
                    "description": spec["description"],
                    "overlay_key": "pure_fundamental",
                    "warning_threshold": "",
                    "severe_threshold": "",
                    "warning_equity_weight": "",
                    "severe_equity_weight": "",
                    "defensive_asset": "",
                    **flatten_window_metrics(pure_metrics),
                }
            )
            rows.append(
                {
                    "fold_id": fold["fold_id"],
                    "strategy_key": spec["strategy_key"],
                    "description": spec["description"],
                    "overlay_key": "shortbond_6040_4055",
                    "warning_threshold": WARNING_THRESHOLD,
                    "severe_threshold": SEVERE_THRESHOLD,
                    "warning_equity_weight": WARNING_EQUITY_WEIGHT,
                    "severe_equity_weight": SEVERE_EQUITY_WEIGHT,
                    "defensive_asset": DEFENSIVE_ASSET_NAME,
                    **flatten_window_metrics(overlay_metrics),
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


def write_summary(config_rows: list[dict[str, object]]) -> None:
    config_df = pd.DataFrame(config_rows)
    if config_df.empty:
        OUTPUT_SUMMARY_PATH.write_text("# Balanced Core-Level Shortbond Overlay Rolling Validation V1\n\n- no rows\n", encoding="utf-8")
        return

    summary_df = (
        config_df.groupby(["strategy_key", "overlay_key", "description"], dropna=False)
        .agg(
            folds=("fold_id", "count"),
            mean_train_cum=("train__cum_return", "mean"),
            mean_test_cum=("test__cum_return", "mean"),
            mean_review_cum=("review__cum_return", "mean"),
            mean_train_signal=("train__mean_signal_value", "mean"),
            mean_test_signal=("test__mean_signal_value", "mean"),
            mean_review_signal=("review__mean_signal_value", "mean"),
            mean_train_equity_weight=("train__mean_equity_weight", "mean"),
            mean_test_equity_weight=("test__mean_equity_weight", "mean"),
            mean_review_equity_weight=("review__mean_equity_weight", "mean"),
        )
        .reset_index()
    )

    pure_df = summary_df[summary_df["overlay_key"] == "pure_fundamental"].copy()
    overlay_df = summary_df[summary_df["overlay_key"] == "shortbond_6040_4055"].copy()
    joined = pure_df.merge(
        overlay_df,
        on="strategy_key",
        suffixes=("__pure", "__overlay"),
    )
    joined["delta_train"] = pd.to_numeric(joined["mean_train_cum__overlay"], errors="coerce") - pd.to_numeric(joined["mean_train_cum__pure"], errors="coerce")
    joined["delta_test"] = pd.to_numeric(joined["mean_test_cum__overlay"], errors="coerce") - pd.to_numeric(joined["mean_test_cum__pure"], errors="coerce")
    joined["delta_review"] = pd.to_numeric(joined["mean_review_cum__overlay"], errors="coerce") - pd.to_numeric(joined["mean_review_cum__pure"], errors="coerce")

    lines = [
        "# Balanced Core-Level Shortbond Overlay Rolling Validation V1",
        "",
        "Protocol:",
        "- pure-fundamental base variants = `balanced` and `core_level_shadow`",
        "- annual shell fixed at `5y/2y/1y + combo__ic_weight_train + top_08`",
        "- defensive overlay fixed at `shortbond_6040_4055`",
        f"- warning threshold = `{int(round(WARNING_THRESHOLD * 100))}%`",
        f"- severe threshold = `{int(round(SEVERE_THRESHOLD * 100))}%`",
        f"- warning equity weight = `{int(round(WARNING_EQUITY_WEIGHT * 100))}%`",
        f"- severe equity weight = `{int(round(SEVERE_EQUITY_WEIGHT * 100))}%`",
        f"- defensive asset = `{DEFENSIVE_ASSET_NAME}`",
        "",
        "Variant summary:",
    ]

    for _, row in summary_df.sort_values(["strategy_key", "overlay_key"]).iterrows():
        lines.append(
            "- "
            f"`{row['strategy_key']}` `{row['overlay_key']}` | folds=`{int(row['folds'])}`"
            f" | mean_train_cum=`{format_float(row['mean_train_cum'])}`"
            f" | mean_test_cum=`{format_float(row['mean_test_cum'])}`"
            f" | mean_review_cum=`{format_float(row['mean_review_cum'])}`"
            f" | mean_review_equity_weight=`{format_float(row['mean_review_equity_weight'])}`"
            f" | mean_review_signal=`{format_float(row['mean_review_signal'])}`"
        )

    lines.extend([
        "",
        "Overlay delta versus pure branch:",
    ])
    for _, row in joined.sort_values("strategy_key").iterrows():
        lines.append(
            "- "
            f"`{row['strategy_key']}` | delta_train=`{format_float(row['delta_train'])}`"
            f" | delta_test=`{format_float(row['delta_test'])}`"
            f" | delta_review=`{format_float(row['delta_review'])}`"
            f" | pure_review=`{format_float(row['mean_review_cum__pure'])}`"
            f" | overlay_review=`{format_float(row['mean_review_cum__overlay'])}`"
        )

    if not joined.empty:
        best_review_row = joined.sort_values("mean_review_cum__overlay", ascending=False).iloc[0]
        lines.extend([
            "",
            "Best overlay branch by mean review cumulative return:",
            "- "
            f"`{best_review_row['strategy_key']}` `shortbond_6040_4055`"
            f" | overlay_review=`{format_float(best_review_row['mean_review_cum__overlay'])}`"
            f" | delta_review=`{format_float(best_review_row['delta_review'])}`",
        ])

    lines.extend([
        "",
        "Outputs:",
        f"- [balanced_corelevel_shortbond_overlay_rolling_validation_v1_config_results.csv]({OUTPUT_CONFIG_RESULTS_PATH})",
    ])
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    config_rows = build_config_rows()
    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_summary(config_rows)


if __name__ == "__main__":
    main()
