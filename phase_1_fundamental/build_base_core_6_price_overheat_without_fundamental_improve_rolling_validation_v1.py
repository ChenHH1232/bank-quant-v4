from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_annual_factor_refresh_5y2y1y_v1 import (
    add_combo_scores,
    build_scored_panel,
    evaluate_factor_window,
    get_may_rebalance_dates,
    load_factor_universe,
    load_panel,
)
from build_phase1_training_panel import load_price_history
from build_pre2021_rolling_validation_v1 import assign_groups


SCRIPT_DIR = Path(__file__).resolve().parent

OUTPUT_CONFIG_RESULTS_PATH = SCRIPT_DIR / "base_core_6_price_overheat_without_fundamental_improve_rolling_validation_v1_config_results.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "base_core_6_price_overheat_without_fundamental_improve_rolling_validation_v1.md"

EXCLUDED_FACTOR = "derived__log_total_assets"
TARGET_BASE_SET = [
    "indicator__roe",
    "indicator__eps",
    "bank_indicator__Nonperforming_loan_rate",
    "bank_indicator__non_performing_loan_provision_coverage",
    "bank_indicator__deposit_loan_ratio",
    "bank_indicator__capital_adequacy_ratio",
]

TARGET_COMBO = "combo__ic_weight_train"
GROUP_COUNT = 5
HOLD_BUCKET = 5
TRAIN_YEAR_COUNT = 5
TEST_YEAR_COUNT = 2
REVIEW_YEAR_COUNT = 1

BASELINE_CONFIG_KEY = "base_core_6__top_bucket_equal_weight"
OVERHEAT_GROWTH_TRIGGERS = [0.15, 0.20]
OVERHEAT_CAP_WEIGHTS = [0.15, 0.10]
IMPROVEMENT_COUNT_THRESHOLDS = [1, 2]
MIN_AVAILABLE_IMPROVEMENT_SIGNALS = 3

IMPROVEMENT_RULES = [
    ("indicator__roe", "higher"),
    ("indicator__eps", "higher"),
    ("bank_indicator__Nonperforming_loan_rate", "lower"),
    ("bank_indicator__non_performing_loan_provision_coverage", "higher"),
    ("bank_indicator__deposit_loan_ratio", "lower"),
    ("bank_indicator__capital_adequacy_ratio", "higher"),
]


