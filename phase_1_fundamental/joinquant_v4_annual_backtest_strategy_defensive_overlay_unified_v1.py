from jqdata import *
from datetime import datetime, timedelta
from io import StringIO

import numpy as np
import pandas as pd


def initialize(context):
    g.bank_stocks = [
        '000001.XSHE', '001227.XSHE', '002142.XSHE', '002807.XSHE',
        '002839.XSHE', '002936.XSHE', '002948.XSHE', '002958.XSHE',
        '002966.XSHE', '600000.XSHG', '600015.XSHG', '600016.XSHG',
        '600036.XSHG', '600908.XSHG', '600919.XSHG', '600926.XSHG',
        '600928.XSHG', '601009.XSHG', '601077.XSHG', '601128.XSHG',
        '601166.XSHG', '601169.XSHG', '601187.XSHG', '601229.XSHG',
        '601288.XSHG', '601328.XSHG', '601398.XSHG', '601528.XSHG',
        '601577.XSHG', '601658.XSHG', '601665.XSHG', '601818.XSHG',
        '601825.XSHG', '601838.XSHG', '601916.XSHG', '601939.XSHG',
        '601963.XSHG', '601988.XSHG', '601997.XSHG', '601998.XSHG',
        '603323.XSHG'
    ]

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

    # Execution cadence aligned with the V4 local panel.
    g.rebalance_months = [5, 9, 11]
    g.group_count = 5
    g.hold_bucket = 5
    g.strategy_line = 'benchmark'
    g.debug = True

    # Overlay logic:
    # compare each year's active factor set with the same period last year,
    # evaluate deterioration inside the post-filter candidate pool, and map
    # deterioration breadth linearly into treasury weight.
    g.overlay_variant = 'treasury_yoy_candidate_pool_linear'
    g.defensive_asset = '511010.XSHG'
    g.regime_compare_mode = 'same_period_last_year'
    g.regime_stock_deterioration_threshold = 0.50
    g.regime_min_valid_factor_count = 2
    g.regime_weight_floor = 0.00
    g.regime_weight_cap = 1.00
    g.regime_weight_power = 1.00

    # The local V4 annual research currently covers annual_01 to annual_05.
    # annual_05 is kept open-ended so a backtest ending on 2026-05-31 can still run.
    g.annual_plan_library = build_annual_plan_library()
    g.manual_bank_indicator_data = build_manual_bank_indicator_data()
    g.executed_rebalance_keys = set()
    g.plan_usage_log = []
    g.regime_history_log = []

    run_daily(maybe_rebalance, time='09:40')


def build_annual_plan_library():
    return [
        {
            'plan_id': 'annual_01',
            'effective_start': datetime(2021, 5, 6).date(),
            'effective_end': datetime(2022, 5, 4).date(),
            'benchmark_factors': [
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 0.191488),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.125512),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.137916),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.050207),
                factor_spec('indicator__eps', 1, 0.073011),
                factor_spec('indicator__roe', 1, 0.105681),
            ],
            'primary_factors': [
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 0.191488),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.125512),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.137916),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.050207),
                factor_spec('indicator__eps', 1, 0.073011),
                factor_spec('indicator__roe', 1, 0.105681),
                factor_spec('improve__annual_delta__bank_indicator__Nonperforming_loan_rate', -1, 0.082644),
                factor_spec('improve__snapshot_delta__derived__investment_income_to_operating_revenue', -1, 0.027117),
            ],
        },
        {
            'plan_id': 'annual_02',
            'effective_start': datetime(2022, 5, 5).date(),
            'effective_end': datetime(2023, 5, 3).date(),
            'benchmark_factors': [
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 0.202109),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.268493),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.303511),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.165653),
                factor_spec('derived__log_total_assets', 1, 0.156735),
                factor_spec('indicator__eps', 1, 0.117962),
                factor_spec('indicator__roe', 1, 0.207792),
            ],
            'primary_factors': [
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 0.202109),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.268493),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.303511),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.165653),
                factor_spec('derived__log_total_assets', 1, 0.156735),
                factor_spec('indicator__eps', 1, 0.117962),
                factor_spec('indicator__roe', 1, 0.207792),
                factor_spec('improve__annual_delta__bank_indicator__capital_adequacy_ratio', -1, 0.210412),
                factor_spec('improve__snapshot_delta__derived__investment_income_to_operating_revenue', -1, 0.040745),
            ],
        },
        {
            'plan_id': 'annual_03',
            'effective_start': datetime(2023, 5, 4).date(),
            'effective_end': datetime(2024, 5, 5).date(),
            'benchmark_factors': [
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.32383),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.259314),
                factor_spec('derived__log_total_assets', 1, 0.160546),
            ],
            'primary_factors': [
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.32383),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.259314),
                factor_spec('derived__log_total_assets', 1, 0.160546),
            ],
        },
        {
            'plan_id': 'annual_04',
            'effective_start': datetime(2024, 5, 6).date(),
            'effective_end': datetime(2025, 5, 5).date(),
            'benchmark_factors': [
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.238645),
                factor_spec('derived__log_total_assets', 1, 0.141748),
            ],
            'primary_factors': [
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.238645),
                factor_spec('derived__log_total_assets', 1, 0.141748),
                factor_spec('improve__annual_delta__bank_indicator__Nonperforming_loan_rate', -1, 0.154845),
                factor_spec('improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual', -1, 0.040045),
            ],
        },
        {
            'plan_id': 'annual_05',
            'effective_start': datetime(2025, 5, 6).date(),
            'effective_end': None,
            'benchmark_factors': [
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.208277),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.167715),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.134438),
                factor_spec('derived__log_total_assets', 1, 0.100048),
            ],
            'primary_factors': [
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.208277),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.167715),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.134438),
                factor_spec('derived__log_total_assets', 1, 0.100048),
                factor_spec('improve__season_yoy_delta__derived__staff_cash_to_operating_revenue', -1, 0.015276),
                factor_spec('improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual', -1, 0.010205),
            ],
        },
    ]


