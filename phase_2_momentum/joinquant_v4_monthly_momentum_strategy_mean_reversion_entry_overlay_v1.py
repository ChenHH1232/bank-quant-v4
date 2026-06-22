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
    # 12-1 momentum needs roughly 240 trading days lookback plus a 21-day skip
    # window, so keep a larger buffer for early backtest dates.
    g.max_price_history_count = 270
    g.pool_history_count = 20
    g.pool_keep_ratio = 0.60
    g.executed_rebalance_dates = set()
    g.latest_rebalance_log = None
    g.debug = True
    g.pending_entry = None

    # Offline annual factor plan from local research.
    g.annual_factor_plan = [
        {"effective_date": "2021-05-31", "factor_name": "mom_12_1", "components": [("mom_12_1", 1.0)], "source": "offline_minimal_bootstrap"},
        {"effective_date": "2022-05-05", "factor_name": "mom_12_1", "components": [("mom_12_1", 1.0)], "source": "offline_minimal_bootstrap"},
        {"effective_date": "2023-05-04", "factor_name": "combo_631_balanced", "components": [("mom_3_1", 0.2), ("mom_6_1", 0.5), ("mom_12_1", 0.3)], "source": "offline_minimal_bootstrap"},
        {"effective_date": "2024-05-06", "factor_name": "combo_631_balanced", "components": [("mom_3_1", 0.2), ("mom_6_1", 0.5), ("mom_12_1", 0.3)], "source": "offline_minimal_bootstrap"},
        {"effective_date": "2025-05-06", "factor_name": "mom_12_1", "components": [("mom_12_1", 1.0)], "source": "offline_minimal_bootstrap"},
        {"effective_date": "2026-05-06", "factor_name": "mom_12_1", "components": [("mom_12_1", 1.0)], "source": "offline_minimal_bootstrap"},
    ]

    # Entry overlay switchboard:
    # - 'baseline_full_entry'
    # - 'split_50_50_time'
    # - 'split_50_50_reversion'
    g.entry_overlay_mode = "baseline_full_entry"
    g.entry_signal_name = "rev_5d"      # 'rev_5d' or 'rev5_abnvol'
    g.entry_threshold_label = "q40"     # 'q20' / 'q30' / 'q40'
    g.entry_initial_ratio = 0.50
    g.entry_search_trade_days = 20
    g.entry_min_listing_trade_days = 60
    g.entry_price_history_count = 25
    g.entry_pool_history_count = 20
    g.entry_trigger_library = build_entry_trigger_library()

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
    run_daily(maybe_complete_pending_entry, time="09:45")
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

    selected_spec = get_active_factor_spec(current_date)
    if selected_spec is None:
        log.info("No active factor plan matched on %s" % str(current_date))
        return False

    score_df = build_score_frame(feature_df, selected_spec)
    if score_df.empty:
        if g.debug:
            log.info(
                "empty_score_diagnostic current_date=%s factor_date=%s selected_factor=%s"
                % (str(current_date), str(factor_date), selected_spec["factor_name"])
            )
            log.info("feature_snapshot_summary=%s" % str(build_feature_snapshot_summary(feature_df)))
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
        log.info("========== V4 monthly momentum rebalance ==========")
        log.info(
            "current_date=%s factor_date=%s reason=%s selected_factor=%s"
            % (str(current_date), str(factor_date), rebalance_reason, selected_spec["factor_name"])
        )
        log.info(
            "selection_log=%s"
            % str(
                {
                    "factor_refresh_date": selected_spec["effective_date"],
                    "selected_factor": selected_spec["factor_name"],
                    "selected_components": build_component_label(selected_spec),
                    "selection_source": selected_spec["source"],
                    "selection_mode": "offline_annual_factor_plan_raw",
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

    entry_threshold_value = get_entry_trigger_threshold(get_effective_plan_id(current_date))

    if g.debug:
        log.info("entry_overlay_mode=%s signal=%s threshold_label=%s threshold_value=%s" % (
            str(g.entry_overlay_mode),
            str(g.entry_signal_name),
            str(g.entry_threshold_label),
            str(safe_round(entry_threshold_value, 6)),
        ))

    apply_entry_overlay(context, current_date, factor_date, long_list, target_weight)
    g.latest_rebalance_log = {
        "current_date": str(current_date),
        "factor_date": str(factor_date),
        "rebalance_reason": rebalance_reason,
        "selected_factor": selected_spec["factor_name"],
        "selected_components": build_component_label(selected_spec),
        "selected_codes": "|".join(long_list),
        "entry_overlay_mode": str(g.entry_overlay_mode),
        "entry_signal_name": str(g.entry_signal_name),
        "entry_threshold_label": str(g.entry_threshold_label),
        "entry_threshold_value": safe_round(entry_threshold_value, 6),
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
        payload = {
            "code": stock,
            "display_name": safe_name(current_data, stock),
            "mom_3_1": np.nan,
            "mom_6_1": np.nan,
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
            payload["mom_3_1"] = calc_skip_month_momentum(close_series, 63, 21)
            payload["mom_6_1"] = calc_skip_month_momentum(close_series, 126, 21)
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


def get_active_factor_spec(current_date):
    active_spec = None
    for spec in g.annual_factor_plan:
        effective_date = pd.Timestamp(spec["effective_date"]).date()
        if effective_date <= current_date:
            active_spec = spec
    if active_spec is None and len(g.annual_factor_plan) > 0:
        return g.annual_factor_plan[0]
    return active_spec


def get_effective_plan_id(current_date):
    selected_spec = get_active_factor_spec(current_date)
    if selected_spec is None:
        return None
    effective_date = str(selected_spec.get("effective_date", ""))
    plan_map = {
        "2021-05-31": "annual_01",
        "2022-05-05": "annual_02",
        "2023-05-04": "annual_03",
        "2024-05-06": "annual_04",
        "2025-05-06": "annual_05",
        "2026-05-06": "annual_05",
    }
    return plan_map.get(effective_date, "annual_05")


def build_entry_trigger_library():
    return {
        "annual_01": {
            "rev5_abnvol": {"q20": 0.213381, "q30": 0.234595, "q40": 0.254403},
            "rev_5d": {"q20": -0.018480, "q30": -0.009956, "q40": -0.004191},
        },
        "annual_02": {
            "rev5_abnvol": {"q20": 0.216620, "q30": 0.237499, "q40": 0.257099},
            "rev_5d": {"q20": -0.020081, "q30": -0.011105, "q40": -0.004726},
        },
        "annual_03": {
            "rev5_abnvol": {"q20": 0.219817, "q30": 0.240178, "q40": 0.259340},
            "rev_5d": {"q20": -0.021312, "q30": -0.011999, "q40": -0.005177},
        },
        "annual_04": {
            "rev5_abnvol": {"q20": 0.222216, "q30": 0.242599, "q40": 0.262001},
            "rev_5d": {"q20": -0.023015, "q30": -0.013385, "q40": -0.005855},
        },
        "annual_05": {
            "rev5_abnvol": {"q20": 0.223340, "q30": 0.243518, "q40": 0.263161},
            "rev_5d": {"q20": -0.023674, "q30": -0.014309, "q40": -0.006524},
        },
    }


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
            if "ST" in data.name or "*" in data.name or "退" in data.name:
                continue
            tradable.append(stock)
        except Exception:
            continue
    return tradable


def apply_entry_overlay(context, current_date, factor_date, long_list, target_weight):
    mode = str(getattr(g, "entry_overlay_mode", "baseline_full_entry"))
    if mode == "baseline_full_entry":
        g.pending_entry = None
        execute_target_weights(context, long_list, target_weight)
        return

    initial_ratio = safe_float(getattr(g, "entry_initial_ratio", 0.5), 0.5)
    initial_ratio = min(max(initial_ratio, 0.0), 1.0)
    execute_target_ratio(context, long_list, initial_ratio)

    plan_id = get_effective_plan_id(current_date)
    threshold_value = get_entry_trigger_threshold(plan_id)
    initial_signal = compute_entry_signal_snapshot(factor_date, long_list)
    g.pending_entry = {
        "plan_id": plan_id,
        "mode": mode,
        "activation_date": str(current_date),
        "activation_trade_date": str(factor_date),
        "target_codes": list(long_list),
        "target_weight": float(target_weight),
        "remaining_ratio": max(0.0, 1.0 - initial_ratio),
        "signal_name": str(g.entry_signal_name),
        "threshold_label": str(g.entry_threshold_label),
        "threshold_value": threshold_value,
        "initial_signal": initial_signal,
        "completed": False,
    }
    if g.debug:
        log.info(
            "entry_overlay_activated mode=%s initial_ratio=%.4f signal=%s threshold=%s initial_signal=%s"
            % (
                mode,
                initial_ratio,
                str(g.entry_signal_name),
                str(safe_round(threshold_value, 6)),
                str(safe_round(initial_signal, 6)),
            )
        )


def maybe_complete_pending_entry(context):
    pending = getattr(g, "pending_entry", None)
    if pending is None or pending.get("completed"):
        return

    approved_codes = get_tradable_stocks(pending.get("target_codes", []))
    if len(approved_codes) == 0:
        return

    current_trade_date = get_previous_trade_date(context)
    waited_days = get_trade_day_count_between(pending.get("activation_trade_date"), current_trade_date)
    if waited_days is None:
        return

    current_signal = compute_entry_signal_snapshot(current_trade_date, approved_codes)
    trigger_hit = False
    force_fill = False
    mode = pending.get("mode")
    max_wait = int(getattr(g, "entry_search_trade_days", 20))

    if mode == "split_50_50_time":
        force_fill = waited_days >= max_wait
    elif mode == "split_50_50_reversion":
        threshold_value = pending.get("threshold_value")
        if current_signal is not None and not pd.isna(current_signal) and threshold_value is not None and not pd.isna(threshold_value):
            trigger_hit = current_signal <= float(threshold_value)
        force_fill = waited_days >= max_wait
    else:
        pending["completed"] = True
        g.pending_entry = pending
        return

    if not trigger_hit and not force_fill:
        if g.debug:
            log.info(
                "pending_entry_wait mode=%s current_date=%s waited_days=%s signal=%s threshold=%s"
                % (
                    str(mode),
                    str(to_date(context.current_dt)),
                    str(waited_days),
                    str(safe_round(current_signal, 6)),
                    str(safe_round(pending.get("threshold_value"), 6)),
                )
            )
        return

    execute_target_weights(context, approved_codes, 1.0 / float(len(approved_codes)))
    pending["completed"] = True
    pending["completion_date"] = str(to_date(context.current_dt))
    pending["completion_trade_date"] = str(current_trade_date)
    pending["completion_signal"] = current_signal
    pending["waited_trade_days"] = waited_days
    pending["completion_reason"] = "signal_trigger" if trigger_hit else "force_fill"
    g.pending_entry = pending

    if g.debug:
        log.info(
            "pending_entry_completed mode=%s date=%s waited_days=%s signal=%s reason=%s"
            % (
                str(mode),
                str(to_date(context.current_dt)),
                str(waited_days),
                str(safe_round(current_signal, 6)),
                str(pending["completion_reason"]),
            )
        )


def execute_target_ratio(context, long_list, total_ratio):
    if long_list is None or len(long_list) == 0:
        return
    total_ratio = float(total_ratio)
    target_weight = total_ratio / float(len(long_list))
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


def get_entry_trigger_threshold(plan_id):
    if plan_id is None:
        return None
    plan_map = g.entry_trigger_library.get(plan_id, {})
    signal_map = plan_map.get(str(g.entry_signal_name), {})
    threshold_value = signal_map.get(str(g.entry_threshold_label), None)
    if threshold_value is None:
        return None
    return float(threshold_value)


def compute_entry_signal_snapshot(factor_date, stocks):
    feature_df = build_entry_feature_snapshot(factor_date, stocks)
    if feature_df.empty:
        return np.nan
    signal_name = str(getattr(g, "entry_signal_name", "rev_5d"))
    work_df = feature_df[(feature_df["price_ready"] == 1) & feature_df[signal_name].notna()].copy()
    if work_df.empty:
        return np.nan
    return float(pd.to_numeric(work_df[signal_name], errors="coerce").mean())


def build_entry_feature_snapshot(factor_date, stocks):
    history_count = int(getattr(g, "entry_price_history_count", 25))
    trade_days = get_trade_days(end_date=factor_date, count=history_count)
    if trade_days is None or len(trade_days) < history_count:
        return pd.DataFrame()

    start_date = to_date(trade_days[0])
    price_df = fetch_price_history_by_range(stocks, start_date, factor_date)
    valuation_df = fetch_market_cap_history_by_range(stocks, start_date, factor_date)
    if price_df.empty or valuation_df.empty:
        return pd.DataFrame()
    return build_entry_feature_frame_for_date(stocks, factor_date, price_df, valuation_df)


def build_entry_feature_frame_for_date(stocks, factor_date, price_df, valuation_df):
    current_data = get_current_data()
    rows = []
    history_count = int(getattr(g, "entry_price_history_count", 25))
    pool_history_count = int(getattr(g, "entry_pool_history_count", 20))
    min_listing_trade_days = int(getattr(g, "entry_min_listing_trade_days", 60))
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

        if len(one_price) >= history_count:
            close_series = pd.to_numeric(one_price["close"], errors="coerce").reset_index(drop=True)
            money_series = pd.to_numeric(one_price["money"], errors="coerce").reset_index(drop=True)
            payload["rev_5d"] = calc_return(close_series, 5)
            payload["abnormal_volume_ratio"] = calc_abnormal_volume_ratio(money_series, 20)
            payload["close_to_ma20"] = calc_close_to_ma(close_series, 20)
            trailing_money = money_series.tail(pool_history_count).dropna()
            if len(trailing_money) >= pool_history_count:
                payload["avg_money_20d"] = float(trailing_money.mean())
            payload["listing_trade_days"] = calc_listing_trade_days(security_info.start_date, factor_date)

        if len(one_valuation) >= pool_history_count:
            mcap_series = pd.to_numeric(one_valuation["market_cap"], errors="coerce").dropna().tail(pool_history_count)
            if len(mcap_series) >= pool_history_count:
                payload["avg_market_cap_20d"] = float(mcap_series.mean())

        rows.append(payload)

    out = pd.DataFrame(rows).sort_values("code").reset_index(drop=True)
    out["price_ready"] = (
        out["rev_5d"].notna()
        & out["abnormal_volume_ratio"].notna()
        & out["close_to_ma20"].notna()
        & out["avg_money_20d"].notna()
        & out["avg_market_cap_20d"].notna()
        & (pd.to_numeric(out["listing_trade_days"], errors="coerce") >= min_listing_trade_days)
    ).astype(int)
    out["rev5_abnvol"] = (
        -0.7 * pd.to_numeric(out["rev_5d"], errors="coerce")
        + 0.3 * pd.to_numeric(out["abnormal_volume_ratio"], errors="coerce")
    )
    return out


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


def get_trade_day_count_between(start_date, end_date):
    start_value = to_date(start_date)
    end_value = to_date(end_date)
    if start_value is None or end_value is None:
        return None
    try:
        trade_days = get_trade_days(start_date=start_value, end_date=end_value)
        if trade_days is None or len(trade_days) == 0:
            return 0
        return int(len(trade_days))
    except Exception:
        return None


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


def safe_float(value, fallback=np.nan):
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