def filter_factor_universe(
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    filtered_base_rows = [row for row in base_rows if row["factor_name"] in TARGET_BASE_SET]
    filtered_enhanced_rows = [
        row for row in enhanced_rows
        if row["factor_name"] in TARGET_BASE_SET or row["factor_name"] != EXCLUDED_FACTOR
    ]
    filtered_universe_rows = [row for row in universe_rows if row["factor_name"] != EXCLUDED_FACTOR]
    return filtered_base_rows, filtered_enhanced_rows, filtered_universe_rows


def apply_fixed_base_selection(
    selection_rows: list[dict[str, object]],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    metadata_map = {row["factor_name"]: row for row in base_rows + enhanced_rows}
    selected_names = {
        row["factor_name"]
        for row in selection_rows
        if row["factor_name"] in TARGET_BASE_SET and int(row["keep_flag"]) == 1
    }

    adjusted_rows: list[dict[str, object]] = []
    for row in selection_rows:
        row_copy = row.copy()
        factor_name = str(row_copy["factor_name"])
        if factor_name in TARGET_BASE_SET and int(row_copy["keep_flag"]) == 1 and factor_name in selected_names:
            row_copy["keep_reason"] = f"{row_copy['keep_reason']}|kept_in_base_core_6"
        elif factor_name in TARGET_BASE_SET and int(row_copy["keep_flag"]) == 1:
            row_copy["keep_flag"] = 0
            row_copy["keep_reason"] = f"{row_copy['keep_reason']}|dropped_from_base_core_6"
        adjusted_rows.append(row_copy)

    selected_rows = [metadata_map[name] for name in TARGET_BASE_SET if name in selected_names]
    return selected_rows, adjusted_rows


def select_factor_rows_base6(
    panel_df: pd.DataFrame,
    universe_rows: list[dict[str, str]],
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
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
    return apply_fixed_base_selection(selection_rows, base_rows, enhanced_rows)


def build_yearly_folds_custom(may_dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    folds: list[dict[str, object]] = []
    required_span = TRAIN_YEAR_COUNT + TEST_YEAR_COUNT + REVIEW_YEAR_COUNT
    for start_idx in range(0, len(may_dates) - required_span + 1):
        train_dates = may_dates[start_idx : start_idx + TRAIN_YEAR_COUNT]
        test_dates = may_dates[start_idx + TRAIN_YEAR_COUNT : start_idx + TRAIN_YEAR_COUNT + TEST_YEAR_COUNT]
        review_dates = may_dates[
            start_idx + TRAIN_YEAR_COUNT + TEST_YEAR_COUNT : start_idx + required_span
        ]
        if (
            len(train_dates) < TRAIN_YEAR_COUNT
            or len(test_dates) < TEST_YEAR_COUNT
            or len(review_dates) < REVIEW_YEAR_COUNT
        ):
            continue
        folds.append(
            {
                "fold_id": f"annual_{len(folds) + 1:02d}",
                "train_start": train_dates[0].strftime("%Y-%m-%d"),
                "train_end": (test_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "test_start": test_dates[0].strftime("%Y-%m-%d"),
                "test_end": (review_dates[0] - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                "review_start": review_dates[0].strftime("%Y-%m-%d"),
                "review_end": (
                    review_dates[0] + pd.DateOffset(years=REVIEW_YEAR_COUNT) - pd.Timedelta(days=1)
                ).strftime("%Y-%m-%d"),
            }
        )
    return folds


def load_daily_path(code: str) -> pd.DataFrame:
    price_df = load_price_history(code).copy()
    if price_df.empty:
        return pd.DataFrame(columns=["day", "close", "daily_return"])
    price_df["day"] = pd.to_datetime(price_df["day"]).dt.date
    price_df["close"] = pd.to_numeric(price_df["close"], errors="coerce")
    price_df = (
        price_df.dropna(subset=["day", "close"])
        .sort_values("day")
        .drop_duplicates(subset=["day"], keep="last")
        .reset_index(drop=True)
    )
    if price_df.empty:
        return pd.DataFrame(columns=["day", "close", "daily_return"])
    price_df["daily_return"] = price_df["close"].pct_change()
    return price_df[["day", "close", "daily_return"]].copy()


def get_aligned_row(df: pd.DataFrame, target_date: pd.Timestamp | str, mode: str) -> pd.Series | None:
    if df.empty:
        return None
    target_day = pd.Timestamp(target_date).date()
    if mode == "anchor":
        eligible = df[df["day"] >= target_day].copy()
    else:
        eligible = df[df["day"] <= target_day].copy()
    if eligible.empty:
        return None
    eligible = eligible.sort_values("day")
    return eligible.iloc[0] if mode == "anchor" else eligible.iloc[-1]


def build_strategy_key(config: dict[str, float]) -> str:
    return "price_hot_no_fund_improve__trigger_%02d__cap_%03d__maximp_%d" % (
        int(round(config["trigger_growth"] * 100)),
        int(round(config["cap_weight"] * 100)),
        int(round(config["max_improve_count"])),
    )


def add_fundamental_improvement_flags(scored_df: pd.DataFrame) -> pd.DataFrame:
    required_cols = ["code", "rebalance_date"] + [name for name, _ in IMPROVEMENT_RULES]
    available_df = scored_df[required_cols].copy()
    available_df = available_df.sort_values(["code", "rebalance_date"]).copy()

    for factor_name, _direction in IMPROVEMENT_RULES:
        available_df[f"prev__{factor_name}"] = available_df.groupby("code")[factor_name].shift(1)

    improve_count_list: list[float] = []
    available_count_list: list[float] = []
    no_sync_list: list[int] = []

    for _, row in available_df.iterrows():
        improve_count = 0
        available_count = 0
        for factor_name, direction in IMPROVEMENT_RULES:
            current_value = pd.to_numeric(pd.Series([row.get(factor_name)]), errors="coerce").iloc[0]
            prev_value = pd.to_numeric(pd.Series([row.get(f"prev__{factor_name}")]), errors="coerce").iloc[0]
            if pd.isna(current_value) or pd.isna(prev_value):
                continue
            delta = float(current_value) - float(prev_value)
            available_count += 1
            if direction == "higher" and delta > 0:
                improve_count += 1
            elif direction == "lower" and delta < 0:
                improve_count += 1
        improve_count_list.append(float(improve_count))
        available_count_list.append(float(available_count))
        no_sync_list.append(0)

    available_df["fund_improve_count"] = improve_count_list
    available_df["fund_improve_available_count"] = available_count_list
    return scored_df.merge(
        available_df[["code", "rebalance_date", "fund_improve_count", "fund_improve_available_count"]],
        on=["code", "rebalance_date"],
        how="left",
    )


def simulate_period_return(
    selected_specs: list[dict[str, object]],
    rebalance_date: pd.Timestamp,
    next_rebalance_date: pd.Timestamp,
    config: dict[str, float] | None,
    daily_cache: dict[str, pd.DataFrame],
) -> tuple[float, dict[str, float]]:
    if not selected_specs:
        return np.nan, {
            "avg_cash_weight": np.nan,
            "trimmed_stock_count": 0,
            "trim_event_count": 0,
            "weight_sum": np.nan,
        }

    top_codes = [str(item["code"]) for item in selected_specs]
    base_weight = 1.0 / float(len(top_codes))
    working_weights = {code: base_weight for code in top_codes}
    anchor_prices: dict[str, float] = {}
    overheat_eligible_map = {str(item["code"]): int(item["overheat_eligible_flag"]) for item in selected_specs}
    trimmed_flags: dict[str, int] = {code: 0 for code in top_codes}
    trim_event_count = 0

    all_days: set[object] = set()
    stock_windows: dict[str, dict[object, tuple[float, float]]] = {}
    for code in top_codes:
        stock_df = daily_cache.get(code, pd.DataFrame()).copy()
        if stock_df.empty:
            continue
        anchor_row = get_aligned_row(stock_df, rebalance_date, "anchor")
        end_row = get_aligned_row(stock_df, next_rebalance_date, "end")
        if anchor_row is None or end_row is None:
            continue
        anchor_day = anchor_row["day"]
        end_day = end_row["day"]
        window = stock_df[(stock_df["day"] > anchor_day) & (stock_df["day"] <= end_day)].copy()
        if window.empty:
            continue
        anchor_prices[code] = float(anchor_row["close"])
        stock_windows[code] = {
            row["day"]: (
                float(row["daily_return"]) if pd.notna(row["daily_return"]) else np.nan,
                float(row["close"]) if pd.notna(row["close"]) else np.nan,
            )
            for _, row in window.iterrows()
        }
        all_days.update(stock_windows[code].keys())

    if not stock_windows:
        return np.nan, {
            "avg_cash_weight": np.nan,
            "trimmed_stock_count": 0,
            "trim_event_count": 0,
            "weight_sum": np.nan,
        }

    ordered_days = sorted(all_days)
    period_returns: list[float] = []
    cash_weights: list[float] = []

    for day in ordered_days:
        portfolio_return = 0.0
        active_weight_sum = 0.0
        for code, day_map in stock_windows.items():
            payload = day_map.get(day)
            if payload is None:
                continue
            daily_return, _ = payload
            weight = float(working_weights.get(code, 0.0))
            if pd.notna(daily_return) and weight > 0:
                portfolio_return += weight * float(daily_return)
            active_weight_sum += weight
        cash_weights.append(max(0.0, 1.0 - active_weight_sum))
        period_returns.append(portfolio_return)

        if config is None:
            continue

        trigger_growth = float(config["trigger_growth"])
        cap_weight = float(config["cap_weight"])
        for code, day_map in stock_windows.items():
            if int(overheat_eligible_map.get(code, 0)) != 1:
                continue
            payload = day_map.get(day)
            if payload is None:
                continue
            _, current_price = payload
            anchor_price = anchor_prices.get(code)
            if anchor_price is None or pd.isna(current_price) or anchor_price <= 0:
                continue
            growth = float(current_price) / float(anchor_price) - 1.0
            if growth < trigger_growth:
                continue
            old_weight = float(working_weights.get(code, base_weight))
            new_weight = min(old_weight, cap_weight)
            if new_weight < old_weight - 1e-12:
                working_weights[code] = new_weight
                trimmed_flags[code] = 1
                trim_event_count += 1

    if not period_returns:
        return np.nan, {
            "avg_cash_weight": np.nan,
            "trimmed_stock_count": 0,
            "trim_event_count": 0,
            "weight_sum": np.nan,
        }

    total_return = float(np.prod([1.0 + x for x in period_returns]) - 1.0)
    metrics = {
        "avg_cash_weight": float(np.mean(cash_weights)) if cash_weights else 0.0,
        "trimmed_stock_count": int(sum(trimmed_flags.values())),
        "trim_event_count": int(trim_event_count),
        "weight_sum": float(sum(float(working_weights.get(code, 0.0)) for code in stock_windows)),
    }
    return total_return, metrics


def build_master_frame(
    panel_df: pd.DataFrame,
    fold: dict[str, object],
    base_rows: list[dict[str, str]],
    enhanced_rows: list[dict[str, str]],
    universe_rows: list[dict[str, str]],
    daily_cache: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    train_start = pd.Timestamp(fold["train_start"])
    test_start = pd.Timestamp(fold["test_start"])
    review_start = pd.Timestamp(fold["review_start"])
    review_end = pd.Timestamp(fold["review_end"]) + pd.Timedelta(days=1)

    context_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < review_end)
    train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < test_start)

    selected_rows, _ = select_factor_rows_base6(
        panel_df=panel_df,
        universe_rows=universe_rows,
        fold=fold,
        base_rows=base_rows,
        enhanced_rows=enhanced_rows,
    )
    factor_specs = [row for row in base_rows if row["factor_name"] in {spec["factor_name"] for spec in selected_rows}]
    if not factor_specs:
        return pd.DataFrame()

    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(
        panel_df[context_mask].copy(),
        factor_specs,
        train_mask[context_mask],
    )
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    if scored_df.empty or TARGET_COMBO not in scored_df.columns:
        return pd.DataFrame()

    scored_df["rebalance_date"] = pd.to_datetime(scored_df["rebalance_date"])
    scored_df = add_fundamental_improvement_flags(scored_df)
    rebalance_dates = sorted(pd.to_datetime(scored_df["rebalance_date"].drop_duplicates()))

    rows: list[dict[str, object]] = []
    for idx, rebalance_date in enumerate(rebalance_dates):
        if rebalance_date < train_start or rebalance_date >= review_end or idx + 1 >= len(rebalance_dates):
            continue
        next_rebalance_date = rebalance_dates[idx + 1]
        if next_rebalance_date > review_end:
            next_rebalance_date = review_end - pd.Timedelta(days=1)

        group = scored_df[scored_df["rebalance_date"] == rebalance_date].copy()
        group = group.dropna(subset=[TARGET_COMBO]).sort_values([TARGET_COMBO, "code"], ascending=[False, True]).copy()
        if len(group) < GROUP_COUNT:
            continue
        group["bucket"] = assign_groups(group[TARGET_COMBO], GROUP_COUNT)
        group = group.dropna(subset=["bucket"]).copy()
        if group.empty:
            continue
        group["bucket"] = group["bucket"].astype(int)
        long_df = group[group["bucket"] == HOLD_BUCKET].copy()
        if long_df.empty:
            continue

        row = {
            "rebalance_date": pd.Timestamp(rebalance_date),
            "next_rebalance_date": pd.Timestamp(next_rebalance_date),
            "window_label": (
                "train" if rebalance_date < test_start else ("test" if rebalance_date < review_start else "review")
            ),
            "selected_count": int(len(long_df)),
            "selected_codes": "|".join(long_df["code"].astype(str).tolist()),
        }

        baseline_specs = [
            {"code": str(item["code"]), "overheat_eligible_flag": 0}
            for _, item in long_df.iterrows()
        ]
        baseline_return, baseline_metrics = simulate_period_return(
            selected_specs=baseline_specs,
            rebalance_date=rebalance_date,
            next_rebalance_date=next_rebalance_date,
            config=None,
            daily_cache=daily_cache,
        )
        if pd.isna(baseline_return):
            continue

        row[f"return__{BASELINE_CONFIG_KEY}"] = baseline_return
        row[f"avg_cash_weight__{BASELINE_CONFIG_KEY}"] = baseline_metrics["avg_cash_weight"]
        row[f"trimmed_stock_count__{BASELINE_CONFIG_KEY}"] = baseline_metrics["trimmed_stock_count"]
        row[f"trim_event_count__{BASELINE_CONFIG_KEY}"] = baseline_metrics["trim_event_count"]
        row[f"weight_sum__{BASELINE_CONFIG_KEY}"] = baseline_metrics["weight_sum"]

        for max_improve_count in IMPROVEMENT_COUNT_THRESHOLDS:
            eligible_df = long_df.copy()
            eligible_df["overheat_eligible_flag"] = (
                (pd.to_numeric(eligible_df["fund_improve_available_count"], errors="coerce") >= MIN_AVAILABLE_IMPROVEMENT_SIGNALS)
                & (pd.to_numeric(eligible_df["fund_improve_count"], errors="coerce") <= float(max_improve_count))
            ).astype(int)
            eligible_specs = [
                {"code": str(item["code"]), "overheat_eligible_flag": int(item["overheat_eligible_flag"])}
                for _, item in eligible_df.iterrows()
            ]
            row[f"eligible_count__maximp_{max_improve_count}"] = int(eligible_df["overheat_eligible_flag"].sum())

            for trigger_growth in OVERHEAT_GROWTH_TRIGGERS:
                for cap_weight in OVERHEAT_CAP_WEIGHTS:
                    config = {
                        "trigger_growth": trigger_growth,
                        "cap_weight": cap_weight,
                        "max_improve_count": max_improve_count,
                    }
                    strategy_key = build_strategy_key(config)
                    period_return, metrics = simulate_period_return(
                        selected_specs=eligible_specs,
                        rebalance_date=rebalance_date,
                        next_rebalance_date=next_rebalance_date,
                        config=config,
                        daily_cache=daily_cache,
                    )
                    row[f"return__{strategy_key}"] = period_return
                    row[f"avg_cash_weight__{strategy_key}"] = metrics["avg_cash_weight"]
                    row[f"trimmed_stock_count__{strategy_key}"] = metrics["trimmed_stock_count"]
                    row[f"trim_event_count__{strategy_key}"] = metrics["trim_event_count"]
                    row[f"weight_sum__{strategy_key}"] = metrics["weight_sum"]
        rows.append(row)

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


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


def build_config_rows(master_df: pd.DataFrame, fold: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    candidate_configs = [BASELINE_CONFIG_KEY]
    for max_improve_count in IMPROVEMENT_COUNT_THRESHOLDS:
        for trigger_growth in OVERHEAT_GROWTH_TRIGGERS:
            for cap_weight in OVERHEAT_CAP_WEIGHTS:
                candidate_configs.append(
                    build_strategy_key(
                        {
                            "trigger_growth": trigger_growth,
                            "cap_weight": cap_weight,
                            "max_improve_count": max_improve_count,
                        }
                    )
                )

    for config_key in candidate_configs:
        window_metrics = {
            label: summarize_window_returns(master_df.loc[master_df["window_label"] == label, f"return__{config_key}"])
            for label in ["train", "test", "review"]
        }
        rows.append(
            {
                "fold_id": fold["fold_id"],
                "config_key": config_key,
                **flatten_window_metrics(window_metrics),
                "review__mean_avg_cash_weight": float(
                    pd.to_numeric(
                        master_df.loc[master_df["window_label"] == "review", f"avg_cash_weight__{config_key}"],
                        errors="coerce",
                    ).mean()
                ),
                "review__mean_trimmed_stock_count": float(
                    pd.to_numeric(
                        master_df.loc[master_df["window_label"] == "review", f"trimmed_stock_count__{config_key}"],
                        errors="coerce",
                    ).mean()
                ),
                "review__mean_trim_event_count": float(
                    pd.to_numeric(
                        master_df.loc[master_df["window_label"] == "review", f"trim_event_count__{config_key}"],
                        errors="coerce",
                    ).mean()
                ),
                "review__mean_weight_sum": float(
                    pd.to_numeric(
                        master_df.loc[master_df["window_label"] == "review", f"weight_sum__{config_key}"],
                        errors="coerce",
                    ).mean()
                ),
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
        OUTPUT_SUMMARY_PATH.write_text("# Base Core 6 Price Overheat Without Fundamental Improve Rolling Validation V1\n\n- no rows\n", encoding="utf-8")
        return

    baseline_df = config_df[config_df["config_key"] == BASELINE_CONFIG_KEY].copy()
    baseline_train_mean = float(pd.to_numeric(baseline_df["train__cum_portfolio_return"], errors="coerce").mean())
    baseline_test_mean = float(pd.to_numeric(baseline_df["test__cum_portfolio_return"], errors="coerce").mean())
    baseline_review_mean = float(pd.to_numeric(baseline_df["review__cum_portfolio_return"], errors="coerce").mean())

    candidate_df = config_df[config_df["config_key"] != BASELINE_CONFIG_KEY].copy()
    summary_df = (
        candidate_df.groupby(["config_key"], dropna=False)
        .agg(
            folds=("fold_id", "count"),
            mean_train_cum=("train__cum_portfolio_return", "mean"),
            mean_test_cum=("test__cum_portfolio_return", "mean"),
            mean_review_cum=("review__cum_portfolio_return", "mean"),
            mean_review_cash=("review__mean_avg_cash_weight", "mean"),
            mean_review_trim_events=("review__mean_trim_event_count", "mean"),
            mean_review_weight_sum=("review__mean_weight_sum", "mean"),
        )
        .reset_index()
    )
    summary_df["delta_test_vs_baseline"] = summary_df["mean_test_cum"] - baseline_test_mean
    summary_df["delta_review_vs_baseline"] = summary_df["mean_review_cum"] - baseline_review_mean
    summary_df = summary_df.sort_values(
        ["delta_test_vs_baseline", "delta_review_vs_baseline", "mean_train_cum"],
        ascending=[False, False, False],
    )

    lines = [
        "# Base Core 6 Price Overheat Without Fundamental Improve Rolling Validation V1",
        "",
        "Protocol:",
        "- factor engine = annual pure-fundamental `base_core_6`",
        f"- combo fixed at `{TARGET_COMBO}`",
        "- stock selection fixed at `top bucket` from the five-group cross-section",
        "- a stock becomes eligible for overheat capping only if its fundamentals did not improve enough at entry",
        "- fundamental improvement is counted across the six resident `base_core_6` fields versus the previous rebalance snapshot",
        f"- minimum available improvement signals required = `{MIN_AVAILABLE_IMPROVEMENT_SIGNALS}`",
        "- only eligible stocks are capped after price overheat; other holdings keep their original weight",
        "- released weight stays in cash with `0` return",
        "- tested price-overheat trigger growth = `15% / 20%`",
        "- tested post-trigger stock cap = `15% / 10%`",
        "- tested poor-improvement threshold = `improve_count <= 1 / 2`",
        "",
        "Baseline means:",
        f"- train/test/review cum = `{format_float(baseline_train_mean)}` / `{format_float(baseline_test_mean)}` / `{format_float(baseline_review_mean)}`",
        "",
        "Candidate ranking:",
    ]

    for _, row in summary_df.iterrows():
        lines.append(
            f"- `{row['config_key']}` | folds=`{int(row['folds'])}` | "
            f"mean_train_cum=`{format_float(row['mean_train_cum'])}` | "
            f"mean_test_cum=`{format_float(row['mean_test_cum'])}` | "
            f"mean_review_cum=`{format_float(row['mean_review_cum'])}` | "
            f"delta_test_vs_baseline=`{format_float(row['delta_test_vs_baseline'])}` | "
            f"delta_review_vs_baseline=`{format_float(row['delta_review_vs_baseline'])}` | "
            f"mean_review_cash=`{format_float(row['mean_review_cash'])}` | "
            f"mean_review_trim_events=`{format_float(row['mean_review_trim_events'])}` | "
            f"mean_review_weight_sum=`{format_float(row['mean_review_weight_sum'])}`"
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
    base_rows, enhanced_rows, universe_rows = filter_factor_universe(base_rows, enhanced_rows, universe_rows)
    may_dates = get_may_rebalance_dates(panel_df)
    folds = build_yearly_folds_custom(may_dates)

    daily_cache: dict[str, pd.DataFrame] = {}
    for code in sorted(panel_df["code"].astype(str).unique()):
        daily_cache[code] = load_daily_path(code)

    config_rows: list[dict[str, object]] = []
    for fold in folds:
        master_df = build_master_frame(
            panel_df=panel_df,
            fold=fold,
            base_rows=base_rows,
            enhanced_rows=enhanced_rows,
            universe_rows=universe_rows,
            daily_cache=daily_cache,
        )
        if master_df.empty:
            continue
        config_rows.extend(build_config_rows(master_df, fold))

    write_csv(OUTPUT_CONFIG_RESULTS_PATH, config_rows)
    write_summary(config_rows)
    print(OUTPUT_CONFIG_RESULTS_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
