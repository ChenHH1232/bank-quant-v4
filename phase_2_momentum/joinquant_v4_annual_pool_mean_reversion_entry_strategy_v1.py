from jqdata import *
from datetime import date, datetime, timedelta
from math import ceil

import numpy as np
import pandas as pd


def initialize(context):
    g.bank_stocks = [
        "000001.XSHE", "001227.XSHE", "002142.XSHE", "002807.XSHE",
        "002839.XSHE", "002936.XSHE", "002948.XSHE", "002958.XSHE",
        "002966.XSHE", "600000.XSHG", "600015.XSHG", "600016.XSHG",
        "600036.XSHG", "600908.XSHG", "600919.XSHG", "600926.XSHG",
        "600928.XSHG", "601009.XSHG", "601077.XSHG", "601128.XSHG",
        "601166.XSHG", "601169.XSHG", "601187.XSHG", "601229.XSHG",
        "601288.XSHG", "601328.XSHG", "601398.XSHG", "601528.XSHG",
        "601577.XSHG", "601658.XSHG", "601665.XSHG", "601818.XSHG",
        "601825.XSHG", "601838.XSHG", "601916.XSHG", "601939.XSHG",
        "601963.XSHG", "601988.XSHG", "601997.XSHG", "601998.XSHG",
        "603323.XSHG",
    ]

    g.min_listing_trade_days = 60
    g.history_count = 25
    g.pool_history_count = 20
    g.pool_keep_ratio = 0.60
    g.initial_entry_ratio = 0.50
    g.remaining_entry_ratio = 0.50
    g.max_entry_wait_weeks = 4
    g.signal_trigger_threshold = 0.00
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
    ]

    g.executed_plan_dates = set()
    g.pending_entry = None
    g.latest_rebalance_log = None

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

    run_daily(maybe_handle_plan_activation, time="09:40")
    run_daily(maybe_complete_pending_entry, time="09:45")
    run_daily(log_position_snapshot, time="14:55")


def maybe_handle_plan_activation(context):
    current_date = to_date(context.current_dt)
    plan = get_due_plan(current_date)
    if plan is None:
        return
    plan_date_str = plan["effective_date"]
    if plan_date_str in g.executed_plan_dates:
        return
    do_plan_activation(context, plan)
    g.executed_plan_dates.add(plan_date_str)


def do_plan_activation(context, plan):
    current_date = to_date(context.current_dt)
    factor_date = get_previous_trade_date(context)
    approved_codes = list(plan["codes"])
    tradable_codes = get_tradable_stocks(approved_codes)
    if len(tradable_codes) == 0:
        log.info("No tradable approved codes on %s" % str(current_date))
        return

    execute_target_ratio(context, tradable_codes, g.initial_entry_ratio)
    liquidate_positions_not_in_target(context, tradable_codes)

    initial_signal = compute_pool_signal_snapshot(factor_date, tradable_codes)
    g.pending_entry = {
        "plan_date": str(current_date),
        "approved_codes": tradable_codes,
        "weeks_waited": 0,
        "initial_signal": initial_signal,
        "remaining_ratio": g.remaining_entry_ratio,
        "completed": False,
    }
    g.latest_rebalance_log = {
        "mode": "annual_pool_mean_reversion_entry_v1",
        "plan_date": str(current_date),
        "factor_date": str(factor_date),
        "approved_count": len(tradable_codes),
        "initial_entry_ratio": g.initial_entry_ratio,
        "remaining_entry_ratio": g.remaining_entry_ratio,
        "initial_signal": safe_round(initial_signal, 6),
        "approved_codes": "|".join(tradable_codes),
    }
    if g.debug:
        log.info("========== annual pool entry activation ==========")
        log.info("current_date=%s factor_date=%s approved_count=%d" % (str(current_date), str(factor_date), len(tradable_codes)))
        log.info("initial_signal=%s approved_codes=%s" % (str(safe_round(initial_signal, 6)), str(tradable_codes)))


