from jqdata import *
from datetime import datetime
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

    # Quarterly rebalance dates inherited from the local phase-1 panel.
    # 2021-05-31 start is handled as an initial build even though the next formal
    # quarterly momentum review point begins at 2021-09-01.
    g.formal_rebalance_dates = {
        "2021-09-01",
        "2021-11-01",
        "2022-05-05",
        "2022-09-01",
        "2022-11-01",
        "2023-05-04",
        "2023-09-01",
        "2023-11-01",
        "2024-05-06",
        "2024-09-02",
        "2024-11-01",
        "2025-05-06",
        "2025-09-01",
        "2025-11-03",
        "2026-05-06",
    }

    g.group_count = 5
    g.hold_bucket = 5
    g.momentum_factor = "mom_12_1"
    g.momentum_direction = "larger_better"
    g.min_listing_trade_days = 240
    g.price_history_count = 241
    g.pool_history_count = 20
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

    if current_date_str in g.formal_rebalance_dates:
        should_rebalance = True
        rebalance_reason = "formal_quarterly_date"
    elif len(context.portfolio.positions) == 0:
        should_rebalance = True
        rebalance_reason = "initial_build"

    if not should_rebalance:
        return

    success = do_rebalance(context, rebalance_reason)
    if success:
        g.executed_rebalance_dates.add(current_date_str)


def do_rebalance(context, rebalance_reason):
    factor_date = get_previous_trade_date(context)
    tradable = get_tradable_stocks(context, g.bank_stocks)
    if len(tradable) < g.group_count:
        log.info("Tradable bank count is too small: %d" % len(tradable))
        return False

    score_df = build_score_frame(context, tradable, factor_date)
    if score_df.empty:
        log.info("Score frame is empty on %s" % str(factor_date))
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
    pool_summary = build_pool_summary(score_df)
    diagnostic_summary = build_diagnostic_summary(score_df)
    bottom_preview = build_score_preview(
        score_df.tail(10).sort_values(["final_score", "code"], ascending=[True, True])
    )

    if g.debug:
        log.info("========== V4 quarterly momentum rebalance ==========")
        log.info(
            "current_date=%s factor_date=%s reason=%s factor=%s direction=%s"
            % (
                str(to_date(context.current_dt)),
                str(factor_date),
                rebalance_reason,
                g.momentum_factor,
                g.momentum_direction,
            )
        )
        log.info(
            "candidate_count=%d selected_count=%d long_list=%s"
            % (len(score_df), len(long_list), str(long_list))
        )
        log.info("pool_summary=%s" % pool_summary)
        log.info("diagnostic_summary=%s" % diagnostic_summary)
        log.info("top_score_preview=%s" % build_score_preview(score_df.head(10)))
        log.info("long_score_preview=%s" % build_score_preview(long_df.head(20)))
        log.info("bottom_score_preview=%s" % bottom_preview)

    execute_target_weights(context, long_list, target_weight)
    g.latest_rebalance_log = {
        "current_date": str(to_date(context.current_dt)),
        "factor_date": str(factor_date),
        "rebalance_reason": rebalance_reason,
        "candidate_count": int(len(score_df)),
        "selected_count": int(len(long_list)),
        "pool_summary": pool_summary,
        "diagnostic_summary": diagnostic_summary,
        "top_score_preview": build_score_preview(score_df.head(10)),
        "long_score_preview": build_score_preview(long_df.head(20)),
        "bottom_score_preview": bottom_preview,
        "selected_codes": "|".join(long_list),
    }
    return True


def build_score_frame(context, stocks, factor_date):
    feature_df = build_feature_frame(stocks, factor_date)
    if feature_df.empty:
        return pd.DataFrame()

    feature_df = feature_df[feature_df["pool_flag"] == 1].copy()
    if feature_df.empty:
        if g.debug:
            log.info("No stocks passed the double-top-80%% pool on %s" % str(factor_date))
        return pd.DataFrame()

    feature_df["final_score"] = score_series(
        feature_df[g.momentum_factor],
        g.momentum_direction,
    )
    feature_df["factor_count"] = feature_df["final_score"].notna().astype(int)
    feature_df = feature_df.dropna(subset=["final_score"]).copy()

    if g.debug:
        log.info(
            "feature coverage on %s: total=%d in_pool=%d scored=%d"
            % (
                str(factor_date),
                len(stocks),
                int(feature_df["pool_flag"].sum()) if "pool_flag" in feature_df.columns else 0,
                len(feature_df),
            )
        )
    return feature_df


