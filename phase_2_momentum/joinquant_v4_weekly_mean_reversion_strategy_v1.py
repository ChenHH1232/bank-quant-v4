from jqdata import *
from datetime import date, datetime
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
        "601825.XSHG", "601838.XSHG", "601860.XSHG", "601916.XSHG",
        "601939.XSHG", "601963.XSHG", "601988.XSHG", "601997.XSHG",
        "601998.XSHG", "603323.XSHG",
    ]

    g.select_count = 5
    g.min_listing_trade_days = 60
    g.history_count = 25
    g.pool_history_count = 20
    g.pool_keep_ratio = 0.60
    g.executed_rebalance_dates = set()
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
    current_date_str = current_date.strftime("%Y-%m-%d")
    if current_date_str in g.executed_rebalance_dates:
        return

    should_rebalance = False
    rebalance_reason = ""
    if len(context.portfolio.positions) == 0:
        should_rebalance = True
        rebalance_reason = "initial_build"
    elif is_first_trade_day_of_week(current_date):
        should_rebalance = True
        rebalance_reason = "weekly_first_trade_day"

    if not should_rebalance:
        return

    success = do_rebalance(context, rebalance_reason)
    if success:
        g.executed_rebalance_dates.add(current_date_str)


def do_rebalance(context, rebalance_reason):
    current_date = to_date(context.current_dt)
    factor_date = get_previous_trade_date(context)
    tradable = get_tradable_stocks(g.bank_stocks)
    if len(tradable) < g.select_count:
        log.info("Tradable bank count is too small: %d" % len(tradable))
        return False

    feature_df = build_current_feature_snapshot(factor_date, tradable)
    if feature_df.empty:
        log.info("Current feature frame is empty on %s" % str(factor_date))
        return False

    score_df = build_score_frame(feature_df)
    if score_df.empty:
        if g.debug:
            log.info("empty_score_diagnostic current_date=%s factor_date=%s" % (str(current_date), str(factor_date)))
            log.info("feature_snapshot_summary=%s" % str(build_feature_snapshot_summary(feature_df)))
            log.info("pool_preview=%s" % build_feature_preview(feature_df.head(12)))
        log.info("Score frame is empty after factor selection on %s" % str(factor_date))
        return False

    long_df = score_df.sort_values(["final_score", "code"], ascending=[True, True]).head(g.select_count).copy()
    long_list = long_df["code"].tolist()
    if len(long_list) == 0:
        log.info("No stocks selected on %s" % str(factor_date))
        return False

    target_weight = 1.0 / float(len(long_list))

    if g.debug:
        log.info("========== V4 weekly mean reversion rebalance ==========")
        log.info(
            "current_date=%s factor_date=%s reason=%s"
            % (str(current_date), str(factor_date), rebalance_reason)
        )
        log.info(
            "selection_log=%s"
            % str(
                {
                    "signal_name": "rev5_abnvol",
                    "selection_mode": "weekly_mean_reversion_raw",
                    "strict_pool_count": int((feature_df["pool_flag"] == 1).sum()),
                    "price_ready_count": int((feature_df["price_ready"] == 1).sum()),
                    "candidate_count": int(len(score_df)),
                    "selected_count": int(len(long_list)),
                }
            )
        )
        log.info("top_score_preview=%s" % build_score_preview(score_df.head(10)))
        log.info("long_score_preview=%s" % build_score_preview(long_df.head(20)))

    execute_target_weights(context, long_list, target_weight)
    g.latest_rebalance_log = {
        "current_date": str(current_date),
        "factor_date": str(factor_date),
        "rebalance_reason": rebalance_reason,
        "selected_signal": "rev5_abnvol",
        "selected_codes": "|".join(long_list),
    }
    return True


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
    liq_flag, mcap_flag, pool_flag = build_pool_flags(out)
    out["liquidity_top_60_flag"] = liq_flag
    out["market_cap_top_60_flag"] = mcap_flag
    out["pool_flag"] = pool_flag
    out["rev5_abnvol"] = (
        -0.7 * pd.to_numeric(out["rev_5d"], errors="coerce")
        + 0.3 * pd.to_numeric(out["abnormal_volume_ratio"], errors="coerce")
    )
    return out