def maybe_complete_pending_entry(context):
    if g.pending_entry is None or g.pending_entry.get("completed"):
        return

    current_date = to_date(context.current_dt)
    if not is_first_trade_day_of_week(current_date):
        return

    pending = g.pending_entry
    pending["weeks_waited"] += 1
    if pending["weeks_waited"] <= 1:
        return

    approved_codes = get_tradable_stocks(pending["approved_codes"])
    if len(approved_codes) == 0:
        return

    factor_date = get_previous_trade_date(context)
    current_signal = compute_pool_signal_snapshot(factor_date, approved_codes)
    trigger_hit = False
    force_fill = False

    if current_signal is not None and not pd.isna(current_signal):
        if current_signal <= g.signal_trigger_threshold:
            trigger_hit = True
    if pending["weeks_waited"] >= g.max_entry_wait_weeks:
        force_fill = True

    if not trigger_hit and not force_fill:
        if g.debug:
            log.info(
                "pending_entry_wait current_date=%s weeks_waited=%d signal=%s trigger=%s"
                % (str(current_date), int(pending["weeks_waited"]), str(safe_round(current_signal, 6)), str(g.signal_trigger_threshold))
            )
        return

    execute_target_ratio(context, approved_codes, 1.0)
    pending["completed"] = True
    pending["completion_date"] = str(current_date)
    pending["completion_signal"] = current_signal
    pending["completion_reason"] = "signal_trigger" if trigger_hit else "force_fill"
    g.latest_rebalance_log = {
        "mode": "annual_pool_mean_reversion_entry_v1",
        "plan_date": pending["plan_date"],
        "completion_date": str(current_date),
        "weeks_waited": int(pending["weeks_waited"]),
        "completion_signal": safe_round(current_signal, 6),
        "completion_reason": pending["completion_reason"],
        "approved_codes": "|".join(approved_codes),
    }
    if g.debug:
        log.info("========== pending entry completion ==========")
        log.info(
            "current_date=%s weeks_waited=%d signal=%s reason=%s"
            % (
                str(current_date),
                int(pending["weeks_waited"]),
                str(safe_round(current_signal, 6)),
                pending["completion_reason"],
            )
        )


def compute_pool_signal_snapshot(factor_date, approved_codes):
    feature_df = build_current_feature_snapshot(factor_date, approved_codes)
    if feature_df.empty:
        return np.nan
    work_df = feature_df[(feature_df["price_ready"] == 1) & feature_df["rev5_abnvol"].notna()].copy()
    if work_df.empty:
        return np.nan
    return float(pd.to_numeric(work_df["rev5_abnvol"], errors="coerce").mean())


def build_current_feature_snapshot(factor_date, stocks):
    trade_days = get_trade_days(end_date=factor_date, count=g.history_count)
    if trade_days is None or len(trade_days) < g.history_count:
        return pd.DataFrame()

    start_date = to_date(trade_days[0])
    price_df = fetch_price_history_by_range(stocks, start_date, factor_date)
    valuation_df = fetch_market_cap_history_by_range(stocks, start_date, factor_date)
    if price_df.empty or valuation_df.empty:
        return pd.DataFrame()

    return build_feature_frame_for_date(stocks, factor_date, price_df, valuation_df)


