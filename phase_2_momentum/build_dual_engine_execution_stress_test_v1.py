from __future__ import annotations

import csv
from pathlib import Path
import sys

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
FUNDAMENTAL_DIR = ROOT_DIR / "phase_1_fundamental"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(FUNDAMENTAL_DIR) not in sys.path:
    sys.path.insert(0, str(FUNDAMENTAL_DIR))

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual  # type: ignore

PRICE_PANEL_PATH = SCRIPT_DIR / "momentum_factor_panel_v2.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "dual_engine_execution_stress_test_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "dual_engine_execution_stress_test_v1.md"

TARGET_STRATEGY_NAME = "blend_60_40"
SCENARIOS = [
    {"scenario_name": "immediate_cost10bps", "delay_days": 0, "one_way_cost_bps": 10.0},
    {"scenario_name": "delay_1d_cost10bps", "delay_days": 1, "one_way_cost_bps": 10.0},
    {"scenario_name": "delay_3d_cost10bps", "delay_days": 3, "one_way_cost_bps": 10.0},
    {"scenario_name": "immediate_cost30bps", "delay_days": 0, "one_way_cost_bps": 30.0},
]


def load_price_panel() -> pd.DataFrame:
    df = pd.read_csv(PRICE_PANEL_PATH, encoding="utf-8-sig", usecols=["date", "code", "close"])
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["date", "code", "close"]).copy()
    return df.sort_values(["date", "code"]).reset_index(drop=True)


def build_target_weight_panel() -> pd.DataFrame:
    panel_df = dual.build_joint_panel()
    folds = dual.load_folds()
    all_rows: list[dict[str, object]] = []

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)
        validation_mask = (panel_df["rebalance_date"] >= validation_start) & (panel_df["rebalance_date"] <= validation_end)

        scored_df = dual.build_fundamental_score_frame(panel_df, train_mask)
        scored_df["score__mom12"] = dual.preprocess_momentum_factor(scored_df, train_mask)

        validation_df = scored_df[validation_mask].copy()
        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            work = group.dropna(subset=[dual.FUNDAMENTAL_COMBO, "score__mom12", dual.FUNDAMENTAL_TARGET_COL]).copy()
            if len(work) < 5:
                continue
            work["fundamental_weight"] = dual.build_engine_weights(
                work,
                dual.FUNDAMENTAL_COMBO,
                0.6,
                dual.ENGINE_STOCK_CAP,
            )
            work["momentum_weight"] = dual.build_engine_weights(
                work,
                "score__mom12",
                0.4,
                dual.ENGINE_STOCK_CAP,
            )
            work["raw_final_weight"] = work["fundamental_weight"] + work["momentum_weight"]
            work["final_weight"] = dual.cap_final_weights(work["raw_final_weight"], dual.FINAL_STOCK_CAP)
            work = work[work["final_weight"] > 0].copy()

            for _, row in work.iterrows():
                all_rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "train_start": fold["train_start"],
                        "train_end": fold["train_end"],
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "rebalance_date": pd.Timestamp(rebalance_date),
                        "code": row["code"],
                        "final_weight": float(row["final_weight"]),
                    }
                )

    out = pd.DataFrame(all_rows)
    if out.empty:
        return out
    return out.sort_values(["fold_id", "rebalance_date", "code"]).reset_index(drop=True)


def build_common_schedule() -> list[pd.Timestamp]:
    joint_panel = dual.build_joint_panel()
    unique_dates = sorted(pd.to_datetime(joint_panel["rebalance_date"]).drop_duplicates().tolist())
    return [pd.Timestamp(x) for x in unique_dates]


def build_trading_dates(price_df: pd.DataFrame) -> list[pd.Timestamp]:
    unique_dates = sorted(price_df["date"].drop_duplicates().tolist())
    return [pd.Timestamp(x) for x in unique_dates]


def shift_trading_date(signal_date: pd.Timestamp, delay_days: int, trading_dates: list[pd.Timestamp]) -> pd.Timestamp:
    if signal_date not in trading_dates:
        raise ValueError(f"signal date missing from daily price panel: {signal_date}")
    idx = trading_dates.index(signal_date)
    shifted_idx = min(idx + delay_days, len(trading_dates) - 1)
    return trading_dates[shifted_idx]


def build_price_matrix(price_df: pd.DataFrame) -> pd.DataFrame:
    return price_df.pivot(index="date", columns="code", values="close").sort_index()


def compute_weight_turnover(prev_weights: pd.Series, new_weights: pd.Series) -> float:
    universe = sorted(set(prev_weights.index.tolist()) | set(new_weights.index.tolist()))
    prev_aligned = prev_weights.reindex(universe).fillna(0.0)
    new_aligned = new_weights.reindex(universe).fillna(0.0)
    return float((new_aligned - prev_aligned).abs().sum() / 2.0)


