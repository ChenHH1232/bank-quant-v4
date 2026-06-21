from jqdata import *
from datetime import date, datetime
from math import ceil

import numpy as np
import pandas as pd


def initialize(context):
    g.strategy_variant = "fixed_60_40"
    g.allowed_variants = [
        "fixed_60_40",
        "delta_median_only",
        "breadth_only",
    ]

    g.bank_stocks = [
        "000001.XSHE", "001227.XSHE", "002142.XSHE", "002807.XSHE",
        "002839.XSHE", "002936.XSHE", "002948.XSHE", "002958.XSHE",
        "002966.XSHE", "600000.XSHG", "600015.XSHG", "600016.XSHG",
        "600036.XSHG", "600908.XSHG", "600919.XSHG", "600926.XSHG",
        "600928.XSHG", "601009.XSHG", "601077.XSHG", "601128.XSHG",
        "601166.XSHG", "601169.XSHG", "601187.XSHG", "601229.XSHG",
        "601288.XSHG", "601328.XSHG", "601398.XSHG", "601528.XSHG",
        "601577.XSHG", "601658.XSHG", "601665.XSHG", "601818.XSHG",
        "601825.XSHG", "601838.XSHG", "601860.XSHG", "601916.XSHG",
        "601939.XSHG", "601963.XSHG", "601988.XSHG", "601997.XSHG",
        "601998.XSHG", "603323.XSHG",
    ]

    g.engine_stock_cap = 0.05
    g.final_stock_cap = 0.08

    g.min_listing_trade_days = 240
    g.max_price_history_count = 270
    g.pool_history_count = 20
    g.pool_keep_ratio = 0.60

    g.executed_fundamental_dates = set()
    g.executed_rebalance_dates = set()
    g.latest_rebalance_log = None
    g.debug = True

    g.approved_pool_schedule = [
        {"effective_date": "2021-05-31", "codes": ["002142.XSHE", "600036.XSHG", "601009.XSHG", "600926.XSHG", "601658.XSHG", "601838.XSHG", "600908.XSHG"]},
        {"effective_date": "2021-09-01", "codes": ["002142.XSHE", "600036.XSHG", "601009.XSHG", "600926.XSHG", "601658.XSHG", "600908.XSHG", "601838.XSHG"]},
        {"effective_date": "2021-11-01", "codes": ["002142.XSHE", "600036.XSHG", "601009.XSHG", "600926.XSHG", "601658.XSHG", "600908.XSHG", "601838.XSHG"]},
        {"effective_date": "2022-05-05", "codes": ["600036.XSHG", "002142.XSHE", "600926.XSHG", "601838.XSHG", "601009.XSHG", "002839.XSHE", "600908.XSHG"]},
        {"effective_date": "2022-09-01", "codes": ["600036.XSHG", "002142.XSHE", "601009.XSHG", "600926.XSHG", "601838.XSHG", "600908.XSHG", "601658.XSHG"]},
        {"effective_date": "2022-11-01", "codes": ["600036.XSHG", "002142.XSHE", "601009.XSHG", "601838.XSHG", "601658.XSHG", "600926.XSHG", "600908.XSHG"]},
        {"effective_date": "2023-05-04", "codes": ["600036.XSHG", "002142.XSHE", "600926.XSHG", "601658.XSHG", "601825.XSHG", "601838.XSHG", "601528.XSHG", "601009.XSHG"]},
        {"effective_date": "2023-09-01", "codes": ["601398.XSHG", "601288.XSHG", "601939.XSHG", "600036.XSHG", "601988.XSHG", "601825.XSHG", "601658.XSHG", "601077.XSHG"]},
        {"effective_date": "2023-11-01", "codes": ["601398.XSHG", "601288.XSHG", "601939.XSHG", "600036.XSHG", "601988.XSHG", "601825.XSHG", "601658.XSHG", "601077.XSHG"]},
        {"effective_date": "2024-05-06", "codes": ["601398.XSHG", "601288.XSHG", "601988.XSHG", "600036.XSHG", "601939.XSHG", "601825.XSHG", "601658.XSHG", "601077.XSHG"]},
        {"effective_date": "2024-09-02", "codes": ["601988.XSHG", "601398.XSHG", "601288.XSHG", "601939.XSHG", "600036.XSHG", "601328.XSHG", "601187.XSHG", "600016.XSHG"]},
        {"effective_date": "2024-11-01", "codes": ["601988.XSHG", "601398.XSHG", "601939.XSHG", "601288.XSHG", "600036.XSHG", "600016.XSHG", "601077.XSHG", "601328.XSHG"]},
        {"effective_date": "2025-05-06", "codes": ["601988.XSHG", "601398.XSHG", "601288.XSHG", "601939.XSHG", "600036.XSHG", "601328.XSHG", "601187.XSHG", "601169.XSHG"]},
        {"effective_date": "2025-09-01", "codes": ["600036.XSHG", "601398.XSHG", "601288.XSHG", "601939.XSHG", "601988.XSHG", "601825.XSHG", "002142.XSHE", "601077.XSHG"]},
        {"effective_date": "2025-11-03", "codes": ["600036.XSHG", "601398.XSHG", "601288.XSHG", "601939.XSHG", "601988.XSHG", "601825.XSHG", "601658.XSHG", "601077.XSHG"]},
        {"effective_date": "2026-05-06", "codes": ["600036.XSHG", "601398.XSHG", "601288.XSHG", "601939.XSHG", "601988.XSHG", "601825.XSHG", "601658.XSHG", "601077.XSHG"]},
    ]

    # Frozen annual state schedules from local pre-2021 validated proxy family.
    # State updates only at annual refresh points and is then carried until next annual refresh.
    # 2026-05-06 uses the last frozen annual state because the local offline panel currently ends before a fresh 2026 annual proxy refresh.
    g.variant_budget_schedule = {
        "fixed_60_40": [
            build_budget_plan("2021-05-31", "fixed", 0.60, 0.40, "fixed dual-engine baseline"),
            build_budget_plan("2022-05-05", "fixed", 0.60, 0.40, "fixed dual-engine baseline"),
            build_budget_plan("2023-05-04", "fixed", 0.60, 0.40, "fixed dual-engine baseline"),
            build_budget_plan("2024-05-06", "fixed", 0.60, 0.40, "fixed dual-engine baseline"),
            build_budget_plan("2025-05-06", "fixed", 0.60, 0.40, "fixed dual-engine baseline"),
            build_budget_plan("2026-05-06", "fixed", 0.60, 0.40, "fixed dual-engine baseline"),
        ],
        "delta_median_only": [
            build_budget_plan("2021-05-31", "weak_down", 1.00, 0.00, "score_delta_median q33/q67 from 2021-05-06"),
            build_budget_plan("2022-05-05", "strong_up", 0.60, 0.40, "score_delta_median q33/q67 from 2022-05-05"),
            build_budget_plan("2023-05-04", "neutral_flat", 0.80, 0.20, "score_delta_median q33/q67 from 2023-05-04"),
            build_budget_plan("2024-05-06", "neutral_flat", 0.80, 0.20, "score_delta_median q33/q67 from 2024-05-06"),
            build_budget_plan("2025-05-06", "neutral_flat", 0.80, 0.20, "score_delta_median q33/q67 from 2025-05-06"),
            build_budget_plan("2026-05-06", "neutral_flat", 0.80, 0.20, "carry forward last frozen annual delta-median state"),
        ],
        "breadth_only": [
            build_budget_plan("2021-05-31", "neutral_flat", 0.80, 0.20, "negative deterioration_ratio q33/q67 from 2021-05-06"),
            build_budget_plan("2022-05-05", "strong_up", 0.60, 0.40, "negative deterioration_ratio q33/q67 from 2022-05-05"),
            build_budget_plan("2023-05-04", "neutral_flat", 0.80, 0.20, "negative deterioration_ratio q33/q67 from 2023-05-04"),
            build_budget_plan("2024-05-06", "strong_up", 0.60, 0.40, "negative deterioration_ratio q33/q67 from 2024-05-06"),
            build_budget_plan("2025-05-06", "strong_up", 0.60, 0.40, "negative deterioration_ratio q33/q67 from 2025-05-06"),
            build_budget_plan("2026-05-06", "strong_up", 0.60, 0.40, "carry forward last frozen annual breadth state"),
        ],
    }

    validate_strategy_variant()

    set_benchmark("512800.XSHG")
    set_option("use_real_price", True)
    set_option("avoid_future_data", True)
    set_order_cost(
        OrderCost(
            open_commission=0.0003,
            close_commission=0.0003,
            close_tax=0.0,
            min_commission=5,
        ),
        type="stock",
    )

    run_daily(maybe_rebalance, time="09:40")
    run_daily(log_position_snapshot, time="14:55")