def build_feature_frame(stocks, factor_date):
    result = pd.DataFrame(index=stocks)
    result["code"] = result.index

    price_df = fetch_price_history(stocks, factor_date, g.price_history_count)
    if price_df.empty:
        return pd.DataFrame()

    valuation_df = fetch_market_cap_history(stocks, factor_date, g.pool_history_count)
    current_data = get_current_data()

    rows = []
    for stock in stocks:
        payload = {
            "code": stock,
            "display_name": "",
            "mom_12_1": np.nan,
            "avg_money_20d": np.nan,
            "avg_market_cap_20d": np.nan,
            "listing_trade_days": np.nan,
        }

        try:
            payload["display_name"] = current_data[stock].name
        except Exception:
            payload["display_name"] = ""

        one_price = price_df[price_df["code"] == stock].sort_values("time").copy()
        one_valuation = valuation_df[valuation_df["code"] == stock].sort_values("day").copy()

        if len(one_price) >= g.price_history_count:
            close_series = pd.to_numeric(one_price["close"], errors="coerce").reset_index(drop=True)
            money_series = pd.to_numeric(one_price["money"], errors="coerce").reset_index(drop=True)
            if close_series.notna().sum() >= g.price_history_count:
                base_close = close_series.iloc[-240]
                skip_close = close_series.iloc[-21]
                if pd.notna(base_close) and abs(float(base_close)) > 1e-12 and pd.notna(skip_close):
                    payload["mom_12_1"] = float(skip_close) / float(base_close) - 1.0
            trailing_money = money_series.tail(g.pool_history_count).dropna()
            if len(trailing_money) >= g.pool_history_count:
                payload["avg_money_20d"] = float(trailing_money.mean())
            payload["listing_trade_days"] = len(one_price)

        if len(one_valuation) > 0:
            market_cap_series = pd.to_numeric(one_valuation["market_cap"], errors="coerce").dropna()
            if len(market_cap_series) >= g.pool_history_count:
                payload["avg_market_cap_20d"] = float(market_cap_series.tail(g.pool_history_count).mean())

        rows.append(payload)

    out = pd.DataFrame(rows).sort_values("code").reset_index(drop=True)
    out["price_ready"] = (
        out["mom_12_1"].notna()
        & out["avg_money_20d"].notna()
        & out["avg_market_cap_20d"].notna()
        & (pd.to_numeric(out["listing_trade_days"], errors="coerce") >= g.min_listing_trade_days)
    ).astype(int)

    liq_flag, mcap_flag, pool_flag = build_pool_flags(out)
    out["liquidity_top_80_flag"] = liq_flag
    out["market_cap_top_80_flag"] = mcap_flag
    out["pool_flag"] = pool_flag
    if g.debug:
        log.info(
            "raw_feature_summary on %s: total=%d ready=%d liq80=%d mcap80=%d pool=%d"
            % (
                str(factor_date),
                len(out),
                int(out["price_ready"].sum()),
                int(out["liquidity_top_80_flag"].sum()),
                int(out["market_cap_top_80_flag"].sum()),
                int(out["pool_flag"].sum()),
            )
        )
    return out


def build_pool_flags(df):
    liq_flag = pd.Series(index=df.index, data=0, dtype="int64")
    mcap_flag = pd.Series(index=df.index, data=0, dtype="int64")

    ready_liq = df["price_ready"].eq(1) & df["avg_money_20d"].notna()
    ready_mcap = df["price_ready"].eq(1) & df["avg_market_cap_20d"].notna()

    valid_liq = int(ready_liq.sum())
    valid_mcap = int(ready_mcap.sum())
    liq_keep = int(ceil(valid_liq * 0.8)) if valid_liq > 0 else 0
    mcap_keep = int(ceil(valid_mcap * 0.8)) if valid_mcap > 0 else 0

    if liq_keep > 0:
        liq_rank = df.loc[ready_liq, "avg_money_20d"].rank(method="first", ascending=False)
        liq_flag.loc[liq_rank.index] = (liq_rank <= liq_keep).astype(int)

    if mcap_keep > 0:
        mcap_rank = df.loc[ready_mcap, "avg_market_cap_20d"].rank(method="first", ascending=False)
        mcap_flag.loc[mcap_rank.index] = (mcap_rank <= mcap_keep).astype(int)

    pool_flag = ((liq_flag == 1) & (mcap_flag == 1) & df["price_ready"].eq(1)).astype(int)
    return liq_flag, mcap_flag, pool_flag


def fetch_price_history(stocks, factor_date, count):
    try:
        df = get_price(
            stocks,
            end_date=factor_date,
            count=count,
            frequency="daily",
            fields=["close", "money"],
            skip_paused=False,
            fq="pre",
            panel=False,
        )
    except Exception as exc:
        log.info("get_price batch failed on %s: %s" % (str(factor_date), str(exc)))
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


