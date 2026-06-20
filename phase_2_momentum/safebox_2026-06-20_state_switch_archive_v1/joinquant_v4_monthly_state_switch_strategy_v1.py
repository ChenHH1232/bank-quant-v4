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

    g.group_count = 5
    g.hold_bucket = 5
    g.min_listing_trade_days = 240
    g.max_price_history_count = 270
    g.pool_history_count = 20
    g.pool_keep_ratio = 0.60
    g.executed_rebalance_dates = set()
    g.latest_rebalance_log = None
    g.debug = True

    # Deployable observable proxy for the state-switch research idea.
    # The original research `state_score_v2` used `cross_target_dispersion`,
    # which depends on next-period returns and therefore cannot be observed
    # inside a real backtest month. This JoinQuant version freezes the closest
    # observable approximation instead:
    # `cross_mcap_median + cross_mom6_positive_ratio - cross_money_median`.
    g.state_v2_component_stats = {
        "cross_mcap_median": {"mean": 4438.4252965278, "std": 1673.5288644883, "sign": 1.0},
        "cross_mom6_positive_ratio": {"mean": 0.6572365996, "std": 0.3424492823, "sign": 1.0},
        "cross_money_median": {"mean": 1174826962.91514, "std": 1587381940.7720375, "sign": -1.0},
    }
    # Frozen pre-2021 top-33% threshold for the observable proxy score.
    g.state_v2_high_threshold = 0.218674

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
    if len(tradable) < g.group_count:
        log.info("Tradable bank count is too small: %d" % len(tradable))
        return False

    feature_df = build_current_feature_snapshot(factor_date, tradable)
    if feature_df.empty:
        log.info("Current feature frame is empty on %s" % str(factor_date))
        return False

    state_info = compute_state_switch_info(feature_df)
    if state_info is None:
        log.info("State switch info is empty on %s" % str(factor_date))
        return False

    selected_spec = state_info["selected_spec"]
    score_df = build_score_frame(feature_df, selected_spec)
    if score_df.empty:
        if g.debug:
            log.info(
                "empty_score_diagnostic current_date=%s factor_date=%s selected_factor=%s"
                % (str(current_date), str(factor_date), selected_spec["factor_name"])
            )
            log.info("feature_snapshot_summary=%s" % str(build_feature_snapshot_summary(feature_df)))
            log.info("state_switch_summary=%s" % str(build_state_switch_log(state_info)))
            log.info("factor_component_summary=%s" % str(build_factor_component_summary(feature_df, selected_spec)))
            log.info("pool_preview=%s" % build_feature_preview(feature_df.head(12)))
        log.info("Score frame is empty after factor selection on %s" % str(factor_date))
        return False

    score_df = score_df.sort_values(["final_score", "code"], ascending=[False, True]).copy()
    score_df["bucket"] = assign_groups(score_df["final_score"], g.group_count)
    score_df = score_df.dropna(subset=["bucket"]).copy()
    score_df["bucket"] = score_df["bucket"].astype(int)

    long_df = score_df[score_df["bucket"] == g.hold_bucket].copy()
    if long_df.empty:
        log.info("No stocks entered top bucket on %s" % str(factor_date))
        return False

    long_list = long_df["code"].tolist()
    target_weight = 1.0 / float(len(long_list))

    if g.debug:
        log.info("========== V4 monthly state-switch rebalance ==========")
        log.info(
            "current_date=%s factor_date=%s reason=%s selected_factor=%s"
            % (str(current_date), str(factor_date), rebalance_reason, selected_spec["factor_name"])
        )
        log.info("state_switch_summary=%s" % str(build_state_switch_log(state_info)))
        log.info(
            "selection_log=%s"
            % str(
                {
                    "selection_mode": "frozen_observable_state_proxy_top33_switch",
                    "selected_factor": selected_spec["factor_name"],
                    "selected_components": build_component_label(selected_spec),
                    "strict_pool_count": int((feature_df["pool_flag"] == 1).sum()),
                    "price_ready_count": int((feature_df["price_ready"] == 1).sum()),
                    "candidate_count": int(len(score_df)),
                }
            )
        )
        log.info(
            "candidate_count=%d selected_count=%d long_list=%s"
            % (len(score_df), len(long_list), str(long_list))
        )
        log.info("top_score_preview=%s" % build_score_preview(score_df.head(10)))
        log.info("long_score_preview=%s" % build_score_preview(long_df.head(20)))

    execute_target_weights(context, long_list, target_weight)
    g.latest_rebalance_log = {
        "current_date": str(current_date),
        "factor_date": str(factor_date),
        "rebalance_reason": rebalance_reason,
        "selected_factor": selected_spec["factor_name"],
        "selected_components": build_component_label(selected_spec),
        "selected_codes": "|".join(long_list),
        "state_score_v2": safe_round(state_info["state_score_v2"], 6),
        "state_bucket": state_info["state_bucket"],
    }
    return True


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