def compute_period_return(
    weights: pd.Series,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    price_matrix: pd.DataFrame,
) -> float:
    if weights.empty:
        return 0.0
    start_prices = price_matrix.loc[start_date, weights.index]
    end_prices = price_matrix.loc[end_date, weights.index]
    valid_mask = start_prices.notna() & end_prices.notna()
    if valid_mask.sum() == 0:
        return 0.0
    valid_weights = weights[valid_mask].astype(float)
    weight_sum = float(valid_weights.sum())
    if weight_sum <= 0:
        return 0.0
    valid_weights = valid_weights / weight_sum
    stock_returns = (end_prices[valid_mask] / start_prices[valid_mask]) - 1.0
    gross_invested_return = float((valid_weights * stock_returns).sum())
    return gross_invested_return * weight_sum


def build_execution_detail(weight_df: pd.DataFrame, price_matrix: pd.DataFrame, trading_dates: list[pd.Timestamp]) -> pd.DataFrame:
    if weight_df.empty:
        return pd.DataFrame()

    schedule = build_common_schedule()
    next_signal_map = {
        schedule[i]: schedule[i + 1]
        for i in range(len(schedule) - 1)
    }

    detail_rows: list[dict[str, object]] = []
    for scenario in SCENARIOS:
        delay_days = int(scenario["delay_days"])
        cost_rate = float(scenario["one_way_cost_bps"]) / 10000.0

        for fold_id, fold_df in weight_df.groupby("fold_id", sort=True):
            signal_dates = sorted(pd.to_datetime(fold_df["rebalance_date"]).drop_duplicates().tolist())
            portfolio_value = 1.0
            prev_weights = pd.Series(dtype="float64")

            for signal_date in signal_dates:
                signal_ts = pd.Timestamp(signal_date)
                next_signal = next_signal_map.get(signal_ts)
                if next_signal is None:
                    continue

                current_weights_df = fold_df[fold_df["rebalance_date"] == signal_ts].copy()
                current_weights = current_weights_df.set_index("code")["final_weight"].astype(float).sort_index()
                exec_start = shift_trading_date(signal_ts, delay_days, trading_dates)
                exec_end = shift_trading_date(pd.Timestamp(next_signal), delay_days, trading_dates)
                turnover = compute_weight_turnover(prev_weights, current_weights)
                trade_cost = turnover * cost_rate
                period_return = compute_period_return(current_weights, exec_start, exec_end, price_matrix)

                pre_period_value = portfolio_value * (1.0 - trade_cost)
                post_period_value = pre_period_value * (1.0 + period_return)
                net_period_return = 0.0
                if portfolio_value > 0:
                    net_period_return = (post_period_value / portfolio_value) - 1.0

                detail_rows.append(
                    {
                        "strategy_name": TARGET_STRATEGY_NAME,
                        "scenario_name": scenario["scenario_name"],
                        "fold_id": fold_id,
                        "signal_date": signal_ts.strftime("%Y-%m-%d"),
                        "next_signal_date": pd.Timestamp(next_signal).strftime("%Y-%m-%d"),
                        "exec_start_date": exec_start.strftime("%Y-%m-%d"),
                        "exec_end_date": exec_end.strftime("%Y-%m-%d"),
                        "delay_days": delay_days,
                        "one_way_cost_bps": scenario["one_way_cost_bps"],
                        "stock_count": int(len(current_weights)),
                        "invested_weight": round(float(current_weights.sum()), 6),
                        "cash_weight": round(float(max(0.0, 1.0 - current_weights.sum())), 6),
                        "turnover_ratio": round(float(turnover), 6),
                        "trade_cost_ratio": round(float(trade_cost), 8),
                        "gross_period_return": round(float(period_return), 10),
                        "net_period_return": round(float(net_period_return), 10),
                        "portfolio_value_before": round(float(portfolio_value), 10),
                        "portfolio_value_after": round(float(post_period_value), 10),
                    }
                )

                portfolio_value = post_period_value
                prev_weights = current_weights

            if len(signal_dates) > 0 and not prev_weights.empty:
                terminal_turnover = float(prev_weights.sum())
                terminal_cost = terminal_turnover * cost_rate
                portfolio_value = portfolio_value * (1.0 - terminal_cost)
                detail_rows.append(
                    {
                        "strategy_name": TARGET_STRATEGY_NAME,
                        "scenario_name": scenario["scenario_name"],
                        "fold_id": fold_id,
                        "signal_date": "terminal_liquidation",
                        "next_signal_date": "",
                        "exec_start_date": "",
                        "exec_end_date": "",
                        "delay_days": delay_days,
                        "one_way_cost_bps": scenario["one_way_cost_bps"],
                        "stock_count": int(len(prev_weights)),
                        "invested_weight": 0.0,
                        "cash_weight": 1.0,
                        "turnover_ratio": round(float(terminal_turnover), 6),
                        "trade_cost_ratio": round(float(terminal_cost), 8),
                        "gross_period_return": 0.0,
                        "net_period_return": round(float(-terminal_cost), 10),
                        "portfolio_value_before": "",
                        "portfolio_value_after": round(float(portfolio_value), 10),
                    }
                )

    return pd.DataFrame(detail_rows)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    if df.empty:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(df.columns))
        writer.writeheader()
        writer.writerows(df.to_dict("records"))