MANUAL_BANK_INDICATOR_CSV = '''\ncode,source_year,Nonperforming_loan_rate,capital_adequacy_ratio,deposit_loan_ratio,non_performing_loan_provision_coverage
000001.XSHE,2019,1.65,13.22,93.72,183.12
000001.XSHE,2020,1.18,13.29,98.9006,201.4
000001.XSHE,2021,1.02,13.34,102.4387,288.42
000001.XSHE,2022,1.05,13.01,99.3108,290.28
000001.XSHE,2023,1.06,13.43,98.5317,277.63
001227.XSHE,2022,1.71,11.27,71.41,194.99
001227.XSHE,2023,1.73,11.12,74.15,197.51
002142.XSHE,2019,0.78,15.57,66.51,524.08
002142.XSHE,2020,0.79,14.84,71.85,505.59
002142.XSHE,2021,0.77,15.43,79.75,525.52
002142.XSHE,2022,0.75,15.18,79.79,504.9
002142.XSHE,2023,0.76,15.01,78.98,461.04
002807.XSHE,2019,1.83,15.29,75.39,259.13
002807.XSHE,2020,1.79,14.48,77.84,224.27
002807.XSHE,2021,1.32,14.11,79.92,330.62
002807.XSHE,2022,0.98,13.9,81.39,469.62
002807.XSHE,2023,0.98,14.24,82.86,409.46
002839.XSHE,2019,1.38,15.1,78.64,252.14
002839.XSHE,2020,1.17,13.75,79.18,307.83
002839.XSHE,2021,0.95,14.3,82.4,475.35
002839.XSHE,2022,0.89,13.13,82.41,521.09
002839.XSHE,2023,0.94,13.04,81.19,424.23
002936.XSHE,2019,2.37,12.11,72.33,159.85
002936.XSHE,2020,2.08,12.86,82.63,160.44
002936.XSHE,2021,1.85,15.0,90.66,156.58
002936.XSHE,2022,1.88,12.72,97.99,165.73
002936.XSHE,2023,1.87,12.38,99.9,174.87
002948.XSHE,2019,1.65,14.76,80.5698,155.09
002948.XSHE,2020,1.51,14.11,75.3022,169.62
002948.XSHE,2021,1.34,15.83,77.0633,197.42
002948.XSHE,2022,1.21,13.56,77.4697,219.77
002948.XSHE,2023,1.18,12.79,75.8823,225.96
002958.XSHE,2019,1.46,12.26,81.6748,310.23
002958.XSHE,2020,1.44,12.32,87.061,278.73
002958.XSHE,2021,1.74,13.07,86.5109,231.77
002958.XSHE,2022,2.19,13.18,83.8858,207.63
002958.XSHE,2023,1.81,13.21,85.7499,237.96
002966.XSHE,2019,1.53,14.36,74.06,224.07
002966.XSHE,2020,1.38,14.21,77.18,291.74
002966.XSHE,2021,1.11,13.06,78.59,422.91
002966.XSHE,2022,0.88,12.92,79.23,530.81
002966.XSHE,2023,0.84,14.03,80.64,522.77
600000.XSHG,2019,2.03,13.86,109.942,134.94
600000.XSHG,2020,1.73,14.64,109.9836,152.77
600000.XSHG,2021,1.61,14.01,107.2236,143.96
600000.XSHG,2022,1.52,13.65,100.14,159.04
600000.XSHG,2023,1.48,12.67,100.6645,173.51
600015.XSHG,2019,1.83,13.89,98.86,141.92
600015.XSHG,2020,1.8,13.08,99.95,147.22
600015.XSHG,2021,1.77,12.82,99.19,150.99
600015.XSHG,2022,1.75,13.27,93.35,159.88
600015.XSHG,2023,1.67,12.23,89.24,160.06
600016.XSHG,2019,1.56,13.17,95.8913,155.5
600016.XSHG,2020,1.82,13.04,102.2764,139.38
600016.XSHG,2021,1.79,13.64,105.7506,145.3
600016.XSHG,2022,1.68,13.14,102.9378,142.49
600016.XSHG,2023,1.48,13.14,100.7258,149.69
600036.XSHG,2019,1.16,15.54,92.6973,426.78
600036.XSHG,2020,1.07,16.54,89.3537,437.68
600036.XSHG,2021,0.91,17.48,87.7575,483.87
600036.XSHG,2022,0.96,17.77,80.3034,450.79
600036.XSHG,2023,0.95,17.88,79.8101,437.7
600908.XSHG,2019,1.21,15.85,66.25,288.18
600908.XSHG,2020,1.1,15.21,70.54,355.88
600908.XSHG,2021,0.93,14.35,75.14,477.19
600908.XSHG,2022,0.81,14.75,74.48,552.74
600908.XSHG,2023,0.79,14.41,73.68,522.57
600919.XSHG,2019,1.38,12.89,82.67,232.79
600919.XSHG,2020,1.32,14.47,88.71,256.4
600919.XSHG,2021,1.08,13.38,93.21,318.93
600919.XSHG,2022,0.94,13.07,93.52,371.66
600919.XSHG,2023,0.89,13.31,89.79,389.53
600926.XSHG,2019,1.34,13.54,67.23,316.71
600926.XSHG,2020,1.07,14.41,68.91,469.54
600926.XSHG,2021,0.86,13.62,72.51,567.71
600926.XSHG,2022,0.77,12.89,74.77,565.1
600926.XSHG,2023,0.76,12.51,75.67,561.42
600928.XSHG,2019,1.18,14.85,87.63,262.41
600928.XSHG,2020,1.18,14.5,79.98,269.39
600928.XSHG,2021,1.32,14.12,78.33,224.21
600928.XSHG,2022,1.25,12.84,66.67,201.63
600928.XSHG,2023,1.35,13.14,68.65,197.07
601009.XSHG,2019,0.89,13.03,66.93,417.73
601009.XSHG,2020,0.91,14.75,71.33,391.76
601009.XSHG,2021,0.91,13.54,73.77,397.34
601009.XSHG,2022,0.9,14.31,76.44,397.2
601009.XSHG,2023,0.9,13.53,80.3,360.58
601077.XSHG,2019,1.25,14.88,64.91,380.31
601077.XSHG,2020,1.31,14.28,70.05,314.95
601077.XSHG,2021,1.25,14.77,76.67,340.25
601077.XSHG,2022,1.22,15.62,76.69,357.74
601077.XSHG,2023,1.19,15.99,75.51,366.7
601128.XSHG,2019,0.96,15.1,81.62,481.28
601128.XSHG,2020,0.96,13.53,82.95,485.33
601128.XSHG,2021,0.81,11.95,89.09,531.82
601128.XSHG,2022,0.81,13.87,90.62,536.77
601128.XSHG,2023,0.75,13.86,89.72,537.88
601166.XSHG,2019,1.54,13.36,90.6878,199.13
601166.XSHG,2020,1.25,13.47,97.0969,218.83
601166.XSHG,2021,1.1,14.39,101.663,268.73
601166.XSHG,2022,1.09,14.44,96.21,236.44
601166.XSHG,2023,1.07,14.13,104.6745,245.21
601169.XSHG,2019,1.4,12.28,93.6101,224.69
601169.XSHG,2020,1.57,11.49,94.6606,215.95
601169.XSHG,2021,1.44,14.63,97.0647,210.22
601169.XSHG,2022,1.43,14.04,92.6449,210.04
601169.XSHG,2023,1.32,13.37,95.9316,216.78
601187.XSHG,2020,0.98,14.49,90.6578,368.03
601187.XSHG,2021,0.91,16.4,94.3487,370.64
601187.XSHG,2022,0.86,13.76,96.7975,387.93
601187.XSHG,2023,0.76,15.4,101.0245,412.89
601229.XSHG,2019,1.16,13.84,81.89,337.15
601229.XSHG,2020,1.22,12.86,83.21,321.38
601229.XSHG,2021,1.25,12.16,83.59,301.13
601229.XSHG,2022,1.25,13.16,81.22,291.61
601229.XSHG,2023,1.21,13.38,81.17,272.66
601288.XSHG,2019,1.4,16.13,72.0511,295.45
601288.XSHG,2020,1.57,16.59,74.4638,266.2
601288.XSHG,2021,1.43,17.13,78.3995,299.73
601288.XSHG,2022,1.37,17.2,78.6744,302.6
601288.XSHG,2023,1.33,17.14,78.0812,303.87
601328.XSHG,2019,1.47,14.83,87.3432,171.77
601328.XSHG,2020,1.67,15.25,88.5142,143.87
601328.XSHG,2021,1.48,15.45,93.1905,166.5
601328.XSHG,2022,1.35,14.97,92.005,180.68
601328.XSHG,2023,1.33,15.27,93.0521,195.21
601398.XSHG,2019,1.43,16.77,71.6,199.32
601398.XSHG,2020,1.58,16.88,72.8,180.68
601398.XSHG,2021,1.42,18.02,77.3,205.84
601398.XSHG,2022,1.38,19.26,76.7,209.47
601398.XSHG,2023,1.36,19.1,76.7,213.97
601528.XSHG,2021,1.25,18.85,84.51,252.9
601528.XSHG,2022,1.08,15.58,80.17,280.5
601528.XSHG,2023,0.97,13.88,75.22,304.12
601577.XSHG,2019,1.22,13.25,66.8,279.98
601577.XSHG,2020,1.21,13.6,66.64,292.68
601577.XSHG,2021,1.2,13.66,69.7,297.87
601577.XSHG,2022,1.16,13.41,70.25,311.09
601577.XSHG,2023,1.15,13.04,67.79,314.21
601658.XSHG,2019,0.86,13.52,53.41,389.45
601658.XSHG,2020,0.88,13.88,55.19,408.06
601658.XSHG,2021,0.82,14.78,56.84,418.61
601658.XSHG,2022,0.84,13.82,56.71,385.51
601658.XSHG,2023,0.83,14.23,58.39,347.57
601665.XSHG,2021,1.35,15.31,58.5,253.95
601665.XSHG,2022,1.29,14.47,73.58,281.06
601665.XSHG,2023,1.26,15.38,75.41,303.58
601818.XSHG,2019,1.56,13.47,89.8709,181.62
601818.XSHG,2020,1.38,13.9,86.4628,182.71
601818.XSHG,2021,1.25,13.37,89.9765,187.02
601818.XSHG,2022,1.25,12.95,91.4572,187.93
601818.XSHG,2023,1.25,13.5,92.4882,181.27
601825.XSHG,2021,0.95,15.28,71.7326,442.5
601825.XSHG,2022,0.94,15.46,69.7571,445.32
601825.XSHG,2023,0.97,15.74,69.9995,404.98
601838.XSHG,2019,1.43,15.69,62.27,253.88
601838.XSHG,2020,1.37,14.23,66.66,293.43
601838.XSHG,2021,0.98,13.0,74.76,402.88
601838.XSHG,2022,0.78,13.15,77.57,501.57
601838.XSHG,2023,0.68,12.89,83.2,504.29
601916.XSHG,2019,1.37,14.24,84.4,220.8
601916.XSHG,2020,1.42,12.93,83.7,191.01
601916.XSHG,2021,1.53,12.89,91.0,174.61
601916.XSHG,2022,1.47,11.6,84.82,182.19
601916.XSHG,2023,1.44,12.19,87.74,182.6
601939.XSHG,2019,1.42,17.52,77.68,227.69
601939.XSHG,2020,1.56,17.06,78.49,213.59
601939.XSHG,2021,1.42,17.85,84.04299999999999,239.96
601939.XSHG,2022,1.38,18.42,84.71799999999999,241.53
601939.XSHG,2023,1.37,17.95,86.1032,239.85
601963.XSHG,2021,1.3,12.99,93.91,274.01
601963.XSHG,2022,1.38,12.72,92.15,211.19
601963.XSHG,2023,1.34,13.37,94.73,234.18
601988.XSHG,2019,1.37,15.59,82.6221,182.86
601988.XSHG,2020,1.46,16.22,84.225,177.84
601988.XSHG,2021,1.33,16.53,82.5,187.05
601988.XSHG,2022,1.32,17.52,82.9,188.73
601988.XSHG,2023,1.27,17.74,82.7,191.66
601997.XSHG,2019,1.45,13.61,61.37,291.86
601997.XSHG,2020,1.53,12.88,65.05,277.3
601997.XSHG,2021,1.45,13.96,70.88,271.03
601997.XSHG,2022,1.45,14.16,74.36,260.86
601997.XSHG,2023,1.59,15.03,80.97,244.5
601998.XSHG,2019,1.65,12.44,98.1521,175.25
601998.XSHG,2020,1.64,13.01,97.8352,171.68
601998.XSHG,2021,1.39,13.53,101.3779,180.07
601998.XSHG,2022,1.27,13.18,100.2344,201.19
601998.XSHG,2023,1.18,12.93,100.5612,207.59
603323.XSHG,2019,1.33,14.67,72.38,249.32
603323.XSHG,2020,1.28,13.53,73.61,305.31
603323.XSHG,2021,1.0,12.99,77.68,412.22
603323.XSHG,2022,0.95,12.09,78.0,442.83
603323.XSHG,2023,0.91,11.88,77.6,452.85
'''