def maybe_rebalance(context):
    current_date = to_date(context.current_dt)
    current_date_str = current_date.strftime("%Y-%m-%d")

    if current_date_str in g.executed_rebalance_dates:
        return

    should_rebalance = False
    rebalance_reason = ""

    if len(context.portfolio.positions) == 0:
        should_rebalance = True
        rebalance_reason = "initial_build"
    else:
        due_plan = get_due_unexecuted_fundamental_plan(current_date)
        if due_plan is not None:
            should_rebalance = True
            rebalance_reason = "fundamental_refresh"
        elif is_first_trade_day_of_month(current_date):
            should_rebalance = True
            rebalance_reason = "monthly_momentum_refresh"

    if not should_rebalance:
        return

    success = do_rebalance(context, rebalance_reason)
    if success:
        g.executed_rebalance_dates.add(current_date_str)
        active_plan = get_active_fundamental_plan(current_date)
        if active_plan is not None:
            g.executed_fundamental_dates.add(active_plan["effective_date"])


def do_rebalance(context, rebalance_reason):
    current_date = to_date(context.current_dt)
    factor_date = get_previous_trade_date(context)

    active_plan = get_active_fundamental_plan(current_date)
    if active_plan is None:
        log.info("No active fundamental plan on %s" % str(current_date))
        return False

    budget_plan = get_active_budget_plan(current_date)
    if budget_plan is None:
        log.info("No active budget plan on %s variant=%s" % (str(current_date), g.strategy_variant))
        return False

    fundamental_budget = float(budget_plan["fundamental_budget"])
    momentum_budget = float(budget_plan["momentum_budget"])

    fundamental_weights = build_fundamental_engine_weights(active_plan["codes"], fundamental_budget)
    momentum_df = build_momentum_score_frame(factor_date)
    if momentum_df.empty:
        log.info("Momentum score frame is empty on %s" % str(factor_date))
        return False
    momentum_weights = build_momentum_engine_weights(momentum_df, momentum_budget)

    target_weight_map = combine_engine_weights(fundamental_weights, momentum_weights)
    if len(target_weight_map) == 0:
        log.info("Combined target weight map is empty on %s" % str(current_date))
        return False

    execute_target_value_map(context, target_weight_map)

    if g.debug:
        log.info("========== V4 state-routed dual-engine rebalance ==========")
        log.info(
            "current_date=%s factor_date=%s reason=%s fundamental_plan=%s strategy_variant=%s"
            % (str(current_date), str(factor_date), rebalance_reason, active_plan["effective_date"], g.strategy_variant)
        )
        log.info("budget_plan=%s" % str(budget_plan))
        log.info(
            "budget_summary=%s"
            % str(
                {
                    "fundamental_budget": fundamental_budget,
                    "momentum_budget": momentum_budget,
                    "engine_stock_cap": g.engine_stock_cap,
                    "final_stock_cap": g.final_stock_cap,
                }
            )
        )
        log.info("fundamental_codes=%s" % str(active_plan["codes"]))
        log.info("fundamental_weight_summary=%s" % str(summarize_weight_map(fundamental_weights)))
        log.info("momentum_top_preview=%s" % build_momentum_preview(momentum_df.head(12)))
        log.info("momentum_weight_summary=%s" % str(summarize_weight_map(momentum_weights)))
        log.info("combined_weight_summary=%s" % str(summarize_weight_map(target_weight_map)))

    g.latest_rebalance_log = {
        "mode": "state_routed_dual_engine_v1",
        "strategy_variant": g.strategy_variant,
        "current_date": str(current_date),
        "factor_date": str(factor_date),
        "rebalance_reason": rebalance_reason,
        "fundamental_plan_date": active_plan["effective_date"],
        "budget_plan_date": budget_plan["effective_date"],
        "state_bucket": budget_plan["state_bucket"],
        "fundamental_count": len(fundamental_weights),
        "momentum_count": len(momentum_weights),
        "final_count": len(target_weight_map),
    }
    return True


