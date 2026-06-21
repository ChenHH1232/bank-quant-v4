from jqdata import *
from datetime import datetime

import numpy as np
import pandas as pd

import joinquant_v4_annual_backtest_strategy as base


def initialize(context):
    g.bank_stocks = list(base.build_manual_bank_indicator_data().keys())

    set_benchmark('512800.XSHG')
    set_option('use_real_price', True)
    set_option('avoid_future_data', True)
    set_order_cost(
        OrderCost(
            open_commission=0.0003,
            close_commission=0.0003,
            min_commission=5
        ),
        type='stock'
    )

    g.rebalance_months = [5, 9, 11]
    g.group_count = 5
    g.hold_bucket = 5
    g.strategy_line = 'benchmark'
    g.debug = True

    g.enable_fundamental_defensive_overlay = True
    g.defensive_asset_candidates = ['511010.XSHG', '511260.XSHG']
    g.regime_warning_equity_weight = 0.60
    g.regime_severe_equity_weight = 0.20

    g.annual_plan_library = base.build_annual_plan_library()
    g.manual_bank_indicator_data = base.build_manual_bank_indicator_data()
    g.executed_rebalance_keys = set()
    g.plan_usage_log = []
    g.regime_history_log = []

    run_daily(maybe_rebalance, time='09:40')


def maybe_rebalance(context):
    current_date = context.current_dt.date()
    if current_date.month not in g.rebalance_months:
        return

    rebalance_key = '%04d-%02d' % (current_date.year, current_date.month)
    if rebalance_key in g.executed_rebalance_keys:
        return

    do_rebalance(context)
    g.executed_rebalance_keys.add(rebalance_key)


def do_rebalance(context):
    factor_date = base.get_previous_trade_date(context)
    plan = base.get_active_plan(factor_date)
    if plan is None:
        log.info('No annual plan available for %s' % str(factor_date))
        return

    factor_specs = plan['primary_factors'] if g.strategy_line == 'primary' else plan['benchmark_factors']
    tradable = base.get_tradable_stocks(context, g.bank_stocks)
    if len(tradable) < g.group_count:
        log.info('Tradable bank count is too small: %d' % len(tradable))
        return

    score_df = base.build_score_frame(context, tradable, factor_date, factor_specs)
    if score_df is None or score_df.empty:
        log.info('Score frame is empty on %s' % str(factor_date))
        return

    score_df = score_df.sort_values(['final_score', 'code'], ascending=[False, True]).copy()
    score_df['bucket'] = base.assign_groups(score_df['final_score'], g.group_count)
    score_df = score_df.dropna(subset=['bucket']).copy()
    score_df['bucket'] = score_df['bucket'].astype(int)

    long_df = score_df[score_df['bucket'] == g.hold_bucket].copy()
    if long_df.empty:
        log.info('No stocks entered top bucket on %s' % str(factor_date))
        return

    long_list = long_df['code'].tolist()
    factor_summary = base.summarize_factor_specs(factor_specs)
    top_score_preview = base.build_score_preview(score_df.head(10))
    long_score_preview = base.build_score_preview(long_df[['code', 'final_score', 'factor_count']].head(20))

    regime_info = evaluate_fundamental_regime(factor_date)
    equity_weight = regime_info['equity_weight']
    defensive_asset = regime_info['defensive_asset']
    defensive_weight = regime_info['defensive_weight']
    target_weight = (equity_weight / float(len(long_list))) if long_list and equity_weight > 0 else 0.0

    if g.debug:
        log.info('========== V4 annual rebalance ==========')
        log.info('current_date=%s factor_date=%s plan=%s line=%s' % (
            str(context.current_dt.date()),
            str(factor_date),
            plan['plan_id'],
            g.strategy_line,
        ))
        log.info('factor_summary=%s' % factor_summary)
        log.info('selected_count=%d long_list=%s' % (len(long_list), str(long_list)))
        log.info('top_score_preview=%s' % top_score_preview)
        log.info('long_score_preview=%s' % long_score_preview)
        log.info(
            'fundamental_regime=%s equity_weight=%.2f defensive_weight=%.2f defensive_asset=%s summary=%s' % (
                regime_info['regime_name'],
                equity_weight,
                defensive_weight,
                str(defensive_asset),
                regime_info['summary'],
            )
        )

    execute_target_weights(context, long_list, target_weight, defensive_asset, defensive_weight)

    g.plan_usage_log.append({
        'rebalance_date': str(context.current_dt.date()),
        'factor_date': str(factor_date),
        'plan_id': plan['plan_id'],
        'strategy_line': g.strategy_line,
        'regime_name': regime_info['regime_name'],
        'equity_weight': round(equity_weight, 4),
        'defensive_weight': round(defensive_weight, 4),
        'defensive_asset': defensive_asset if defensive_asset is not None else '',
        'regime_summary': regime_info['summary'],
        'factor_summary': factor_summary,
        'holding_count': len(long_list),
        'holdings': '|'.join(long_list),
        'top_score_preview': top_score_preview,
    })
    g.regime_history_log.append({
        'rebalance_date': str(context.current_dt.date()),
        'factor_date': str(factor_date),
        'regime_name': regime_info['regime_name'],
        'equity_weight': round(equity_weight, 4),
        'defensive_weight': round(defensive_weight, 4),
        'defensive_asset': defensive_asset if defensive_asset is not None else '',
        'summary': regime_info['summary'],
    })