def factor_spec(name, direction_sign, train_ic):
    return {
        'name': name,
        'direction_sign': direction_sign,
        'train_ic': float(abs(train_ic)),
    }


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
    factor_date = get_previous_trade_date(context)
    plan = get_active_plan(factor_date)
    if plan is None:
        log.info('No annual plan available for %s' % str(factor_date))
        return

    factor_specs = plan['benchmark_factors']
    tradable = get_tradable_stocks(context, g.bank_stocks)
    if len(tradable) < g.group_count:
        log.info('Tradable bank count is too small: %d' % len(tradable))
        return

    score_df = build_score_frame(context, tradable, factor_date, factor_specs)
    if score_df is None or score_df.empty:
        log.info('Score frame is empty on %s' % str(factor_date))
        return

    score_df = score_df.sort_values(['final_score', 'code'], ascending=[False, True]).copy()
    score_df['bucket'] = assign_groups(score_df['final_score'], g.group_count)
    score_df = score_df.dropna(subset=['bucket']).copy()
    score_df['bucket'] = score_df['bucket'].astype(int)

    long_df = score_df[score_df['bucket'] == g.hold_bucket].copy()
    if long_df.empty:
        log.info('No stocks entered top bucket on %s' % str(factor_date))
        return

    long_list = long_df['code'].tolist()
    factor_summary = summarize_factor_specs(factor_specs)
    top_score_preview = build_score_preview(score_df.head(10))
    long_score_preview = build_score_preview(long_df[['code', 'final_score', 'factor_count']].head(20))
    regime_info = evaluate_fundamental_regime(factor_date, factor_specs, score_df)
    equity_weight = regime_info['equity_weight']
    defensive_weight = regime_info['defensive_weight']
    defensive_asset = regime_info['defensive_asset']
    target_weight = (equity_weight / float(len(long_list))) if long_list and equity_weight > 0 else 0.0

    if g.debug:
        log.info('========== V4 annual defensive candidate ==========')
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
            'overlay_variant=%s fundamental_regime=%s equity_weight=%.2f defensive_weight=%.2f defensive_asset=%s summary=%s' % (
                g.overlay_variant,
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
        'overlay_variant': g.overlay_variant,
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
        'overlay_variant': g.overlay_variant,
        'regime_name': regime_info['regime_name'],
        'equity_weight': round(equity_weight, 4),
        'defensive_weight': round(defensive_weight, 4),
        'defensive_asset': defensive_asset if defensive_asset is not None else '',
        'summary': regime_info['summary'],
    })