def validate_strategy_variant():
    if g.strategy_variant not in g.allowed_variants:
        raise ValueError("Unsupported g.strategy_variant=%s" % str(g.strategy_variant))


def build_budget_plan(effective_date, state_bucket, fundamental_budget, momentum_budget, source_note):
    return {
        "effective_date": effective_date,
        "state_bucket": state_bucket,
        "fundamental_budget": fundamental_budget,
        "momentum_budget": momentum_budget,
        "source_note": source_note,
    }


def get_active_budget_plan(current_date):
    plan_list = g.variant_budget_schedule.get(g.strategy_variant, [])
    active = None
    for plan in plan_list:
        plan_date = pd.Timestamp(plan["effective_date"]).date()
        if plan_date <= current_date:
            active = plan
    return active


def get_active_fundamental_plan(current_date):
    active = None
    for plan in g.approved_pool_schedule:
        plan_date = pd.Timestamp(plan["effective_date"]).date()
        if plan_date <= current_date:
            active = plan
    return active


def get_due_unexecuted_fundamental_plan(current_date):
    active = get_active_fundamental_plan(current_date)
    if active is None:
        return None
    if active["effective_date"] in g.executed_fundamental_dates:
        return None
    return active


def build_fundamental_engine_weights(codes, budget):
    tradable_codes = get_tradable_stocks(codes)
    if len(tradable_codes) == 0:
        return {}

    score_df = pd.DataFrame({"code": tradable_codes})
    score_df["rank_score"] = list(range(len(score_df), 0, -1))
    return build_ranked_weight_map(score_df, "rank_score", budget, g.engine_stock_cap)