def evaluate_fundamental_regime(factor_date):
    stocks = list(g.bank_stocks)
    current_snapshot = base.fetch_current_snapshot_factors(stocks, factor_date)
    previous_rebalance_date = base.get_previous_rebalance_factor_date(factor_date)
    previous_snapshot = base.fetch_current_snapshot_factors(stocks, previous_rebalance_date) if previous_rebalance_date else pd.DataFrame()

    current_bank_source_year = base.get_current_bank_source_year(factor_date)
    previous_bank_source_year = current_bank_source_year - 1 if current_bank_source_year is not None else None
    current_bank = base.fetch_bank_indicator_snapshot(stocks, current_bank_source_year)
    previous_bank = base.fetch_bank_indicator_snapshot(stocks, previous_bank_source_year) if previous_bank_source_year is not None else pd.DataFrame()

    metrics = {
        'npl_deterioration_ratio': compute_deterioration_ratio(
            current_bank.get('bank_indicator__Nonperforming_loan_rate'),
            previous_bank.get('bank_indicator__Nonperforming_loan_rate'),
            higher_is_worse=True,
        ),
        'capital_deterioration_ratio': compute_deterioration_ratio(
            current_bank.get('bank_indicator__capital_adequacy_ratio'),
            previous_bank.get('bank_indicator__capital_adequacy_ratio'),
            higher_is_worse=False,
        ),
        'coverage_deterioration_ratio': compute_deterioration_ratio(
            current_bank.get('bank_indicator__non_performing_loan_provision_coverage'),
            previous_bank.get('bank_indicator__non_performing_loan_provision_coverage'),
            higher_is_worse=False,
        ),
        'roe_deterioration_ratio': compute_deterioration_ratio(
            current_snapshot.get('indicator__roe'),
            previous_snapshot.get('indicator__roe'),
            higher_is_worse=False,
        ),
        'profit_growth_deterioration_ratio': compute_deterioration_ratio(
            current_snapshot.get('indicator__inc_net_profit_to_shareholders_annual'),
            previous_snapshot.get('indicator__inc_net_profit_to_shareholders_annual'),
            higher_is_worse=False,
        ),
    }

    valid_metric_values = [value for value in metrics.values() if pd.notna(value)]
    breadth_score = float(np.mean(valid_metric_values)) if valid_metric_values else 0.0
    severe_hit_count = sum(value >= 0.55 for value in valid_metric_values)
    warning_hit_count = sum(value >= 0.40 for value in valid_metric_values)

    if severe_hit_count >= 2 or breadth_score >= 0.55:
        regime_name = 'severe_deterioration'
        equity_weight = g.regime_severe_equity_weight
    elif warning_hit_count >= 2 or breadth_score >= 0.40:
        regime_name = 'warning_deterioration'
        equity_weight = g.regime_warning_equity_weight
    else:
        regime_name = 'normal'
        equity_weight = 1.0

    defensive_asset = pick_defensive_asset() if equity_weight < 1.0 else None
    defensive_weight = max(0.0, 1.0 - float(equity_weight))
    if defensive_weight > 0 and defensive_asset is None:
        regime_name = regime_name + '_cash_fallback'

    summary = ' ; '.join(
        '%s=%.3f' % (name, float(value))
        for name, value in sorted(metrics.items())
        if pd.notna(value)
    )
    return {
        'regime_name': regime_name,
        'equity_weight': float(equity_weight),
        'defensive_weight': float(defensive_weight),
        'defensive_asset': defensive_asset,
        'summary': summary if summary else 'no_valid_metrics',
    }


def compute_deterioration_ratio(current_series, previous_series, higher_is_worse):
    current_series = pd.to_numeric(current_series, errors='coerce') if current_series is not None else pd.Series(dtype=float)
    previous_series = pd.to_numeric(previous_series, errors='coerce') if previous_series is not None else pd.Series(dtype=float)
    if current_series.empty or previous_series.empty:
        return np.nan

    paired = pd.concat(
        [
            current_series.rename('current'),
            previous_series.rename('previous'),
        ],
        axis=1,
    ).dropna()
    if paired.empty:
        return np.nan

    if higher_is_worse:
        deteriorated = paired['current'] > paired['previous']
    else:
        deteriorated = paired['current'] < paired['previous']
    return float(deteriorated.mean())


def pick_defensive_asset():
    current_data = get_current_data()
    for asset in g.defensive_asset_candidates:
        try:
            data = current_data[asset]
        except Exception:
            continue
        if data is None or data.paused:
            continue
        return asset
    return None


def execute_target_weights(context, long_list, target_weight, defensive_asset, defensive_weight):
    target_value_map = {}
    if target_weight > 0:
        for stock in long_list:
            target_value_map[stock] = context.portfolio.total_value * target_weight
    if defensive_asset is not None and defensive_weight > 0:
        target_value_map[defensive_asset] = context.portfolio.total_value * defensive_weight

    positions = context.portfolio.positions
    current_positions = list(positions.keys())

    for stock in current_positions:
        if stock not in target_value_map:
            try:
                order_target_value(stock, 0)
            except Exception as exc:
                log.info('sell failed %s %s' % (stock, str(exc)))

    for stock in target_value_map:
        try:
            order_target_value(stock, target_value_map[stock])
        except Exception as exc:
            log.info('buy failed %s %s' % (stock, str(exc)))


def after_trading_end(context):
    if not g.debug:
        return
    current_date = context.current_dt.date()
    if current_date == datetime(2026, 5, 31).date():
        log.info('========== V4 annual plan usage ==========')
        for item in g.plan_usage_log:
            log.info(str(item))
        log.info('========== V4 annual regime usage ==========')
        for item in g.regime_history_log:
            log.info(str(item))