def build_score_frame(context, stocks, factor_date, factor_specs):
    factor_context = build_factor_context(stocks, factor_date)
    current_snapshot = factor_context['current_snapshot']
    if current_snapshot.empty:
        if g.debug:
            log.info('current_snapshot is empty on %s' % str(factor_date))
        return pd.DataFrame()

    previous_rebalance_date = factor_context['previous_rebalance_date']
    previous_snapshot = factor_context['previous_snapshot']
    yoy_snapshot_date = factor_context['yoy_snapshot_date']
    yoy_snapshot = factor_context['yoy_snapshot']
    current_bank_source_year = factor_context['current_bank_source_year']
    previous_bank_source_year = factor_context['previous_bank_source_year']
    current_bank = factor_context['current_bank']
    previous_bank = factor_context['previous_bank']

    score_df = pd.DataFrame(index=stocks)
    score_df['code'] = score_df.index

    if g.debug:
        log_factor_frame_status('current_snapshot', current_snapshot, factor_date)
        log_factor_frame_status('previous_snapshot', previous_snapshot, previous_rebalance_date)
        log_factor_frame_status('yoy_snapshot', yoy_snapshot, yoy_snapshot_date)
        log_factor_frame_status('current_bank', current_bank, current_bank_source_year)
        log_factor_frame_status('previous_bank', previous_bank, previous_bank_source_year)

    for spec in factor_specs:
        factor_name = spec['name']
        raw_series = compute_factor_series(
            factor_name=factor_name,
            stocks=stocks,
            current_snapshot=current_snapshot,
            previous_snapshot=previous_snapshot,
            yoy_snapshot=yoy_snapshot,
            current_bank=current_bank,
            previous_bank=previous_bank,
        )
        if raw_series is None:
            if g.debug:
                log.info('factor %s returned None' % factor_name)
            continue
        raw_series = raw_series.reindex(stocks)
        if g.debug:
            non_na_count = int(raw_series.notna().sum())
            missing_codes = raw_series[raw_series.isna()].index.tolist()
            log.info(
                'factor %s raw coverage=%d/%d missing_sample=%s' % (
                    factor_name,
                    non_na_count,
                    len(stocks),
                    str(missing_codes[:10]),
                )
            )
        z_col = 'z__' + factor_name
        adj_col = 'adj__' + factor_name
        score_df[factor_name] = raw_series
        score_df[z_col] = zscore_series(winsorize_series(raw_series))
        score_df[adj_col] = score_df[z_col] * float(spec['direction_sign'])

    weight_sum = 0.0
    weighted_score = None
    factor_count = None
    valid_factor_names = []

    for spec in factor_specs:
        factor_name = spec['name']
        adj_col = 'adj__' + factor_name
        if adj_col not in score_df.columns:
            if g.debug:
                log.info('factor %s skipped because %s column is missing' % (factor_name, adj_col))
            continue
        weight = float(spec['train_ic'])
        valid_series = pd.to_numeric(score_df[adj_col], errors='coerce')
        if g.debug:
            usable_count = int(valid_series.notna().sum())
            log.info('factor %s usable zscore coverage=%d/%d weight=%.6f' % (
                factor_name,
                usable_count,
                len(stocks),
                weight,
            ))
        weighted_part = valid_series * weight
        weighted_score = weighted_part if weighted_score is None else (weighted_score + weighted_part)
        factor_count = valid_series.notna().astype(int) if factor_count is None else (factor_count + valid_series.notna().astype(int))
        weight_sum += weight
        valid_factor_names.append(factor_name)

    if weighted_score is None or weight_sum <= 0:
        if g.debug:
            log.info('weighted_score is empty or weight_sum<=0 on %s' % str(factor_date))
        return pd.DataFrame()

    score_df['final_score'] = weighted_score / weight_sum
    score_df['factor_count'] = factor_count
    if g.debug:
        log.info('before final_score dropna rows=%d' % len(score_df))
    score_df = score_df.dropna(subset=['final_score']).copy()
    min_required = min(2, len(valid_factor_names)) if valid_factor_names else 0
    if min_required > 0:
        if g.debug:
            count_dist = score_df['factor_count'].value_counts(dropna=False).sort_index().to_dict()
            log.info('factor_count distribution before threshold: %s min_required=%d' % (str(count_dist), min_required))
        score_df = score_df[score_df['factor_count'] >= min_required].copy()
    if g.debug:
        log.info('after final filters rows=%d on %s' % (len(score_df), str(factor_date)))
    return score_df