def compute_state_switch_info(feature_df):
    pool_df = feature_df[feature_df["pool_flag"] == 1].copy()
    if pool_df.empty:
        pool_df = feature_df[feature_df["price_ready"] == 1].copy()
    if pool_df.empty or len(pool_df) < g.group_count:
        return None

    target_values = pd.to_numeric(pool_df["mom_6_1"], errors="coerce").dropna()
    money_values = pd.to_numeric(pool_df["avg_money_20d_pre_rebalance"], errors="coerce").dropna()
    mcap_values = pd.to_numeric(pool_df["avg_market_cap_20d_pre_rebalance"], errors="coerce").dropna()
    if len(target_values) < g.group_count or len(money_values) < g.group_count or len(mcap_values) < g.group_count:
        return None

    proxy_values = {
        "cross_mcap_median": float(mcap_values.median()),
        "cross_mom6_positive_ratio": float((target_values > 0).mean()),
        "cross_money_median": float(money_values.median()),
    }

    component_z = {}
    signed_parts = []
    for component_name, stats in g.state_v2_component_stats.items():
        current_value = proxy_values[component_name]
        std_value = float(stats["std"])
        if pd.isna(current_value) or pd.isna(std_value) or std_value <= 1e-12:
            return None
        z_value = (float(current_value) - float(stats["mean"])) / std_value
        component_z[component_name] = z_value
        signed_parts.append(z_value * float(stats["sign"]))

    state_score_v2 = float(sum(signed_parts) / len(signed_parts))
    is_high_state = state_score_v2 >= float(g.state_v2_high_threshold)
    selected_spec = (
        {"factor_name": "mom_6_1", "components": [("mom_6_1", 1.0)], "source": "frozen_observable_state_proxy_top33"}
        if is_high_state
        else {"factor_name": "mom_12_1", "components": [("mom_12_1", 1.0)], "source": "frozen_observable_state_proxy_top33"}
    )
    return {
        "selected_spec": selected_spec,
        "state_bucket": "high_use_mom6" if is_high_state else "non_high_use_mom12",
        "state_score_v2": state_score_v2,
        "state_threshold": float(g.state_v2_high_threshold),
        "proxy_values": proxy_values,
        "component_z": component_z,
        "pool_count": int(len(pool_df)),
    }


def build_score_frame(feature_df, selected_spec):
    work_df = feature_df.copy()
    pool_df = work_df[work_df["pool_flag"] == 1].copy()
    if pool_df.empty:
        pool_df = work_df[work_df["price_ready"] == 1].copy()
    if pool_df.empty:
        return pd.DataFrame()

    parts = []
    total_weight = 0.0
    for factor_name, weight in selected_spec["components"]:
        z_col = "z__%s" % factor_name
        pool_df[z_col] = score_series(pool_df[factor_name], "larger_better")
        parts.append(pd.to_numeric(pool_df[z_col], errors="coerce") * float(weight))
        total_weight += abs(float(weight))

    if len(parts) == 0 or total_weight <= 0:
        return pd.DataFrame()

    final_score = parts[0]
    for idx in range(1, len(parts)):
        final_score = final_score + parts[idx]
    pool_df["final_score"] = final_score / total_weight
    pool_df = pool_df.dropna(subset=["final_score"]).copy()
    return pool_df


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


def assign_groups(values, group_count):
    ranked = pd.Series(values).rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=ranked.index, dtype="float64")