def build_momentum_score_frame(factor_date):
    tradable = get_tradable_stocks(g.bank_stocks)
    if len(tradable) == 0:
        return pd.DataFrame()

    trade_days = get_trade_days(end_date=factor_date, count=g.max_price_history_count)
    if trade_days is None or len(trade_days) < g.max_price_history_count:
        return pd.DataFrame()

    start_date = to_date(trade_days[0])
    price_df = fetch_price_history_by_range(tradable, start_date, factor_date)
    valuation_df = fetch_market_cap_history_by_range(tradable, start_date, factor_date)
    if price_df.empty or valuation_df.empty:
        return pd.DataFrame()

    feature_df = build_feature_frame_for_date(tradable, factor_date, price_df, valuation_df)
    if feature_df.empty:
        return pd.DataFrame()

    pool_df = feature_df[feature_df["pool_flag"] == 1].copy()
    if pool_df.empty:
        pool_df = feature_df[feature_df["price_ready"] == 1].copy()
    if pool_df.empty:
        return pd.DataFrame()

    pool_df["final_score"] = score_series(pool_df["mom_12_1"], "larger_better")
    pool_df = pool_df.dropna(subset=["final_score"]).copy()
    pool_df = pool_df.sort_values(["final_score", "code"], ascending=[False, True]).reset_index(drop=True)
    return pool_df


def build_momentum_engine_weights(momentum_df, budget):
    return build_ranked_weight_map(momentum_df, "final_score", budget, g.engine_stock_cap)


def build_ranked_weight_map(score_df, score_col, budget, cap):
    weights = pd.Series(index=score_df.index, data=0.0, dtype="float64")
    if budget <= 0 or score_df is None or len(score_df) == 0:
        return {}

    work = score_df.dropna(subset=[score_col]).sort_values([score_col, "code"], ascending=[False, True]).copy()
    if work.empty:
        return {}

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

        if bool((proposed <= cap + 1e-12).all()):
            for idx, value in proposed.items():
                weights.loc[idx] += float(value)
            remaining_budget = 0.0
            break

        for idx, value in proposed.items():
            if float(value) <= cap + 1e-12:
                continue
            additional_room = max(0.0, cap - float(weights.loc[idx]))
            if additional_room > 1e-12:
                weights.loc[idx] += additional_room
                remaining_budget -= additional_room
            capped_this_round.append(idx)

        if len(capped_this_round) == 0:
            for idx, value in proposed.items():
                room = max(0.0, cap - float(weights.loc[idx]))
                add_value = min(float(value), room)
                if add_value > 1e-12:
                    weights.loc[idx] += add_value
                    remaining_budget -= add_value
            break

        active_index = [
            idx for idx in active_index
            if idx not in capped_this_round and float(weights.loc[idx]) < cap - 1e-12
        ]

    out = {}
    for idx in work.index:
        code = work.loc[idx, "code"]
        value = float(weights.loc[idx])
        if value > 1e-10:
            out[code] = value
    return out


