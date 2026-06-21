from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual
import build_weak_down_exit_rolling_validation_v1 as state_base

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "slow_fundamental_fast_exit_execution_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "slow_fundamental_fast_exit_execution_validation_v1.md"

MONTHLY_TARGET_COL = "y_month_avg_daily_return_close"

STRATEGY_SPECS = [
    {"strategy_name": "fixed_60_40", "mode": "fixed"},
    {"strategy_name": "annual_entry_monthly_exit_unconstrained", "mode": "unconstrained"},
    {"strategy_name": "annual_entry_monthly_exit_slow_fundamental", "mode": "slow_fundamental"},
]


def load_monthly_panel() -> pd.DataFrame:
    df = pd.read_csv(dual.MOMENTUM_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    df = df[df["rebalance_stock_pool_flag_v2"] == 1].copy()
    for col in ["mom_6_1", "mom_12_1", MONTHLY_TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["rebalance_date", "code", "mom_6_1", "mom_12_1", MONTHLY_TARGET_COL]].copy()


def get_target_budgets(state_bucket: str) -> tuple[float, float]:
    if state_bucket == "strong_up":
        return 0.6, 0.4
    if state_bucket == "weak_down":
        return 1.0, 0.0
    return 0.8, 0.2


def build_weight_series(group: pd.DataFrame, score_col: str, budget: float) -> pd.Series:
    return dual.build_engine_weights(group, score_col, budget, dual.ENGINE_STOCK_CAP)


def combine_weight_series(group: pd.DataFrame, fundamental_weight: pd.Series, momentum_weight: pd.Series) -> pd.DataFrame:
    work = group.copy()
    work["fundamental_weight"] = pd.to_numeric(fundamental_weight, errors="coerce").fillna(0.0)
    work["momentum_weight"] = pd.to_numeric(momentum_weight, errors="coerce").fillna(0.0)
    work["raw_final_weight"] = work["fundamental_weight"] + work["momentum_weight"]
    work["final_weight"] = dual.cap_final_weights(work["raw_final_weight"], dual.FINAL_STOCK_CAP)
    work["weighted_return"] = work["final_weight"] * pd.to_numeric(work[MONTHLY_TARGET_COL], errors="coerce").fillna(0.0)
    return work


def build_detail_rows(monthly_panel: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    quarterly_panel = dual.load_fundamental_panel()
    quarterly_panel["rebalance_date"] = pd.to_datetime(quarterly_panel["rebalance_date"])
    quarterly_panel = quarterly_panel[quarterly_panel["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()

    annual_state_df = state_base.load_annual_state_panel()
    monthly_release_df = state_base.build_monthly_release_panel(monthly_panel)

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        quarterly_train_mask = (quarterly_panel["rebalance_date"] >= train_start) & (quarterly_panel["rebalance_date"] < validation_start)
        scored_quarterly_df = dual.build_fundamental_score_frame(quarterly_panel, quarterly_train_mask)

        monthly_bridge_df = state_base.build_fundamental_monthly_bridge(scored_quarterly_df, monthly_panel)
        monthly_train_mask = (monthly_bridge_df["rebalance_date"] >= train_start) & (monthly_bridge_df["rebalance_date"] < validation_start)
        monthly_bridge_df["score__mom12"] = dual.preprocess_momentum_factor(monthly_bridge_df, monthly_train_mask)

        train_annual = annual_state_df[
            (annual_state_df["rebalance_date"] >= train_start) & (annual_state_df["rebalance_date"] < validation_start)
        ].copy()
        if train_annual.empty:
            continue
        annual_low_cut = float(train_annual["breadth_state_score"].quantile(0.33))
        annual_high_cut = float(train_annual["breadth_state_score"].quantile(0.67))

        train_release = monthly_release_df[
            (monthly_release_df["rebalance_date"] >= train_start) & (monthly_release_df["rebalance_date"] < validation_start)
        ].copy()
        if train_release.empty:
            continue
        release_cut = float(pd.to_numeric(train_release[state_base.MONTHLY_RELEASE_COL], errors="coerce").quantile(0.50))

        validation_df = monthly_bridge_df[
            (monthly_bridge_df["rebalance_date"] >= validation_start)
            & (monthly_bridge_df["rebalance_date"] <= validation_end)
        ].copy()
        if validation_df.empty:
            continue

        validation_dates = sorted(pd.to_datetime(validation_df["rebalance_date"].drop_duplicates()))
        annual_dates = sorted(pd.to_datetime(annual_state_df["rebalance_date"].drop_duplicates()))
        annual_state_map: dict[pd.Timestamp, dict[str, object]] = {}
        for annual_date, group in annual_state_df.groupby("rebalance_date", sort=True):
            score_value = float(group["breadth_state_score"].iloc[0])
            annual_state_map[pd.Timestamp(annual_date)] = {
                "score_value": score_value,
                "state_bucket": state_base.classify_state(score_value, annual_low_cut, annual_high_cut),
            }

        quarter_dates = sorted(pd.to_datetime(scored_quarterly_df["rebalance_date"].drop_duplicates()))
        month_to_annual = state_base.build_fundamental_monthly_bridge(
            pd.DataFrame({"rebalance_date": annual_dates, "code": [], dual.FUNDAMENTAL_COMBO: []}),
            pd.DataFrame({"rebalance_date": validation_dates, "code": []}),
        ) if False else None
        annual_idx = 0
        last_annual: pd.Timestamp | None = None
        month_to_annual_map: dict[pd.Timestamp, pd.Timestamp | None] = {}
        for month_date in validation_dates:
            while annual_idx < len(annual_dates) and annual_dates[annual_idx] <= month_date:
                last_annual = annual_dates[annual_idx]
                annual_idx += 1
            month_to_annual_map[month_date] = last_annual

        quarter_idx = 0
        last_quarter: pd.Timestamp | None = None
        month_to_quarter_map: dict[pd.Timestamp, pd.Timestamp | None] = {}
        for month_date in validation_dates:
            while quarter_idx < len(quarter_dates) and quarter_dates[quarter_idx] <= month_date:
                last_quarter = quarter_dates[quarter_idx]
                quarter_idx += 1
            month_to_quarter_map[month_date] = last_quarter

        release_map = monthly_release_df.set_index("rebalance_date")[state_base.MONTHLY_RELEASE_COL].to_dict()

        slow_fundamental_holdings: dict[str, float] = {}

        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[dual.FUNDAMENTAL_COMBO, "score__mom12", MONTHLY_TARGET_COL]).copy()
            if len(group) < 5:
                continue

            month_date = pd.Timestamp(rebalance_date)
            annual_anchor = month_to_annual_map.get(month_date)
            quarter_anchor = month_to_quarter_map.get(month_date)
            if annual_anchor is None or annual_anchor not in annual_state_map:
                continue
            if quarter_anchor is None:
                continue

            annual_bucket = str(annual_state_map[annual_anchor]["state_bucket"])
            release_value = release_map.get(month_date, np.nan)
            final_state_bucket = annual_bucket
            if annual_bucket == "weak_down" and pd.notna(release_value) and float(release_value) >= release_cut:
                final_state_bucket = "neutral_flat"

            target_fundamental_budget, target_momentum_budget = get_target_budgets(final_state_bucket)

            fundamental_unconstrained = build_weight_series(group, dual.FUNDAMENTAL_COMBO, target_fundamental_budget)
            momentum_weight = build_weight_series(group, "score__mom12", target_momentum_budget)

            if month_date == quarter_anchor:
                rebuilt_series = build_weight_series(group, dual.FUNDAMENTAL_COMBO, target_fundamental_budget)
                slow_fundamental_holdings = {
                    str(group.loc[idx, "code"]): float(value)
                    for idx, value in rebuilt_series.items()
                    if float(value) > 1e-12
                }
            else:
                current_sum = float(sum(slow_fundamental_holdings.values()))
                if current_sum > target_fundamental_budget + 1e-12:
                    scale = target_fundamental_budget / current_sum if current_sum > 1e-12 else 0.0
                    slow_fundamental_holdings = {
                        code: float(weight) * scale
                        for code, weight in slow_fundamental_holdings.items()
                        if float(weight) * scale > 1e-12
                    }

            slow_fundamental_series = pd.Series(index=group.index, data=0.0, dtype="float64")
            code_to_index = dict(zip(group["code"], group.index))
            for code, value in slow_fundamental_holdings.items():
                idx = code_to_index.get(code)
                if idx is not None:
                    slow_fundamental_series.loc[idx] = float(value)

            strategy_payloads = {
                "fixed_60_40": combine_weight_series(
                    group,
                    build_weight_series(group, dual.FUNDAMENTAL_COMBO, 0.6),
                    build_weight_series(group, "score__mom12", 0.4),
                ),
                "annual_entry_monthly_exit_unconstrained": combine_weight_series(
                    group,
                    fundamental_unconstrained,
                    momentum_weight,
                ),
                "annual_entry_monthly_exit_slow_fundamental": combine_weight_series(
                    group,
                    slow_fundamental_series,
                    momentum_weight,
                ),
            }

            for spec in STRATEGY_SPECS:
                work = strategy_payloads[spec["strategy_name"]]
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "strategy_name": spec["strategy_name"],
                        "rebalance_date": month_date.strftime("%Y-%m-%d"),
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "annual_anchor_date": annual_anchor.strftime("%Y-%m-%d"),
                        "quarter_anchor_date": quarter_anchor.strftime("%Y-%m-%d"),
                        "annual_state_bucket": annual_bucket,
                        "final_state_bucket": final_state_bucket,
                        "release_signal_value": round(float(release_value), 6) if pd.notna(release_value) else np.nan,
                        "release_signal_cut": round(release_cut, 6),
                        "target_fundamental_budget": round(target_fundamental_budget, 6),
                        "target_momentum_budget": round(target_momentum_budget, 6),
                        "actual_fundamental_weight": round(float(pd.to_numeric(work["fundamental_weight"], errors="coerce").sum()), 6),
                        "actual_momentum_weight": round(float(pd.to_numeric(work["momentum_weight"], errors="coerce").sum()), 6),
                        "final_invested_weight": round(float(pd.to_numeric(work["final_weight"], errors="coerce").sum()), 6),
                        "cash_weight": round(float(max(0.0, 1.0 - pd.to_numeric(work["final_weight"], errors="coerce").sum())), 6),
                        "portfolio_return": round(float(pd.to_numeric(work["weighted_return"], errors="coerce").sum()), 10),
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
        "# Slow Fundamental Fast Exit Execution Validation V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- annual entry and monthly exit signal stay fixed at the current active candidate",
        "- only execution permission changes:",
        "- fundamental sleeve may rebuild on quarterly fundamental refresh dates",
        "- on non-quarter dates, fundamental sleeve may sell down but may not buy new fundamental positions",
        "- monthly restored risk budget still goes to the momentum sleeve",
        "",
        f"- fold count: `{len(folds)}`",
        "",
    ]
    if not df.empty:
        summary_df = (
            df.groupby("strategy_name", dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_cash=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_f_weight=("actual_fundamental_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_m_weight=("actual_momentum_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        lines.append("Strategy summary:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{format_float(row['mean_return'])}` | "
                f"cum_return=`{format_float(row['cumulative_return'])}` | "
                f"mean_cash=`{format_float(row['mean_cash'])}` | "
                f"mean_f_weight=`{format_float(row['mean_f_weight'])}` | "
                f"mean_m_weight=`{format_float(row['mean_m_weight'])}`"
            )

        slow_df = df[df["strategy_name"] == "annual_entry_monthly_exit_slow_fundamental"].copy()
        if not slow_df.empty:
            lines.extend(["", "Constraint behavior summary:"])
            lines.append(
                f"- non-quarter weak_down snapshots=`{int(((slow_df['final_state_bucket'] == 'weak_down') & (slow_df['rebalance_date'] != slow_df['quarter_anchor_date'])).sum())}`"
            )
            lines.append(
                f"- mean actual fundamental weight in slow variant=`{format_float(pd.to_numeric(slow_df['actual_fundamental_weight'], errors='coerce').mean())}`"
            )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    monthly_panel = load_monthly_panel()
    folds = dual.load_folds()
    rows = build_detail_rows(monthly_panel, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