def build_factor_context(stocks, factor_date):
    current_snapshot = fetch_current_snapshot_factors(stocks, factor_date)
    previous_rebalance_date = get_previous_rebalance_factor_date(factor_date)
    previous_snapshot = fetch_current_snapshot_factors(stocks, previous_rebalance_date) if previous_rebalance_date else pd.DataFrame()
    yoy_snapshot_date = get_yoy_snapshot_factor_date(factor_date)
    yoy_snapshot = fetch_current_snapshot_factors(stocks, yoy_snapshot_date) if yoy_snapshot_date else pd.DataFrame()

    current_bank_source_year = get_current_bank_source_year(factor_date)
    previous_bank_source_year = current_bank_source_year - 1 if current_bank_source_year is not None else None
    current_bank = fetch_bank_indicator_snapshot(stocks, current_bank_source_year)
    previous_bank = fetch_bank_indicator_snapshot(stocks, previous_bank_source_year) if previous_bank_source_year is not None else pd.DataFrame()

    return {
        'current_snapshot': current_snapshot,
        'previous_rebalance_date': previous_rebalance_date,
        'previous_snapshot': previous_snapshot,
        'yoy_snapshot_date': yoy_snapshot_date,
        'yoy_snapshot': yoy_snapshot,
        'current_bank_source_year': current_bank_source_year,
        'previous_bank_source_year': previous_bank_source_year,
        'current_bank': current_bank,
        'previous_bank': previous_bank,
    }


def compute_factor_series(factor_name, stocks, current_snapshot, previous_snapshot, yoy_snapshot, current_bank, previous_bank):
    if factor_name == 'indicator__roe':
        return current_snapshot.get('indicator__roe')
    if factor_name == 'indicator__eps':
        return current_snapshot.get('indicator__eps')
    if factor_name == 'indicator__inc_net_profit_to_shareholders_annual':
        return current_snapshot.get('indicator__inc_net_profit_to_shareholders_annual')
    if factor_name == 'derived__log_total_assets':
        series = current_snapshot.get('balance__total_assets')
        return np.log(series.replace({0: np.nan})) if series is not None else None
    if factor_name == 'bank_indicator__Nonperforming_loan_rate':
        return current_bank.get('bank_indicator__Nonperforming_loan_rate')
    if factor_name == 'bank_indicator__capital_adequacy_ratio':
        return current_bank.get('bank_indicator__capital_adequacy_ratio')
    if factor_name == 'bank_indicator__deposit_loan_ratio':
        return current_bank.get('bank_indicator__deposit_loan_ratio')
    if factor_name == 'bank_indicator__non_performing_loan_provision_coverage':
        return current_bank.get('bank_indicator__non_performing_loan_provision_coverage')
    if factor_name == 'improve__annual_delta__bank_indicator__Nonperforming_loan_rate':
        return safe_subtract(
            current_bank.get('bank_indicator__Nonperforming_loan_rate'),
            previous_bank.get('bank_indicator__Nonperforming_loan_rate')
        )
    if factor_name == 'improve__annual_delta__bank_indicator__capital_adequacy_ratio':
        return safe_subtract(
            current_bank.get('bank_indicator__capital_adequacy_ratio'),
            previous_bank.get('bank_indicator__capital_adequacy_ratio')
        )
    if factor_name == 'improve__snapshot_delta__derived__investment_income_to_operating_revenue':
        return safe_subtract(
            current_snapshot.get('derived__investment_income_to_operating_revenue'),
            previous_snapshot.get('derived__investment_income_to_operating_revenue')
        )
    if factor_name == 'improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual':
        return safe_subtract(
            current_snapshot.get('indicator__inc_net_profit_to_shareholders_annual'),
            previous_snapshot.get('indicator__inc_net_profit_to_shareholders_annual')
        )
    if factor_name == 'improve__season_yoy_delta__derived__staff_cash_to_operating_revenue':
        return safe_subtract(
            current_snapshot.get('derived__staff_cash_to_operating_revenue'),
            yoy_snapshot.get('derived__staff_cash_to_operating_revenue')
        )
    return None