def combine_engine_weights(fundamental_weights, momentum_weights):
    combined = {}
    all_codes = sorted(set(fundamental_weights.keys()) | set(momentum_weights.keys()))
    for code in all_codes:
        weight = float(fundamental_weights.get(code, 0.0)) + float(momentum_weights.get(code, 0.0))
        if weight <= 1e-10:
            continue
        combined[code] = min(weight, g.final_stock_cap)
    return combined


def build_feature_frame_for_date(stocks, factor_date, price_df, valuation_df):
    current_data = get_current_data()
    rows = []
    for stock in stocks:
        listing_trade_days = get_listing_trade_days(stock, factor_date)
        payload = {
            "code": stock,
            "display_name": safe_name(current_data, stock),
            "mom_3_1": np.nan,
            "mom_6_1": np.nan,
            "mom_12_1": np.nan,
            "avg_money_20d_pre_rebalance": np.nan,
            "avg_market_cap_20d_pre_rebalance": np.nan,
            "listing_trade_days": listing_trade_days,
        }

        one_price = price_df[(price_df["code"] == stock) & (price_df["time"] <= pd.Timestamp(factor_date))].sort_values("time").copy()
        one_valuation = valuation_df[(valuation_df["code"] == stock) & (valuation_df["day"] <= pd.Timestamp(factor_date))].sort_values("day").copy()

        if len(one_price) >= g.max_price_history_count:
            close_series = pd.to_numeric(one_price["close"], errors="coerce").reset_index(drop=True)
            money_series = pd.to_numeric(one_price["money"], errors="coerce").reset_index(drop=True)
            payload["mom_3_1"] = calc_skip_month_momentum(close_series, 63, 21)
            payload["mom_6_1"] = calc_skip_month_momentum(close_series, 126, 21)
            payload["mom_12_1"] = calc_skip_month_momentum(close_series, 240, 21)
            trailing_money = money_series.tail(g.pool_history_count).dropna()
            if len(trailing_money) >= g.pool_history_count:
                payload["avg_money_20d_pre_rebalance"] = float(trailing_money.mean())

        if len(one_valuation) >= g.pool_history_count:
            mcap_series = pd.to_numeric(one_valuation["market_cap"], errors="coerce").dropna().tail(g.pool_history_count)
            if len(mcap_series) >= g.pool_history_count:
                payload["avg_market_cap_20d_pre_rebalance"] = float(mcap_series.mean())

        rows.append(payload)

    out = pd.DataFrame(rows).sort_values("code").reset_index(drop=True)
    out["price_ready"] = (
        out["mom_3_1"].notna()
        & out["mom_6_1"].notna()
        & out["mom_12_1"].notna()
        & out["avg_money_20d_pre_rebalance"].notna()
        & out["avg_market_cap_20d_pre_rebalance"].notna()
        & (pd.to_numeric(out["listing_trade_days"], errors="coerce") >= g.min_listing_trade_days)
    ).astype(int)
    liq_flag, mcap_flag, pool_flag = build_pool_flags(out)
    out["liquidity_top_60_flag"] = liq_flag
    out["market_cap_top_60_flag"] = mcap_flag
    out["pool_flag"] = pool_flag
    return out