def format_float(value: object, digits: int = 6) -> str:
    if value is None or value == "" or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(detail_df: pd.DataFrame) -> None:
    lines = [
        "# Dual Engine Execution Stress Test V1",
        "",
        "Objective:",
        "- hold the `blend_60_40` signal layer fixed",
        "- stress only the execution layer using delayed fills and higher one-way cost assumptions",
        "- check whether the current dual-engine baseline is execution-fragile before formal report writing",
        "",
        "Protocol:",
        "- research scope remains pre-2021 rolling validation folds only",
        "- target weights are rebuilt from the same `blend_60_40` rolling logic used in the main dual-engine test",
        "- returns are proxied from daily close-to-close paths between delayed execution dates",
        "- each rebalance pays one-way transaction cost on realized turnover",
        "- terminal liquidation cost is included for conservative comparability",
        "",
        "Scenarios:",
    ]
    for scenario in SCENARIOS:
        lines.append(
            f"- `{scenario['scenario_name']}` | delay=`{scenario['delay_days']}` trading day(s) | one_way_cost=`{scenario['one_way_cost_bps']}` bps"
        )

    if detail_df.empty:
        lines.extend(["", "No detail rows were produced."])
        OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    scenario_df = detail_df[detail_df["signal_date"] != "terminal_liquidation"].copy()
    summary_df = (
        detail_df.groupby(["scenario_name", "fold_id"], dropna=False)
        .agg(
            final_value=("portfolio_value_after", lambda s: pd.to_numeric(s, errors="coerce").dropna().iloc[-1]),
            avg_turnover=("turnover_ratio", lambda s: pd.to_numeric(s, errors="coerce").dropna().mean()),
            total_cost=("trade_cost_ratio", lambda s: pd.to_numeric(s, errors="coerce").fillna(0.0).sum()),
            periods=("signal_date", "count"),
        )
        .reset_index()
    )
    summary_df["cum_return"] = summary_df["final_value"] - 1.0

    scenario_summary = (
        summary_df.groupby("scenario_name", dropna=False)
        .agg(
            fold_count=("fold_id", "count"),
            mean_cum_return=("cum_return", "mean"),
            median_cum_return=("cum_return", "median"),
            min_cum_return=("cum_return", "min"),
            max_cum_return=("cum_return", "max"),
            mean_turnover=("avg_turnover", "mean"),
            mean_total_cost=("total_cost", "mean"),
        )
        .reset_index()
        .sort_values("mean_cum_return", ascending=False)
    )

    lines.extend(["", "Scenario summary:"])
    for _, row in scenario_summary.iterrows():
        lines.append(
            f"- `{row['scenario_name']}` | fold_count=`{int(row['fold_count'])}` | mean_cum_return=`{format_float(row['mean_cum_return'])}` | "
            f"median_cum_return=`{format_float(row['median_cum_return'])}` | range=`[{format_float(row['min_cum_return'])}, {format_float(row['max_cum_return'])}]` | "
            f"mean_turnover=`{format_float(row['mean_turnover'])}` | mean_total_cost=`{format_float(row['mean_total_cost'])}`"
        )

    baseline_value = scenario_summary.loc[
        scenario_summary["scenario_name"] == "immediate_cost10bps",
        "mean_cum_return",
    ]
    if not baseline_value.empty:
        baseline = float(baseline_value.iloc[0])
        lines.extend(["", "Relative to immediate_cost10bps:"])
        for scenario_name in ["delay_1d_cost10bps", "delay_3d_cost10bps", "immediate_cost30bps"]:
            subset = scenario_summary[scenario_summary["scenario_name"] == scenario_name]
            if subset.empty:
                continue
            delta_value = float(subset["mean_cum_return"].iloc[0]) - baseline
            lines.append(f"- `{scenario_name}` delta_mean_cum_return=`{format_float(delta_value)}`")

    if not scenario_df.empty:
        period_summary = (
            scenario_df.groupby("scenario_name", dropna=False)
            .agg(
                mean_gross_period_return=("gross_period_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_net_period_return=("net_period_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_invested_weight=("invested_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
        )
        lines.extend(["", "Period-level averages:"])
        for _, row in period_summary.iterrows():
            lines.append(
                f"- `{row['scenario_name']}` | mean_gross_period_return=`{format_float(row['mean_gross_period_return'])}` | "
                f"mean_net_period_return=`{format_float(row['mean_net_period_return'])}` | mean_invested_weight=`{format_float(row['mean_invested_weight'])}`"
            )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    weight_df = build_target_weight_panel()
    price_df = load_price_panel()
    trading_dates = build_trading_dates(price_df)
    price_matrix = build_price_matrix(price_df)
    detail_df = build_execution_detail(weight_df, price_matrix, trading_dates)
    write_csv(OUT_DETAIL_PATH, detail_df)
    write_summary(detail_df)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