def fetch_current_snapshot_factors(stocks, factor_date):
    result = pd.DataFrame(index=stocks)
    result['code'] = result.index
    if factor_date is None:
        return result

    indicator_df = get_fundamentals(
        query(
            indicator.code,
            indicator.roe,
            indicator.eps,
            indicator.inc_net_profit_to_shareholders_annual
        ).filter(indicator.code.in_(stocks)),
        date=factor_date,
    )
    if indicator_df is not None and len(indicator_df) > 0:
        indicator_df = indicator_df.set_index('code')
        result['indicator__roe'] = pd.to_numeric(indicator_df['roe'], errors='coerce')
        result['indicator__eps'] = pd.to_numeric(indicator_df['eps'], errors='coerce')
        result['indicator__inc_net_profit_to_shareholders_annual'] = pd.to_numeric(
            indicator_df['inc_net_profit_to_shareholders_annual'],
            errors='coerce'
        )

    balance_df = get_fundamentals(
        query(
            balance.code,
            balance.total_assets
        ).filter(balance.code.in_(stocks)),
        date=factor_date,
    )
    if balance_df is not None and len(balance_df) > 0:
        balance_df = balance_df.set_index('code')
        result['balance__total_assets'] = pd.to_numeric(balance_df['total_assets'], errors='coerce')

    income_df = get_fundamentals(
        query(
            income.code,
            income.operating_revenue,
            income.investment_income
        ).filter(income.code.in_(stocks)),
        date=factor_date,
    )
    if income_df is not None and len(income_df) > 0:
        income_df = income_df.set_index('code')
        result['income__operating_revenue'] = pd.to_numeric(income_df['operating_revenue'], errors='coerce')
        result['income__investment_income'] = pd.to_numeric(income_df['investment_income'], errors='coerce')

    cash_flow_df = get_fundamentals(
        query(
            cash_flow.code,
            cash_flow.staff_behalf_paid
        ).filter(cash_flow.code.in_(stocks)),
        date=factor_date,
    )
    if cash_flow_df is not None and len(cash_flow_df) > 0:
        cash_flow_df = cash_flow_df.set_index('code')
        result['cash_flow__staff_behalf_paid'] = pd.to_numeric(cash_flow_df['staff_behalf_paid'], errors='coerce')

    result['derived__investment_income_to_operating_revenue'] = safe_divide(
        result.get('income__investment_income'),
        result.get('income__operating_revenue')
    )
    result['derived__staff_cash_to_operating_revenue'] = safe_divide(
        result.get('cash_flow__staff_behalf_paid'),
        result.get('income__operating_revenue')
    )
    return result


def fetch_bank_indicator_snapshot(stocks, source_year):
    result = pd.DataFrame(index=stocks)
    result['code'] = result.index
    if source_year is None:
        return result

    records = []
    for stock in stocks:
        stock_data = g.manual_bank_indicator_data.get(stock, {})
        yearly_data = stock_data.get(source_year, None)
        if yearly_data is None:
            continue
        records.append({
            'code': stock,
            'bank_indicator__capital_adequacy_ratio': yearly_data.get('capital_adequacy_ratio', np.nan),
            'bank_indicator__deposit_loan_ratio': yearly_data.get('deposit_loan_ratio', np.nan),
            'bank_indicator__Nonperforming_loan_rate': yearly_data.get('Nonperforming_loan_rate', np.nan),
            'bank_indicator__non_performing_loan_provision_coverage': yearly_data.get('non_performing_loan_provision_coverage', np.nan),
        })

    if not records:
        return result

    df = pd.DataFrame(records).set_index('code')
    for col in df.columns:
        result[col] = pd.to_numeric(df[col], errors='coerce')
    return result


def log_factor_frame_status(name, df, ref_date):
    if not g.debug:
        return
    if df is None or len(df) == 0:
        log.info('%s is empty, ref_date=%s' % (name, str(ref_date)))
        return
    summary_parts = []
    for col in df.columns:
        if col == 'code':
            continue
        try:
            non_na = int(pd.to_numeric(df[col], errors='coerce').notna().sum())
        except Exception:
            non_na = int(df[col].notna().sum())
        summary_parts.append('%s=%d/%d' % (col, non_na, len(df)))
    log.info('%s ref_date=%s coverage: %s' % (name, str(ref_date), ' ; '.join(summary_parts)))


def summarize_factor_specs(factor_specs):
    parts = []
    for spec in factor_specs:
        parts.append('%s[%+d,%.6f]' % (
            spec['name'],
            int(spec['direction_sign']),
            float(spec['train_ic']),
        ))
    return ' ; '.join(parts)


def build_score_preview(df):
    if df is None or len(df) == 0:
        return '[]'
    preview = []
    for _, row in df.iterrows():
        preview.append('%s:score=%.4f,count=%s' % (
            row['code'],
            float(row['final_score']) if pd.notna(row['final_score']) else float('nan'),
            str(int(row['factor_count'])) if 'factor_count' in row and pd.notna(row['factor_count']) else 'na',
        ))
    return '[' + ' ; '.join(preview) + ']'