def build_pool_flags(df):
    liq_flag = pd.Series(index=df.index, data=0, dtype="int64")
    mcap_flag = pd.Series(index=df.index, data=0, dtype="int64")

    ready_liq = df["price_ready"].eq(1) & df["avg_money_20d_pre_rebalance"].notna()
    ready_mcap = df["price_ready"].eq(1) & df["avg_market_cap_20d_pre_rebalance"].notna()
    valid_liq = int(ready_liq.sum())
    valid_mcap = int(ready_mcap.sum())
    liq_keep = int(ceil(valid_liq * g.pool_keep_ratio)) if valid_liq > 0 else 0
    mcap_keep = int(ceil(valid_mcap * g.pool_keep_ratio)) if valid_mcap > 0 else 0

    if liq_keep > 0:
        liq_rank = df.loc[ready_liq, "avg_money_20d_pre_rebalance"].rank(method="first", ascending=False)
        liq_flag.loc[liq_rank.index] = (liq_rank <= liq_keep).astype(int)

    if mcap_keep > 0:
        mcap_rank = df.loc[ready_mcap, "avg_market_cap_20d_pre_rebalance"].rank(method="first", ascending=False)
        mcap_flag.loc[mcap_rank.index] = (mcap_rank <= mcap_keep).astype(int)

    pool_flag = ((liq_flag == 1) & (mcap_flag == 1) & df["price_ready"].eq(1)).astype(int)
    return liq_flag, mcap_flag, pool_flag


def fetch_price_history_by_range(stocks, start_date, end_date):
    try:
        df = get_price(
            stocks,
            start_date=start_date,
            end_date=end_date,
            frequency="daily",
            fields=["close", "money"],
            skip_paused=False,
            fq="pre",
            panel=False,
        )
    except Exception as exc:
        log.info("get_price failed on %s to %s: %s" % (str(start_date), str(end_date), str(exc)))
        return pd.DataFrame()

    if df is None or len(df) == 0:
        return pd.DataFrame()

    out = df.copy()
    if "time" not in out.columns and "day" in out.columns:
        out = out.rename(columns={"day": "time"})
    out["time"] = pd.to_datetime(out["time"])
    out["close"] = pd.to_numeric(out["close"], errors="coerce")
    out["money"] = pd.to_numeric(out["money"], errors="coerce")
    return out[["time", "code", "close", "money"]].copy()


def fetch_market_cap_history_by_range(stocks, start_date, end_date):
    trade_count = len(get_trade_days(start_date=start_date, end_date=end_date))
    if trade_count <= 0:
        return pd.DataFrame()
    try:
        df = get_fundamentals_continuously(
            query(
                valuation.code,
                valuation.market_cap,
            ).filter(valuation.code.in_(stocks)),
            end_date=end_date,
            count=trade_count,
            panel=False,
        )
    except Exception as exc:
        log.info("get_fundamentals_continuously failed on %s to %s: %s" % (str(start_date), str(end_date), str(exc)))
        return pd.DataFrame()

    if df is None or len(df) == 0:
        return pd.DataFrame()

    out = df.copy()
    if "day" not in out.columns and "date" in out.columns:
        out = out.rename(columns={"date": "day"})
    out["day"] = pd.to_datetime(out["day"])
    out["market_cap"] = pd.to_numeric(out["market_cap"], errors="coerce")
    out = out[out["day"] >= pd.Timestamp(start_date)].copy()
    return out[["day", "code", "market_cap"]].copy()


def get_listing_trade_days(stock, factor_date):
    try:
        start_date = get_security_info(stock).start_date
    except Exception:
        return np.nan
    if start_date is None:
        return np.nan
    try:
        trade_days = get_trade_days(start_date=start_date, end_date=factor_date)
    except Exception:
        return np.nan
    if trade_days is None:
        return np.nan
    return len(trade_days)


def get_tradable_stocks(stocks):
    current_data = get_current_data()
    tradable = []
    for stock in stocks:
        try:
            data = current_data[stock]
            if data.paused or data.is_st:
                continue
            if "ST" in data.name or "*" in data.name or "闁偓" in data.name:
                continue
            tradable.append(stock)
        except Exception:
            continue
    return tradable


def execute_target_value_map(context, target_weight_map):
    current_positions = list(context.portfolio.positions.keys())
    target_codes = set(target_weight_map.keys())

    for stock in current_positions:
        if stock not in target_codes:
            try:
                order_target_value(stock, 0)
            except Exception as exc:
                log.info("sell failed %s %s" % (stock, str(exc)))

    total_value = float(context.portfolio.total_value)
    for stock in sorted(target_weight_map.keys()):
        try:
            order_target_value(stock, total_value * float(target_weight_map[stock]))
        except Exception as exc:
            log.info("buy failed %s %s" % (stock, str(exc)))