def build_feature_snapshot_summary(feature_df):
    if feature_df is None or len(feature_df) == 0:
        return {"rows": 0}
    summary = {
        "rows": int(len(feature_df)),
        "price_ready_count": int(feature_df["price_ready"].sum()) if "price_ready" in feature_df.columns else 0,
        "pool_flag_count": int(feature_df["pool_flag"].sum()) if "pool_flag" in feature_df.columns else 0,
        "liq_top_60_count": int(feature_df["liquidity_top_60_flag"].sum()) if "liquidity_top_60_flag" in feature_df.columns else 0,
        "mcap_top_60_count": int(feature_df["market_cap_top_60_flag"].sum()) if "market_cap_top_60_flag" in feature_df.columns else 0,
        "mom_3_1_non_null": int(feature_df["mom_3_1"].notna().sum()) if "mom_3_1" in feature_df.columns else 0,
        "mom_6_1_non_null": int(feature_df["mom_6_1"].notna().sum()) if "mom_6_1" in feature_df.columns else 0,
        "mom_12_1_non_null": int(feature_df["mom_12_1"].notna().sum()) if "mom_12_1" in feature_df.columns else 0,
        "avg_money_non_null": int(feature_df["avg_money_20d_pre_rebalance"].notna().sum()) if "avg_money_20d_pre_rebalance" in feature_df.columns else 0,
        "avg_mcap_non_null": int(feature_df["avg_market_cap_20d_pre_rebalance"].notna().sum()) if "avg_market_cap_20d_pre_rebalance" in feature_df.columns else 0,
    }
    return summary


def build_factor_component_summary(feature_df, selected_spec):
    summary = {"selected_factor": selected_spec["factor_name"], "components": build_component_label(selected_spec)}
    if feature_df is None or len(feature_df) == 0:
        return summary
    for factor_name, _ in selected_spec["components"]:
        factor_values = pd.to_numeric(feature_df[factor_name], errors="coerce")
        summary[factor_name + "_non_null"] = int(factor_values.notna().sum())
        summary[factor_name + "_min"] = safe_round(factor_values.min())
        summary[factor_name + "_median"] = safe_round(factor_values.median())
        summary[factor_name + "_max"] = safe_round(factor_values.max())
    return summary


def build_state_switch_log(state_info):
    return {
        "state_score_v2": safe_round(state_info["state_score_v2"], 6),
        "state_threshold": safe_round(state_info["state_threshold"], 6),
        "state_bucket": state_info["state_bucket"],
        "pool_count": int(state_info["pool_count"]),
        "proxy_values": {key: safe_round(value, 6) for key, value in state_info["proxy_values"].items()},
        "component_z": {key: safe_round(value, 6) for key, value in state_info["component_z"].items()},
    }


def build_feature_preview(df):
    if df is None or len(df) == 0:
        return "[]"
    preview = []
    for _, row in df.iterrows():
        preview.append(
            "%s:ready=%s,pool=%s,m3=%s,m6=%s,m12=%s"
            % (
                row["code"],
                str(int(row["price_ready"])) if pd.notna(row["price_ready"]) else "nan",
                str(int(row["pool_flag"])) if pd.notna(row["pool_flag"]) else "nan",
                str(safe_round(row["mom_3_1"], 4)),
                str(safe_round(row["mom_6_1"], 4)),
                str(safe_round(row["mom_12_1"], 4)),
            )
        )
    return "[" + " ; ".join(preview) + "]"


def build_score_preview(df):
    if df is None or len(df) == 0:
        return "[]"
    preview = []
    for _, row in df.iterrows():
        preview.append(
            "%s:score=%.4f,m3=%.4f,m6=%.4f,m12=%.4f"
            % (
                row["code"],
                safe_number(row.get("final_score"), np.nan),
                safe_number(row.get("mom_3_1"), np.nan),
                safe_number(row.get("mom_6_1"), np.nan),
                safe_number(row.get("mom_12_1"), np.nan),
            )
        )
    return "[" + " ; ".join(preview) + "]"


def build_component_label(spec):
    parts = []
    for factor_name, weight in spec["components"]:
        parts.append("%s*%s" % (str(weight), factor_name))
    return " + ".join(parts)


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
