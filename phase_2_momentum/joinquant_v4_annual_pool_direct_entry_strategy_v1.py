from jqdata import *
from datetime import date, datetime

import numpy as np
import pandas as pd


def initialize(context):
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
    ]
    g.executed_plan_dates = set()
    g.latest_rebalance_log = None
    g.debug = True

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
    plan = get_due_plan(current_date)
    if plan is None:
        return
    if plan["effective_date"] in g.executed_plan_dates:
        return
    do_rebalance(context, plan)
    g.executed_plan_dates.add(plan["effective_date"])


def do_rebalance(context, plan):
    current_date = to_date(context.current_dt)
    tradable_codes = get_tradable_stocks(plan["codes"])
    if len(tradable_codes) == 0:
        log.info("No tradable approved codes on %s" % str(current_date))
        return

    liquidate_positions_not_in_target(context, tradable_codes)
    target_weight = 1.0 / float(len(tradable_codes))
    for stock in tradable_codes:
        try:
            order_target_value(stock, context.portfolio.total_value * target_weight)
        except Exception as exc:
            log.info("buy failed %s %s" % (stock, str(exc)))

    g.latest_rebalance_log = {
        "mode": "annual_pool_direct_entry_v1",
        "plan_date": str(current_date),
        "selected_count": len(tradable_codes),
        "approved_codes": "|".join(tradable_codes),
    }
    if g.debug:
        log.info("========== annual pool direct entry ==========")
        log.info("current_date=%s selected_count=%d codes=%s" % (str(current_date), len(tradable_codes), str(tradable_codes)))


def get_due_plan(current_date):
    active = None
    for plan in g.approved_pool_schedule:
        plan_date = pd.Timestamp(plan["effective_date"]).date()
        if plan_date <= current_date:
            active = plan
    return active


def get_tradable_stocks(stocks):
    current_data = get_current_data()
    tradable = []
    for stock in stocks:
        try:
            data = current_data[stock]
            if data.paused or data.is_st:
                continue
            if "ST" in data.name or "*" in data.name or "退" in data.name:
                continue
            tradable.append(stock)
        except Exception:
            continue
    return tradable


def liquidate_positions_not_in_target(context, target_codes):
    target_set = set(target_codes)
    for stock in list(context.portfolio.positions.keys()):
        if stock not in target_set:
            try:
                order_target_value(stock, 0)
            except Exception as exc:
                log.info("sell failed %s %s" % (stock, str(exc)))


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
