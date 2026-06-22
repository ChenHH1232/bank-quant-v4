from jqdata import *
from datetime import date, datetime
from math import ceil

import numpy as np
import pandas as pd


def initialize(context):
    # Switch among the three frozen post-rolling acceptance candidates here.
    g.strategy_variant = "mom12_top10_then_fundamental_top6"
    g.allowed_variants = [
        "direct_mom12_top6",
        "mom12_top10_then_fundamental_top4",
        "mom12_top10_then_fundamental_top6",
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

    g.min_listing_trade_days = 240
    g.max_price_history_count = 270
    g.pool_history_count = 20
    g.pool_keep_ratio = 0.60
    g.executed_rebalance_dates = set()
    g.latest_rebalance_log = None
    g.debug = True

    g.fundamental_rank_schedule = [
        {"effective_date": "2021-05-06", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601009.XSHG", "601166.XSHG", "600926.XSHG", "601939.XSHG", "601838.XSHG", "601288.XSHG", "601398.XSHG"]},
        {"effective_date": "2021-09-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601166.XSHG", "600926.XSHG", "601009.XSHG", "601939.XSHG", "601288.XSHG", "601577.XSHG", "601838.XSHG"]},
        {"effective_date": "2021-11-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601166.XSHG", "601939.XSHG", "601398.XSHG", "601288.XSHG", "000001.XSHE", "601988.XSHG", "600000.XSHG"]},
        {"effective_date": "2022-05-05", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601166.XSHG", "601288.XSHG", "601939.XSHG", "601838.XSHG", "601009.XSHG", "601398.XSHG", "600926.XSHG"]},
        {"effective_date": "2022-09-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601838.XSHG", "601009.XSHG", "601939.XSHG", "601288.XSHG", "600926.XSHG", "601398.XSHG", "601988.XSHG"]},
        {"effective_date": "2022-11-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601166.XSHG", "601288.XSHG", "601939.XSHG", "601398.XSHG", "000001.XSHE", "600926.XSHG", "601988.XSHG"]},
        {"effective_date": "2023-05-04", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601838.XSHG", "601166.XSHG", "601009.XSHG", "601939.XSHG", "601288.XSHG", "601398.XSHG", "002966.XSHE"]},
        {"effective_date": "2023-09-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601838.XSHG", "601658.XSHG", "601009.XSHG", "601288.XSHG", "601939.XSHG", "002966.XSHE", "601398.XSHG", "600926.XSHG"]},
        {"effective_date": "2023-11-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601288.XSHG", "601939.XSHG", "601166.XSHG", "601398.XSHG", "600926.XSHG", "601577.XSHG", "601988.XSHG"]},
        {"effective_date": "2024-05-06", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601288.XSHG", "601838.XSHG", "601939.XSHG", "601398.XSHG", "601009.XSHG", "002966.XSHE", "601825.XSHG"]},
        {"effective_date": "2024-09-02", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601838.XSHG", "601988.XSHG", "601166.XSHG", "601009.XSHG", "601288.XSHG", "002966.XSHE", "601825.XSHG"]},
        {"effective_date": "2024-11-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601288.XSHG", "601398.XSHG", "601939.XSHG", "601077.XSHG", "000001.XSHE", "601577.XSHG", "601166.XSHG"]},
        {"effective_date": "2025-05-06", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601838.XSHG", "601658.XSHG", "601288.XSHG", "601009.XSHG", "601939.XSHG", "601166.XSHG", "002966.XSHE", "601825.XSHG"]},
        {"effective_date": "2025-09-01", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601658.XSHG", "601838.XSHG", "601988.XSHG", "601009.XSHG", "601166.XSHG", "601288.XSHG", "002966.XSHE", "601825.XSHG"]},
        {"effective_date": "2025-11-03", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601288.XSHG", "601939.XSHG", "601658.XSHG", "601398.XSHG", "000001.XSHE", "601077.XSHG", "601166.XSHG", "600926.XSHG"]},
        {"effective_date": "2026-05-06", "ranked_codes": ["600036.XSHG", "002142.XSHE", "601288.XSHG", "601939.XSHG", "601658.XSHG", "601398.XSHG", "000001.XSHE", "601077.XSHG", "601166.XSHG", "600926.XSHG"]},
    ]

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
    elif is_first_trade_day_of_month(current_date):
        should_rebalance = True
        rebalance_reason = "monthly_first_trade_day"

    if not should_rebalance:
        return

    success = do_rebalance(context, rebalance_reason)
    if success:
        g.executed_rebalance_dates.add(current_date_str)


def do_rebalance(context, rebalance_reason):
    current_date = to_date(context.current_dt)
    factor_date = get_previous_trade_date(context)
    tradable = get_tradable_stocks(g.bank_stocks)
    if len(tradable) < 6:
        log.info("Tradable bank count is too small: %d" % len(tradable))
        return False

    feature_df = build_current_feature_snapshot(factor_date, tradable)
    if feature_df.empty:
        log.info("Current feature frame is empty on %s" % str(factor_date))
        return False

    pool_df = build_candidate_pool(feature_df)
    if pool_df.empty:
        log.info("Candidate pool is empty on %s" % str(factor_date))
        return False

    fundamental_rank_map, fundamental_plan_date = get_active_fundamental_rank_map(current_date)
    selected_df = select_holdings_by_variant(pool_df, fundamental_rank_map)
    if selected_df.empty:
        log.info("Selected holdings are empty on %s variant=%s" % (str(factor_date), g.strategy_variant))
        return False

    long_list = selected_df["code"].tolist()
    target_weight = 1.0 / float(len(long_list))
    execute_target_weights(context, long_list, target_weight)

    if g.debug:
        log.info("========== momentum-first fundamental candidate rebalance ==========")
        log.info(
            "current_date=%s factor_date=%s reason=%s variant=%s fundamental_plan_date=%s"
            % (str(current_date), str(factor_date), rebalance_reason, g.strategy_variant, str(fundamental_plan_date))
        )
        log.info(
            "selection_summary=%s"
            % str(
                {
                    "strict_pool_count": int((feature_df["pool_flag"] == 1).sum()),
                    "price_ready_count": int((feature_df["price_ready"] == 1).sum()),
                    "candidate_count": int(len(pool_df)),
                    "selected_count": int(len(selected_df)),
                }
            )
        )
        log.info("candidate_preview=%s" % build_candidate_preview(pool_df.head(15)))
        log.info("selected_preview=%s" % build_candidate_preview(selected_df.head(15)))

    g.latest_rebalance_log = {
        "mode": "momentum_first_fundamental_candidates_v1",
        "strategy_variant": g.strategy_variant,
        "current_date": str(current_date),
        "factor_date": str(factor_date),
        "rebalance_reason": rebalance_reason,
        "fundamental_plan_date": str(fundamental_plan_date),
        "selected_codes": "|".join(long_list),
        "selected_count": len(long_list),
    }
    return True


def validate_strategy_variant():
    if g.strategy_variant not in g.allowed_variants:
        raise ValueError("Unsupported g.strategy_variant=%s" % str(g.strategy_variant))


def get_active_fundamental_rank_map(current_date):
    active = None
    for plan in g.fundamental_rank_schedule:
        plan_date = pd.Timestamp(plan["effective_date"]).date()
        if plan_date <= current_date:
            active = plan
    if active is None:
        return {}, None
    rank_map = {}
    for idx, code in enumerate(active["ranked_codes"]):
        rank_map[code] = idx + 1
    return rank_map, active["effective_date"]


def build_current_feature_snapshot(factor_date, stocks):
    trade_days = get_trade_days(end_date=factor_date, count=g.max_price_history_count)
    if trade_days is None or len(trade_days) < g.max_price_history_count:
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
        payload = {
            "code": stock,
            "display_name": safe_name(current_data, stock),
            "mom_12_1": np.nan,
            "avg_money_20d_pre_rebalance": np.nan,
            "avg_market_cap_20d_pre_rebalance": np.nan,
            "listing_trade_days": np.nan,
        }

        one_price = price_df[(price_df["code"] == stock) & (price_df["time"] <= pd.Timestamp(factor_date))].sort_values("time").copy()
        one_valuation = valuation_df[(valuation_df["code"] == stock) & (valuation_df["day"] <= pd.Timestamp(factor_date))].sort_values("day").copy()

        if len(one_price) >= g.max_price_history_count:
            close_series = pd.to_numeric(one_price["close"], errors="coerce").reset_index(drop=True)
            money_series = pd.to_numeric(one_price["money"], errors="coerce").reset_index(drop=True)
            payload["mom_12_1"] = calc_skip_month_momentum(close_series, 240, 21)
            trailing_money = money_series.tail(g.pool_history_count).dropna()
            if len(trailing_money) >= g.pool_history_count:
                payload["avg_money_20d_pre_rebalance"] = float(trailing_money.mean())
            payload["listing_trade_days"] = len(one_price)

        if len(one_valuation) >= g.pool_history_count:
            mcap_series = pd.to_numeric(one_valuation["market_cap"], errors="coerce").dropna().tail(g.pool_history_count)
            if len(mcap_series) >= g.pool_history_count:
                payload["avg_market_cap_20d_pre_rebalance"] = float(mcap_series.mean())

        rows.append(payload)

    out = pd.DataFrame(rows).sort_values("code").reset_index(drop=True)
    out["price_ready"] = (
        out["mom_12_1"].notna()
        & out["avg_money_20d_pre_rebalance"].notna()
        & out["avg_market_cap_20d_pre_rebalance"].notna()
        & (pd.to_numeric(out["listing_trade_days"], errors="coerce") >= g.min_listing_trade_days)
    ).astype(int)
    liq_flag, mcap_flag, pool_flag = build_pool_flags(out)
    out["liquidity_top_60_flag"] = liq_flag
    out["market_cap_top_60_flag"] = mcap_flag
    out["pool_flag"] = pool_flag
    return out


def build_candidate_pool(feature_df):
    work_df = feature_df.copy()
    pool_df = work_df[work_df["pool_flag"] == 1].copy()
    if pool_df.empty:
        pool_df = work_df[work_df["price_ready"] == 1].copy()
    if pool_df.empty:
        return pd.DataFrame()

    pool_df["momentum_score"] = score_series(pool_df["mom_12_1"], "larger_better")
    pool_df = pool_df.dropna(subset=["momentum_score"]).copy()
    return pool_df.sort_values(["momentum_score", "code"], ascending=[False, True]).reset_index(drop=True)


def select_holdings_by_variant(pool_df, fundamental_rank_map):
    if g.strategy_variant == "direct_mom12_top6":
        return pool_df.head(6).copy()

    stage1_df = pool_df.head(10).copy()
    if stage1_df.empty:
        return pd.DataFrame()

    stage1_df["fundamental_rank"] = stage1_df["code"].map(fundamental_rank_map)
    stage1_df["fundamental_rank"] = pd.to_numeric(stage1_df["fundamental_rank"], errors="coerce").fillna(999.0)
    stage1_df = stage1_df.sort_values(
        ["fundamental_rank", "momentum_score", "code"],
        ascending=[True, False, True],
    ).copy()

    hold_count = 6
    if g.strategy_variant == "mom12_top10_then_fundamental_top4":
        hold_count = 4
    return stage1_df.head(hold_count).copy()


def build_candidate_preview(df):
    if df is None or len(df) == 0:
        return "[]"
    preview = []
    for _, row in df.iterrows():
        preview.append(
            "%s:m12=%.4f,score=%.4f,frank=%s"
            % (
                row["code"],
                safe_number(row.get("mom_12_1"), np.nan),
                safe_number(row.get("momentum_score"), np.nan),
                str(int(row["fundamental_rank"])) if "fundamental_rank" in row and pd.notna(row["fundamental_rank"]) else "",
            )
        )
    return "[" + " ; ".join(preview) + "]"


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


def get_tradable_stocks(stocks):
    current_data = get_current_data()
    tradable = []
    for stock in stocks:
        try:
            data = current_data[stock]
            if data.paused or data.is_st:
                continue
            if "ST" in data.name or "*" in data.name or "閫€" in data.name:
                continue
            tradable.append(stock)
        except Exception:
            continue
    return tradable


def execute_target_weights(context, long_list, target_weight):
    target_value_map = {stock: context.portfolio.total_value * target_weight for stock in long_list}
    current_positions = list(context.portfolio.positions.keys())

    for stock in current_positions:
        if stock not in long_list:
            try:
                order_target_value(stock, 0)
            except Exception as exc:
                log.info("sell failed %s %s" % (stock, str(exc)))

    for stock in long_list:
        try:
            order_target_value(stock, target_value_map[stock])
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


def safe_number(value, fallback=np.nan):
    try:
        if value is None or pd.isna(value):
            return fallback
        return float(value)
    except Exception:
        return fallback


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