def build_score_frame(feature_df):
    work_df = feature_df.copy()
    pool_df = work_df[work_df["pool_flag"] == 1].copy()
    if pool_df.empty:
        pool_df = work_df[work_df["price_ready"] == 1].copy()
    if pool_df.empty:
        return pd.DataFrame()

    pool_df["final_score"] = pd.to_numeric(pool_df["rev5_abnvol"], errors="coerce")
    pool_df = pool_df.dropna(subset=["final_score"]).copy()
    return pool_df


def build_pool_flags(df):
    liq_flag = pd.Series(index=df.index, data=0, dtype="int64")
    mcap_flag = pd.Series(index=df.index, data=0, dtype="int64")

    ready_liq = df["price_ready"].eq(1) & df["avg_money_20d"].notna()
    ready_mcap = df["price_ready"].eq(1) & df["avg_market_cap_20d"].notna()
    valid_liq = int(ready_liq.sum())
    valid_mcap = int(ready_mcap.sum())
    liq_keep = int(ceil(valid_liq * g.pool_keep_ratio)) if valid_liq > 0 else 0
    mcap_keep = int(ceil(valid_mcap * g.pool_keep_ratio)) if valid_mcap > 0 else 0

    if liq_keep > 0:
        liq_rank = df.loc[ready_liq, "avg_money_20d"].rank(method="first", ascending=False)
        liq_flag.loc[liq_rank.index] = (liq_rank <= liq_keep).astype(int)

    if mcap_keep > 0:
        mcap_rank = df.loc[ready_mcap, "avg_market_cap_20d"].rank(method="first", ascending=False)
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
            if "ST" in data.name or "*" in data.name or "退" in data.name:
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


def build_feature_snapshot_summary(feature_df):
    if feature_df is None or len(feature_df) == 0:
        return {"rows": 0}
    return {
        "rows": int(len(feature_df)),
        "price_ready_count": int(feature_df["price_ready"].sum()) if "price_ready" in feature_df.columns else 0,
        "pool_flag_count": int(feature_df["pool_flag"].sum()) if "pool_flag" in feature_df.columns else 0,
        "liq_top_60_count": int(feature_df["liquidity_top_60_flag"].sum()) if "liquidity_top_60_flag" in feature_df.columns else 0,
        "mcap_top_60_count": int(feature_df["market_cap_top_60_flag"].sum()) if "market_cap_top_60_flag" in feature_df.columns else 0,
        "rev_5d_non_null": int(feature_df["rev_5d"].notna().sum()) if "rev_5d" in feature_df.columns else 0,
        "abnormal_volume_non_null": int(feature_df["abnormal_volume_ratio"].notna().sum()) if "abnormal_volume_ratio" in feature_df.columns else 0,
        "close_to_ma20_non_null": int(feature_df["close_to_ma20"].notna().sum()) if "close_to_ma20" in feature_df.columns else 0,
    }


def build_feature_preview(df):
    if df is None or len(df) == 0:
        return "[]"
    preview = []
    for _, row in df.iterrows():
        preview.append(
            "%s:ready=%s,pool=%s,rev5=%s,abnvol=%s,score=%s"
            % (
                row["code"],
                str(int(row["price_ready"])) if pd.notna(row["price_ready"]) else "nan",
                str(int(row["pool_flag"])) if pd.notna(row["pool_flag"]) else "nan",
                str(safe_round(row["rev_5d"], 4)),
                str(safe_round(row["abnormal_volume_ratio"], 4)),
                str(safe_round(row["rev5_abnvol"], 4)),
            )
        )
    return "[" + " ; ".join(preview) + "]"


def build_score_preview(df):
    if df is None or len(df) == 0:
        return "[]"
    preview = []
    for _, row in df.iterrows():
        preview.append(
            "%s:score=%.4f,rev5=%.4f,abnvol=%.4f,ma20=%.4f"
            % (
                row["code"],
                safe_number(row.get("final_score"), np.nan),
                safe_number(row.get("rev_5d"), np.nan),
                safe_number(row.get("abnormal_volume_ratio"), np.nan),
                safe_number(row.get("close_to_ma20"), np.nan),
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


def is_first_trade_day_of_week(current_date):
    weekday = current_date.weekday()
    week_start = current_date - pd.Timedelta(days=weekday)
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


def safe_number(value, fallback=np.nan):
    try:
        if value is None or pd.isna(value):
            return fallback
        return float(value)
    except Exception:
        return fallback


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