def build_feature_frame_for_date(stocks, factor_date, price_df, valuation_df):
    current_data = get_current_data()
    rows = []
    for stock in stocks:
        security_info = get_security_info(stock)
        payload = {
            "code": stock,
            "display_name": safe_name(current_data, stock),
            "rev_5d": np.nan,
            "abnormal_volume_ratio": np.nan,
            "close_to_ma20": np.nan,
            "avg_money_20d": np.nan,
            "avg_market_cap_20d": np.nan,
            "listing_trade_days": np.nan,
        }

        one_price = price_df[(price_df["code"] == stock) & (price_df["time"] <= pd.Timestamp(factor_date))].sort_values("time").copy()
        one_valuation = valuation_df[(valuation_df["code"] == stock) & (valuation_df["day"] <= pd.Timestamp(factor_date))].sort_values("day").copy()

        if len(one_price) >= g.history_count:
            close_series = pd.to_numeric(one_price["close"], errors="coerce").reset_index(drop=True)
            money_series = pd.to_numeric(one_price["money"], errors="coerce").reset_index(drop=True)
            payload["rev_5d"] = calc_return(close_series, 5)
            payload["abnormal_volume_ratio"] = calc_abnormal_volume_ratio(money_series, 20)
            payload["close_to_ma20"] = calc_close_to_ma(close_series, 20)
            trailing_money = money_series.tail(g.pool_history_count).dropna()
            if len(trailing_money) >= g.pool_history_count:
                payload["avg_money_20d"] = float(trailing_money.mean())
            payload["listing_trade_days"] = calc_listing_trade_days(security_info.start_date, factor_date)

        if len(one_valuation) >= g.pool_history_count:
            mcap_series = pd.to_numeric(one_valuation["market_cap"], errors="coerce").dropna().tail(g.pool_history_count)
            if len(mcap_series) >= g.pool_history_count:
                payload["avg_market_cap_20d"] = float(mcap_series.mean())

        rows.append(payload)

    out = pd.DataFrame(rows).sort_values("code").reset_index(drop=True)
    out["price_ready"] = (
        out["rev_5d"].notna()
        & out["abnormal_volume_ratio"].notna()
        & out["close_to_ma20"].notna()
        & out["avg_money_20d"].notna()
        & out["avg_market_cap_20d"].notna()
        & (pd.to_numeric(out["listing_trade_days"], errors="coerce") >= g.min_listing_trade_days)
    ).astype(int)
    out["rev5_abnvol"] = (
        -0.7 * pd.to_numeric(out["rev_5d"], errors="coerce")
        + 0.3 * pd.to_numeric(out["abnormal_volume_ratio"], errors="coerce")
    )
    return out


def get_due_plan(current_date):
    active = None
    for plan in g.approved_pool_schedule:
        plan_date = pd.Timestamp(plan["effective_date"]).date()
        if plan_date <= current_date:
            active = plan
    return active


def execute_target_ratio(context, target_codes, total_ratio):
    target_codes = list(target_codes)
    if len(target_codes) == 0:
        return
    target_weight = float(total_ratio) / float(len(target_codes))
    for stock in target_codes:
        try:
            order_target_value(stock, context.portfolio.total_value * target_weight)
        except Exception as exc:
            log.info("buy failed %s %s" % (stock, str(exc)))


def liquidate_positions_not_in_target(context, target_codes):
    target_set = set(target_codes)
    for stock in list(context.portfolio.positions.keys()):
        if stock not in target_set:
            try:
                order_target_value(stock, 0)
            except Exception as exc:
                log.info("sell failed %s %s" % (stock, str(exc)))


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
            query(valuation.code, valuation.market_cap).filter(valuation.code.in_(stocks)),
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


def calc_return(close_series, lookback_days):
    if close_series is None or len(close_series) < lookback_days + 1:
        return np.nan
    base_close = close_series.iloc[-(lookback_days + 1)]
    current_close = close_series.iloc[-1]
    if pd.isna(base_close) or pd.isna(current_close) or abs(float(base_close)) <= 1e-12:
        return np.nan
    return float(current_close) / float(base_close) - 1.0


def calc_abnormal_volume_ratio(money_series, lookback_days):
    if money_series is None or len(money_series) < lookback_days:
        return np.nan
    latest_money = money_series.iloc[-1]
    base_series = money_series.iloc[-lookback_days:]
    avg_money = base_series.mean()
    if pd.isna(latest_money) or pd.isna(avg_money) or abs(float(avg_money)) <= 1e-12:
        return np.nan
    return float(latest_money) / float(avg_money) - 1.0


def calc_close_to_ma(close_series, ma_days):
    if close_series is None or len(close_series) < ma_days:
        return np.nan
    latest_close = close_series.iloc[-1]
    ma_value = close_series.iloc[-ma_days:].mean()
    if pd.isna(latest_close) or pd.isna(ma_value) or abs(float(ma_value)) <= 1e-12:
        return np.nan
    return float(latest_close) / float(ma_value) - 1.0


def calc_listing_trade_days(start_date, end_date):
    try:
        trade_days = get_trade_days(start_date=start_date, end_date=end_date)
        if trade_days is None:
            return np.nan
        return int(len(trade_days))
    except Exception:
        return np.nan


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


def is_first_trade_day_of_week(current_date):
    weekday = current_date.weekday()
    week_start = current_date - timedelta(days=weekday)
    trade_days = get_trade_days(start_date=week_start, end_date=current_date)
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