def evaluate_fundamental_regime(factor_date, factor_specs, pool_df):
    if pool_df is None or pool_df.empty or not factor_specs:
        return {
            'regime_name': 'pool_unavailable',
            'equity_weight': 1.0,
            'defensive_weight': 0.0,
            'defensive_asset': None,
            'summary': 'pool_unavailable',
        }

    stocks = pool_df['code'].tolist()
    current_context = build_factor_context(stocks, factor_date)
    reference_date = get_yoy_snapshot_factor_date(factor_date)
    reference_context = build_factor_context(stocks, reference_date) if reference_date else None
    if reference_context is None:
        return {
            'regime_name': 'reference_unavailable',
            'equity_weight': 1.0,
            'defensive_weight': 0.0,
            'defensive_asset': None,
            'summary': 'reference_unavailable',
        }

    deterioration_df = pd.DataFrame(index=stocks)
    deterioration_df['code'] = deterioration_df.index
    factor_breadth_parts = []

    for spec in factor_specs:
        factor_name = spec['name']
        current_series = compute_factor_series(
            factor_name=factor_name,
            stocks=stocks,
            current_snapshot=current_context['current_snapshot'],
            previous_snapshot=current_context['previous_snapshot'],
            yoy_snapshot=current_context['yoy_snapshot'],
            current_bank=current_context['current_bank'],
            previous_bank=current_context['previous_bank'],
        )
        reference_series = compute_factor_series(
            factor_name=factor_name,
            stocks=stocks,
            current_snapshot=reference_context['current_snapshot'],
            previous_snapshot=reference_context['previous_snapshot'],
            yoy_snapshot=reference_context['yoy_snapshot'],
            current_bank=reference_context['current_bank'],
            previous_bank=reference_context['previous_bank'],
        )
        if current_series is None or reference_series is None:
            continue

        factor_flag = compute_factor_deterioration_flag(
            current_series=current_series.reindex(stocks),
            reference_series=reference_series.reindex(stocks),
            direction_sign=spec['direction_sign'],
        )
        col_name = 'deteriorated__' + factor_name
        deterioration_df[col_name] = factor_flag
        valid_ratio = float(factor_flag.notna().mean()) if len(factor_flag) > 0 else np.nan
        breadth_ratio = float(factor_flag.mean()) if factor_flag.notna().sum() > 0 else np.nan
        if pd.notna(breadth_ratio):
            factor_breadth_parts.append('%s=%.3f' % (factor_name, breadth_ratio))
        if g.debug:
            log.info(
                'overlay factor %s yoy_valid_ratio=%.3f yoy_deterioration_ratio=%s' % (
                    factor_name,
                    valid_ratio if pd.notna(valid_ratio) else float('nan'),
                    '%.3f' % breadth_ratio if pd.notna(breadth_ratio) else 'nan',
                )
            )

    factor_flag_cols = [col for col in deterioration_df.columns if col.startswith('deteriorated__')]
    if not factor_flag_cols:
        return {
            'regime_name': 'no_deterioration_factors',
            'equity_weight': 1.0,
            'defensive_weight': 0.0,
            'defensive_asset': None,
            'summary': 'no_deterioration_factors',
        }

    flag_frame = deterioration_df[factor_flag_cols].copy()
    valid_factor_count = flag_frame.notna().sum(axis=1)
    deteriorated_factor_count = flag_frame.fillna(False).astype(int).sum(axis=1)
    deterioration_ratio = deteriorated_factor_count / valid_factor_count.replace({0: np.nan})
    stock_deteriorated = deterioration_ratio >= float(g.regime_stock_deterioration_threshold)
    eligible_stock_mask = valid_factor_count >= int(g.regime_min_valid_factor_count)
    eligible_stock_count = int(eligible_stock_mask.sum())
    deteriorated_stock_count = int((stock_deteriorated & eligible_stock_mask).sum())
    deteriorated_stock_ratio = (
        float(deteriorated_stock_count) / float(eligible_stock_count)
        if eligible_stock_count > 0 else 0.0
    )

    defensive_weight_raw = deteriorated_stock_ratio ** float(g.regime_weight_power)
    defensive_weight = float(np.clip(defensive_weight_raw, g.regime_weight_floor, g.regime_weight_cap))
    equity_weight = float(np.clip(1.0 - defensive_weight, 0.0, 1.0))
    regime_name = 'pool_yoy_deterioration'

    summary_parts = [
        'compare_mode=%s' % g.regime_compare_mode,
        'pool=%d' % len(stocks),
        'eligible=%d' % eligible_stock_count,
        'deteriorated=%d' % deteriorated_stock_count,
        'stock_ratio=%.3f' % deteriorated_stock_ratio,
        'equity_weight=%.3f' % equity_weight,
        'treasury_weight=%.3f' % defensive_weight,
    ]
    if factor_breadth_parts:
        summary_parts.append('factor_breadth=' + '|'.join(factor_breadth_parts))
    return {
        'regime_name': regime_name,
        'equity_weight': equity_weight,
        'defensive_weight': defensive_weight,
        'defensive_asset': resolve_defensive_asset(g.defensive_asset, equity_weight),
        'summary': ' ; '.join(summary_parts),
    }


def compute_factor_deterioration_flag(current_series, reference_series, direction_sign):
    current_series = pd.to_numeric(current_series, errors='coerce') if current_series is not None else pd.Series(dtype=float)
    reference_series = pd.to_numeric(reference_series, errors='coerce') if reference_series is not None else pd.Series(dtype=float)
    paired = pd.concat(
        [
            current_series.rename('current'),
            reference_series.rename('reference'),
        ],
        axis=1,
    ).dropna()
    result = pd.Series(index=current_series.index.union(reference_series.index), dtype='float64')
    if paired.empty:
        return result

    if int(direction_sign) > 0:
        deteriorated = paired['current'] < paired['reference']
    else:
        deteriorated = paired['current'] > paired['reference']
    result.loc[paired.index] = deteriorated.astype(float)
    return result