def score_series(values, direction):
    raw = pd.to_numeric(values, errors="coerce")
    non_null = raw.dropna()
    if non_null.empty:
        return pd.Series(index=raw.index, data=np.nan)

    lower = float(non_null.quantile(0.01))
    upper = float(non_null.quantile(0.99))
    clipped = raw.clip(lower=lower, upper=upper)
    clipped_non_null = clipped.dropna()
    if clipped_non_null.empty:
        return pd.Series(index=raw.index, data=np.nan)

    mean_value = float(clipped_non_null.mean())
    std_value = float(clipped_non_null.std(ddof=0))
    if pd.isna(std_value) or std_value <= 1e-12:
        return pd.Series(index=raw.index, data=np.nan)

    z_values = (clipped - mean_value) / std_value
    multiplier = 1.0 if direction == "larger_better" else -1.0
    return z_values * multiplier


def calc_skip_month_momentum(close_series, lookback_days, skip_days):
    required_count = lookback_days + skip_days + 1
    if close_series is None or len(close_series) < required_count:
        return np.nan
    base_close = close_series.iloc[-(lookback_days + 1)]
    skip_close = close_series.iloc[-skip_days]
    if pd.isna(base_close) or pd.isna(skip_close) or abs(float(base_close)) <= 1e-12:
        return np.nan
    return float(skip_close) / float(base_close) - 1.0


def summarize_weight_map(weight_map):
    if weight_map is None or len(weight_map) == 0:
        return {"count": 0, "sum": 0.0, "max": 0.0}
    values = list(weight_map.values())
    return {
        "count": len(weight_map),
        "sum": safe_round(sum(values), 6),
        "max": safe_round(max(values), 6),
        "top": sorted(weight_map.items(), key=lambda item: (-item[1], item[0]))[:10],
    }


def build_momentum_preview(df):
    if df is None or len(df) == 0:
        return "[]"
    preview = []
    for _, row in df.iterrows():
        preview.append(
            "%s:score=%s,m12=%s"
            % (
                row["code"],
                str(safe_round(row.get("final_score"), 4)),
                str(safe_round(row.get("mom_12_1"), 4)),
            )
        )
    return "[" + " ; ".join(preview) + "]"


def log_position_snapshot(context):
    if not g.debug:
        return
    current_date = str(to_date(context.current_dt))
    positions = context.portfolio.positions
    if len(positions) == 0:
        log.info(
            "position_snapshot date=%s holdings=[] total_value=%.2f cash=%.2f"
            % (current_date, float(context.portfolio.total_value), float(context.portfolio.available_cash))
        )
        return

    parts = []
    for stock in sorted(positions.keys()):
        pos = positions[stock]
        market_value = float(pos.price * pos.total_amount)
        weight = market_value / float(context.portfolio.total_value) if context.portfolio.total_value > 0 else np.nan
        parts.append(
            "%s:w=%.4f,amt=%s,price=%.2f,cost=%.2f,mv=%.2f"
            % (stock, weight, str(int(pos.total_amount)), float(pos.price), float(pos.avg_cost), market_value)
        )
    log.info(
        "position_snapshot date=%s holding_count=%d total_value=%.2f cash=%.2f holdings=[%s]"
        % (current_date, len(parts), float(context.portfolio.total_value), float(context.portfolio.available_cash), " ; ".join(parts))
    )
    if g.latest_rebalance_log is not None:
        log.info("latest_rebalance_log=%s" % str(g.latest_rebalance_log))


def is_first_trade_day_of_month(current_date):
    month_start = date(current_date.year, current_date.month, 1)
    trade_days = get_trade_days(start_date=month_start, end_date=current_date)
    if trade_days is None or len(trade_days) == 0:
        return False
    return to_date(trade_days[0]) == current_date


def get_previous_trade_date(context):
    try:
        return to_date(context.previous_date)
    except Exception:
        trade_days = get_trade_days(end_date=to_date(context.current_dt), count=2)
        if trade_days is None or len(trade_days) == 0:
            return to_date(context.current_dt)
        return to_date(trade_days[0])


def safe_name(current_data, stock):
    try:
        return current_data[stock].name
    except Exception:
        return ""


def safe_round(value, digits=6):
    try:
        if value is None or pd.isna(value):
            return None
        return round(float(value), digits)
    except Exception:
        return None


def to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if hasattr(value, "date"):
        return value.date()
    return pd.Timestamp(value).date()