def fetch_market_cap_history(stocks, factor_date, count):
    try:
        df = get_fundamentals_continuously(
            query(
                valuation.code,
                valuation.market_cap,
            ).filter(valuation.code.in_(stocks)),
            end_date=factor_date,
            count=count,
            panel=False,
        )
    except Exception as exc:
        log.info("get_fundamentals_continuously failed on %s: %s" % (str(factor_date), str(exc)))
        return pd.DataFrame()

    if df is None or len(df) == 0:
        return pd.DataFrame()

    out = df.copy()
    if "day" not in out.columns and "date" in out.columns:
        out = out.rename(columns={"date": "day"})
    out["day"] = pd.to_datetime(out["day"])
    out["market_cap"] = pd.to_numeric(out["market_cap"], errors="coerce")
    return out[["day", "code", "market_cap"]].copy()


def get_tradable_stocks(context, stocks):
    current_data = get_current_data()
    tradable = []
    for stock in stocks:
        try:
            data = current_data[stock]
            if data.paused:
                continue
            if data.is_st:
                continue
            if "ST" in data.name or "*" in data.name or "退" in data.name:
                continue
            tradable.append(stock)
        except Exception:
            continue
    return tradable


def execute_target_weights(context, long_list, target_weight):
    target_value_map = {
        stock: context.portfolio.total_value * target_weight
        for stock in long_list
    }
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

    zscore = (clipped - mean_value) / std_value
    multiplier = 1.0 if direction == "larger_better" else -1.0
    return zscore * multiplier


def assign_groups(values, group_count):
    ranked = pd.Series(values).rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=ranked.index, dtype="float64")


def build_score_preview(df):
    if df is None or len(df) == 0:
        return "[]"

    preview = []
    for _, row in df.iterrows():
        preview.append(
            "%s:score=%.4f,liq=%.2f,mcap=%.2f"
            % (
                row["code"],
                float(row["final_score"]) if pd.notna(row["final_score"]) else float("nan"),
                float(row["avg_money_20d"]) if pd.notna(row["avg_money_20d"]) else float("nan"),
                float(row["avg_market_cap_20d"]) if pd.notna(row["avg_market_cap_20d"]) else float("nan"),
            )
        )
    return "[" + " ; ".join(preview) + "]"


def build_diagnostic_summary(df):
    if df is None or len(df) == 0:
        return "{}"
    summary = {
        "score_min": safe_round(df["final_score"].min()),
        "score_p20": safe_round(df["final_score"].quantile(0.2)),
        "score_p50": safe_round(df["final_score"].quantile(0.5)),
        "score_p80": safe_round(df["final_score"].quantile(0.8)),
        "score_max": safe_round(df["final_score"].max()),
        "mom_min": safe_round(df["mom_12_1"].min()),
        "mom_p50": safe_round(df["mom_12_1"].quantile(0.5)),
        "mom_max": safe_round(df["mom_12_1"].max()),
    }
    return str(summary)


def build_pool_summary(df):
    if df is None or len(df) == 0:
        return "{}"
    summary = {
        "liq_mean": safe_round(df["avg_money_20d"].mean()),
        "liq_median": safe_round(df["avg_money_20d"].median()),
        "mcap_mean": safe_round(df["avg_market_cap_20d"].mean()),
        "mcap_median": safe_round(df["avg_market_cap_20d"].median()),
    }
    return str(summary)


def log_position_snapshot(context):
    if not g.debug:
        return
    current_date = str(to_date(context.current_dt))
    positions = context.portfolio.positions
    if len(positions) == 0:
        log.info(
            "position_snapshot date=%s holdings=[] total_value=%.2f cash=%.2f"
            % (
                current_date,
                float(context.portfolio.total_value),
                float(context.portfolio.available_cash),
            )
        )
        return

    parts = []
    for stock in sorted(positions.keys()):
        pos = positions[stock]
        market_value = float(pos.price * pos.total_amount)
        weight = market_value / float(context.portfolio.total_value) if context.portfolio.total_value > 0 else np.nan
        parts.append(
            "%s:w=%.4f,amt=%s,price=%.2f,cost=%.2f,mv=%.2f"
            % (
                stock,
                weight,
                str(int(pos.total_amount)),
                float(pos.price),
                float(pos.avg_cost),
                market_value,
            )
        )
    log.info(
        "position_snapshot date=%s holding_count=%d total_value=%.2f cash=%.2f holdings=[%s]"
        % (
            current_date,
            len(parts),
            float(context.portfolio.total_value),
            float(context.portfolio.available_cash),
            " ; ".join(parts),
        )
    )
    if g.latest_rebalance_log is not None:
        log.info("latest_rebalance_log=%s" % str(g.latest_rebalance_log))


def get_previous_trade_date(context):
    try:
        return to_date(context.previous_date)
    except Exception:
        trade_days = get_trade_days(end_date=to_date(context.current_dt), count=2)
        if trade_days is None or len(trade_days) == 0:
            return to_date(context.current_dt)
        return to_date(trade_days[0])


def to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, "date"):
        return value.date()
    return pd.Timestamp(value).date()


def safe_round(value, digits=6):
    try:
        if value is None or pd.isna(value):
            return None
        return round(float(value), digits)
    except Exception:
        return None