def resolve_defensive_asset(asset_code, equity_weight):
    if asset_code is None or equity_weight >= 1.0:
        return None
    current_data = get_current_data()
    try:
        asset_data = current_data[asset_code]
    except Exception:
        return None
    if asset_data is None or asset_data.paused:
        return None
    return asset_code


def execute_target_weights(context, long_list, target_weight, defensive_asset, defensive_weight):
    target_value_map = {
        stock: context.portfolio.total_value * target_weight
        for stock in long_list
    }
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


def get_active_plan(factor_date):
    date_value = to_date(factor_date)
    for plan in g.annual_plan_library:
        start_date = plan['effective_start']
        end_date = plan['effective_end']
        if date_value < start_date:
            continue
        if end_date is not None and date_value > end_date:
            continue
        return plan
    return None


def get_current_bank_source_year(factor_date):
    date_value = to_date(factor_date)
    if date_value is None:
        return None
    if date_value.year <= 2021:
        return 2020
    if date_value.year == 2022:
        return 2021
    if date_value.year == 2023:
        return 2022
    return 2023


def build_manual_bank_indicator_data():
    df = pd.read_csv(StringIO(MANUAL_BANK_INDICATOR_CSV))
    data = {}
    for _, row in df.iterrows():
        code = row['code']
        source_year = int(row['source_year'])
        data.setdefault(code, {})[source_year] = {
            'Nonperforming_loan_rate': safe_float(row['Nonperforming_loan_rate']),
            'capital_adequacy_ratio': safe_float(row['capital_adequacy_ratio']),
            'deposit_loan_ratio': safe_float(row['deposit_loan_ratio']),
            'non_performing_loan_provision_coverage': safe_float(row['non_performing_loan_provision_coverage']),
        }
    return data


def get_previous_rebalance_factor_date(factor_date):
    date_value = to_date(factor_date)
    window_start = date_value - timedelta(days=450)
    trade_days = get_trade_days(start_date=window_start, end_date=date_value)
    monthly_first_days = first_trade_days_by_month(trade_days)
    eligible = [d for d in monthly_first_days if d.month in g.rebalance_months and d < date_value]
    if len(eligible) >= 2:
        return eligible[-2]
    if len(eligible) == 1:
        return eligible[0]
    return None


def get_yoy_snapshot_factor_date(factor_date):
    date_value = to_date(factor_date)
    target_start = datetime(date_value.year - 1, date_value.month, 1).date()
    if date_value.month == 12:
        target_end = datetime(date_value.year, 1, 1).date() - timedelta(days=1)
    else:
        target_end = datetime(date_value.year - 1, date_value.month + 1, 1).date() - timedelta(days=1)
    trade_days = get_trade_days(start_date=target_start, end_date=target_end)
    if trade_days is None or len(trade_days) == 0:
        return None
    return to_date(trade_days[0])


def first_trade_days_by_month(trade_days):
    result = []
    seen = set()
    for day in trade_days:
        day = to_date(day)
        key = (day.year, day.month)
        if key in seen:
            continue
        seen.add(key)
        result.append(day)
    return result


def get_previous_trade_date(context):
    try:
        return to_date(context.previous_date)
    except Exception:
        trade_days = get_trade_days(end_date=context.current_dt.date(), count=2)
        if trade_days is None or len(trade_days) == 0:
            return context.current_dt.date()
        return to_date(trade_days[0])


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
            if 'ST' in data.name or '*' in data.name or '退' in data.name:
                continue
            tradable.append(stock)
        except Exception:
            continue
    return tradable


def safe_float(value):
    try:
        if value is None or pd.isna(value):
            return None
        value = float(value)
        if np.isinf(value):
            return None
        return value
    except Exception:
        return None


def winsorize_series(series, lower=0.05, upper=0.95):
    series = pd.to_numeric(series, errors='coerce')
    if series.notna().sum() < 5:
        return series
    low = series.quantile(lower)
    high = series.quantile(upper)
    return series.clip(lower=low, upper=high)


def zscore_series(series):
    series = pd.to_numeric(series, errors='coerce')
    if series.notna().sum() < 3:
        return pd.Series(index=series.index, data=np.nan)
    std = series.std()
    mean = series.mean()
    if std is None or pd.isna(std) or abs(std) < 1e-12:
        return pd.Series(index=series.index, data=np.nan)
    return (series - mean) / std


def assign_groups(values, group_count):
    ranked = pd.Series(values).rank(method='first')
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates='drop') + 1
    except ValueError:
        return pd.Series(index=ranked.index, dtype='float64')


def safe_divide(numerator, denominator):
    if numerator is None or denominator is None:
        return pd.Series(dtype='float64')
    numerator = pd.to_numeric(numerator, errors='coerce')
    denominator = pd.to_numeric(denominator, errors='coerce').replace({0: np.nan})
    return numerator / denominator


def safe_subtract(left, right):
    if left is None:
        return pd.Series(dtype='float64')
    left = pd.to_numeric(left, errors='coerce')
    if right is None:
        return pd.Series(index=left.index, data=np.nan)
    right = pd.to_numeric(right, errors='coerce')
    return left - right


def to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, 'date'):
        return value.date()
    return pd.Timestamp(value).date()


def after_trading_end(context):
    if not g.debug:
        return
    current_date = context.current_dt.date()
    if current_date == datetime(2026, 5, 31).date():
        log.info('========== V4 annual defensive candidate usage ==========')
        for item in g.plan_usage_log:
            log.info(str(item))
        log.info('========== V4 annual defensive candidate regime log ==========')
        for item in g.regime_history_log:
            log.info(str(item))
