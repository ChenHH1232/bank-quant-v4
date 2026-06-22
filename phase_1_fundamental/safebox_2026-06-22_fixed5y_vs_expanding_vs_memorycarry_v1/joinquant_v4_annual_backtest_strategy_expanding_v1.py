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

    g.rebalance_months = [5, 9, 11]
    g.group_count = 5
    g.hold_bucket = 5
    # 'benchmark' = expanding base_core_7 equal-weight line
    # 'primary' = expanding base_plus_top2_9 ic-weight line
    g.strategy_line = 'benchmark'
    g.debug = True

    g.annual_plan_library = build_annual_plan_library()
    g.manual_bank_indicator_data = build_manual_bank_indicator_data()
    g.executed_rebalance_keys = set()
    g.plan_usage_log = []

    run_daily(maybe_rebalance, time='09:40')


def build_annual_plan_library():
    return [
        {
            'plan_id': 'expanding_01',
            'effective_start': datetime.strptime('2021-05-06', '%Y-%m-%d').date(),
            'effective_end': datetime.strptime('2022-05-04', '%Y-%m-%d').date(),
            'benchmark_factors': [
                factor_spec('indicator__roe', 1, 1.0),
                factor_spec('indicator__eps', 1, 1.0),
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 1.0),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 1.0),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 1.0),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 1.0),
            ],
            'primary_factors': [
                factor_spec('indicator__roe', 1, 0.105681),
                factor_spec('indicator__eps', 1, 0.073011),
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 0.191488),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.050207),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.137916),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.125512),
                factor_spec('improve__annual_delta__bank_indicator__Nonperforming_loan_rate', -1, 0.082644),
                factor_spec('improve__snapshot_delta__derived__investment_income_to_operating_revenue', -1, 0.027117),
                factor_spec('bank_indicator__non_interest_income_ratio', 1, 0.064595),
                factor_spec('bank_indicator__net_interest_margin', 1, 0.178425),
            ],
        },
        {
            'plan_id': 'expanding_02',
            'effective_start': datetime.strptime('2022-05-05', '%Y-%m-%d').date(),
            'effective_end': datetime.strptime('2023-05-03', '%Y-%m-%d').date(),
            'benchmark_factors': [
                factor_spec('indicator__roe', 1, 1.0),
                factor_spec('indicator__eps', 1, 1.0),
                factor_spec('derived__log_total_assets', 1, 1.0),
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 1.0),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 1.0),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 1.0),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 1.0),
            ],
            'primary_factors': [
                factor_spec('indicator__roe', 1, 0.120472),
                factor_spec('indicator__eps', 1, 0.082579),
                factor_spec('derived__log_total_assets', 1, 0.115672),
                factor_spec('bank_indicator__Nonperforming_loan_rate', -1, 0.232146),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.135596),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.171640),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.143941),
                factor_spec('improve__snapshot_delta__derived__investment_income_to_operating_revenue', -1, 0.062863),
                factor_spec('bank_indicator__core_level_capital_adequacy_ratio', 1, 0.060200),
                factor_spec('improve__annual_delta__bank_indicator__capital_adequacy_ratio', -1, 0.208539),
            ],
        },
        {
            'plan_id': 'expanding_03',
            'effective_start': datetime.strptime('2023-05-04', '%Y-%m-%d').date(),
            'effective_end': datetime.strptime('2024-05-05', '%Y-%m-%d').date(),
            'benchmark_factors': [
                factor_spec('derived__log_total_assets', 1, 1.0),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 1.0),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 1.0),
            ],
            'primary_factors': [
                factor_spec('derived__log_total_assets', 1, 0.094632),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.183065),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.138938),
                factor_spec('indicator__inc_net_profit_to_shareholders_annual', 1, 0.025023),
                factor_spec('bank_indicator__core_level_capital_adequacy_ratio', 1, 0.039272),
            ],
        },
        {
            'plan_id': 'expanding_04',
            'effective_start': datetime.strptime('2024-05-06', '%Y-%m-%d').date(),
            'effective_end': datetime.strptime('2025-05-05', '%Y-%m-%d').date(),
            'benchmark_factors': [
                factor_spec('derived__log_total_assets', 1, 1.0),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 1.0),
            ],
            'primary_factors': [
                factor_spec('derived__log_total_assets', 1, 0.108582),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.160937),
                factor_spec('improve__annual_delta__bank_indicator__Nonperforming_loan_rate', -1, 0.078237),
                factor_spec('bank_indicator__cost_to_income_ratio', -1, 0.020471),
                factor_spec('bank_indicator__core_level_capital_adequacy_ratio', 1, 0.064819),
                factor_spec('improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual', -1, 0.030610),
            ],
        },
        {
            'plan_id': 'expanding_05',
            'effective_start': datetime.strptime('2025-05-06', '%Y-%m-%d').date(),
            'effective_end': None,
            'benchmark_factors': [
                factor_spec('derived__log_total_assets', 1, 1.0),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 1.0),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 1.0),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 1.0),
            ],
            'primary_factors': [
                factor_spec('derived__log_total_assets', 1, 0.112759),
                factor_spec('bank_indicator__non_performing_loan_provision_coverage', 1, 0.071226),
                factor_spec('bank_indicator__deposit_loan_ratio', -1, 0.157623),
                factor_spec('bank_indicator__capital_adequacy_ratio', 1, 0.170260),
                factor_spec('bank_indicator__cost_to_income_ratio', -1, 0.013324),
                factor_spec('bank_indicator__core_level_capital_adequacy_ratio', 1, 0.093597),
                factor_spec('improve__season_yoy_delta__derived__staff_cash_to_operating_revenue', -1, 0.037468),
                factor_spec('improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual', -1, 0.030264),
            ],
        },
    ]


MANUAL_BANK_INDICATOR_CSV = '''code,source_year,bank_indicator__Nonperforming_loan_rate,bank_indicator__capital_adequacy_ratio,bank_indicator__core_level_capital_adequacy_ratio,bank_indicator__cost_to_income_ratio,bank_indicator__deposit_loan_ratio,bank_indicator__net_interest_margin,bank_indicator__non_interest_income_ratio,bank_indicator__non_performing_loan_provision_coverage
000001.XSHE,2021,1.18,13.29,8.69,29.11,98.9006,2.88,35.1,201.4
000001.XSHE,2022,1.02,13.34,8.6,28.3,102.4387,2.79,28.96,288.42
000001.XSHE,2023,1.05,13.01,8.64,27.45,99.3108,2.75,27.66,290.28
001227.XSHE,2023,1.71,11.27,8.47,31.24,71.41,1.58,20.971,194.99
002142.XSHE,2019,0.78,14.86,9.16,34.44,65.88,2.23,33.9093,521.83
002142.XSHE,2020,0.78,15.57,9.62,34.32,66.51,2.27,36.612,524.08
002142.XSHE,2021,0.79,14.84,9.52,37.96,71.85,2.3,32.23,505.59
002142.XSHE,2022,0.77,15.43,10.16,36.95,79.75,2.21,38.04,525.52
002142.XSHE,2023,0.75,15.18,9.75,37.29,79.79,2.02,35.1734,504.9
002807.XSHE,2019,2.15,15.21,14.02,32.03,74.31,2.67,26.4985,233.71
002807.XSHE,2020,1.83,15.29,14.16,31.66,75.39,2.46,27.374,259.13
002807.XSHE,2021,1.79,14.48,13.34,31.47,77.84,2.19,23.6368,224.27
002807.XSHE,2022,1.32,14.11,12.96,33.4,79.92,2.14,15.914,330.62
002807.XSHE,2023,0.98,13.9,12.77,30.39,81.39,2.18,15.5142,469.62
002839.XSHE,2019,1.47,15.65,11.94,35.43,75.67,2.56,9.1045,223.85
002839.XSHE,2020,1.38,15.1,11.02,31.15,78.64,2.74,17.3945,252.14
002839.XSHE,2021,1.17,13.75,10.35,31.27,79.18,2.74,14.1519,307.83
002839.XSHE,2022,0.95,14.3,9.82,31.11,82.4,2.43,20.0403,475.35
002839.XSHE,2023,0.89,13.13,9.36,32.61,82.41,2.25,18.863,521.09
002936.XSHE,2019,2.47,13.15,8.22,27.96,66.06,1.7,40.4608,154.84
002936.XSHE,2020,2.37,12.11,7.98,26.46,72.33,2.16,33.3857,159.85
002936.XSHE,2021,2.08,12.86,8.92,22.4,82.63,2.4,23.054,160.44
002936.XSHE,2022,1.85,15.0,9.49,22.98,90.66,2.31,19.27,156.58
002936.XSHE,2023,1.88,12.72,9.29,22.99,97.99,2.27,18.86,165.73
002948.XSHE,2020,1.65,14.76,8.36,31.88,80.5698,2.13,28.81,155.09
002948.XSHE,2021,1.51,14.11,8.35,33.61,75.3022,2.13,22.71,169.62
002948.XSHE,2022,1.34,15.83,8.38,33.91,77.0633,1.79,31.34,197.42
002948.XSHE,2023,1.21,13.56,8.75,34.97,77.4697,1.76,28.82,219.77
002958.XSHE,2020,1.46,12.26,10.48,30.25,81.6748,2.61,18.7746,310.23
002958.XSHE,2021,1.44,12.32,9.73,28.79,87.061,2.52,15.526,278.73
002958.XSHE,2022,1.74,13.07,9.62,29.22,86.5109,2.16,21.8371,231.77
002958.XSHE,2023,2.19,13.18,9.77,30.34,83.8858,2.0,21.1669,207.63
002966.XSHE,2020,1.53,14.36,11.3,31.68,74.06,2.21,31.8334,224.07
002966.XSHE,2021,1.38,14.21,11.26,29.74,77.18,2.22,27.3883,291.74
002966.XSHE,2022,1.11,13.06,10.37,32.02,78.59,1.91,30.44,422.91
002966.XSHE,2023,0.88,12.92,9.63,33.33,79.23,1.87,29.09,530.81
600000.XSHG,2019,1.9,13.67,10.09,24.9,110.6095,2.13,34.8,156.08
600000.XSHG,2020,2.03,13.86,10.26,22.58,109.942,2.34,32.43,134.94
600000.XSHG,2021,1.73,14.64,9.51,23.78,109.9836,2.02,29.43,152.77
600000.XSHG,2022,1.61,14.01,9.4,26.17,107.2236,1.83,28.81,143.96
600000.XSHG,2023,1.52,13.65,9.19,27.89,100.14,1.77,29.1339,159.04
600015.XSHG,2019,1.85,13.19,9.47,32.58,95.05,2.19,28.6444,158.59
600015.XSHG,2020,1.83,13.89,9.25,30.59,98.86,2.51,23.81,141.92
600015.XSHG,2021,1.8,13.08,8.79,27.93,99.95,2.59,13.9987,147.22
600015.XSHG,2022,1.77,12.82,8.78,29.06,99.19,2.35,16.97,150.99
600015.XSHG,2023,1.75,13.27,9.24,30.13,93.35,2.1,20.8031,159.88
600016.XSHG,2019,1.76,11.75,8.93,30.07,96.5098,1.77,51.09,134.05
600016.XSHG,2020,1.56,13.17,8.89,26.74,95.8913,2.14,45.72,155.5
600016.XSHG,2021,1.82,13.04,8.51,26.19,102.2764,2.14,26.89,139.38
600016.XSHG,2022,1.79,13.64,9.04,29.17,105.7506,1.91,25.49,145.3
600016.XSHG,2023,1.68,13.14,9.17,35.61,102.9378,1.6,24.57,142.49
600036.XSHG,2019,1.36,15.68,11.78,31.02,88.8306,2.57,35.47,358.18
600036.XSHG,2020,1.16,15.54,11.95,32.09,92.6973,2.59,35.82,426.78
600036.XSHG,2021,1.07,16.54,12.29,33.3,89.3537,2.49,36.3,437.68
600036.XSHG,2022,0.91,17.48,12.66,33.12,87.7575,2.48,38.44,483.87
600036.XSHG,2023,0.96,17.77,13.68,32.88,80.3034,2.4,36.7,450.79
600908.XSHG,2019,1.24,16.81,10.44,29.18,65.06,2.16,6.3646,234.76
600908.XSHG,2020,1.21,15.85,10.2,29.66,66.25,2.02,16.2517,288.18
600908.XSHG,2021,1.1,15.21,9.03,27.15,70.54,2.07,15.8781,355.88
600908.XSHG,2022,0.93,14.35,8.74,28.77,75.14,1.95,19.433,477.19
600908.XSHG,2023,0.81,14.75,10.97,30.98,74.48,1.81,22.1486,552.74
600919.XSHG,2019,1.39,12.55,8.61,28.68,78.53,1.8692,27.7569,203.84
600919.XSHG,2020,1.38,12.89,8.59,25.64,82.67,1.94,43.2191,232.79
600919.XSHG,2021,1.32,14.47,9.25,23.46,88.71,2.14,28.9079,256.4
600919.XSHG,2022,1.08,13.38,8.78,22.44,93.21,2.28,28.6832,318.93
600919.XSHG,2023,0.94,13.07,8.79,24.52,93.52,2.32,25.9408,371.66
600926.XSHG,2020,1.34,13.54,8.08,28.71,67.23,1.85,27.07,316.71
600926.XSHG,2021,1.07,14.41,8.53,26.35,68.91,1.98,22.31,469.54
600926.XSHG,2022,0.86,13.62,8.43,27.3,72.51,1.83,28.36,567.71
600926.XSHG,2023,0.77,12.89,8.08,29.64,74.77,1.69,30.59,565.1
600928.XSHG,2020,1.18,14.85,12.62,25.68,87.63,2.27,17.8881,262.41
600928.XSHG,2021,1.18,14.5,12.37,25.33,79.98,2.16,13.0367,269.39
600928.XSHG,2022,1.32,14.12,12.09,26.06,78.33,1.91,16.8024,224.21
600928.XSHG,2023,1.25,12.84,10.48,28.92,66.67,1.66,16.1372,201.63
601009.XSHG,2019,0.89,12.99,8.51,28.61,62.34,1.89,21.31,462.68
601009.XSHG,2020,0.89,13.03,8.87,27.39,66.93,1.86,34.1,417.73
601009.XSHG,2021,0.91,14.75,9.97,28.46,71.33,2.25,31.25,391.76
601009.XSHG,2022,0.91,13.54,10.16,29.22,73.77,2.25,33.77,397.34
601009.XSHG,2023,0.9,14.31,9.73,29.75,76.44,2.19,39.54,397.2
601077.XSHG,2020,1.25,14.88,12.42,28.54,64.91,2.33,12.54,380.31
601077.XSHG,2021,1.31,14.28,11.96,27.09,70.05,2.25,13.9689,314.95
601077.XSHG,2022,1.25,14.77,12.47,27.52,76.67,2.17,14.94,340.25
601077.XSHG,2023,1.22,15.62,13.1,31.84,76.69,1.97,12.3712,357.74
601128.XSHG,2019,0.99,15.12,10.49,36.53,82.05,3.43,12.41,445.02
601128.XSHG,2020,0.96,15.1,12.44,38.24,81.62,3.45,10.0102,481.28
601128.XSHG,2021,0.96,13.53,11.08,42.77,82.95,3.18,9.3536,485.33
601128.XSHG,2022,0.81,11.95,10.21,41.4,89.09,3.06,12.5933,531.82
601128.XSHG,2023,0.81,13.87,10.21,38.58,90.62,3.02,13.5918,536.77
601166.XSHG,2019,1.57,12.2,9.3,26.89,88.8171,1.83,39.5674,207.28
601166.XSHG,2020,1.54,13.36,9.47,26.03,90.6878,2.25,32.5518,199.13
601166.XSHG,2021,1.25,13.47,9.33,24.16,97.0969,2.36,29.3506,218.83
601166.XSHG,2022,1.1,14.39,9.81,25.68,101.663,2.29,34.15,268.73
601166.XSHG,2023,1.09,14.44,9.81,29.37,96.21,2.1,34.6718,236.44
601169.XSHG,2019,1.46,12.07,8.93,25.19,91.0394,1.88,17.9048,217.51
601169.XSHG,2020,1.4,12.28,9.22,23.23,93.6101,1.96,21.464,224.69
601169.XSHG,2021,1.57,11.49,9.42,22.07,94.6606,1.93,19.7421,215.95
601169.XSHG,2022,1.44,14.63,9.86,24.96,97.0647,1.83,22.4489,210.22
601169.XSHG,2023,1.43,14.04,9.54,26.55,92.6449,1.76,22.36,210.04
601187.XSHG,2021,0.98,14.49,11.34,28.64,90.6578,1.65,16.9858,368.03
601187.XSHG,2022,0.91,16.4,10.47,34.56,94.3487,1.62,16.6536,370.64
601187.XSHG,2023,0.86,13.76,9.5,34.3,96.7975,1.53,18.753,387.93
601229.XSHG,2019,1.14,13.0,9.83,20.52,81.61,1.81,31.79,332.95
601229.XSHG,2020,1.16,13.84,9.66,19.98,81.89,1.78,39.12,337.15
601229.XSHG,2021,1.22,12.86,9.34,18.93,83.21,1.82,28.28,321.38
601229.XSHG,2022,1.25,12.16,8.95,21.52,83.59,1.74,28.09,301.13
601229.XSHG,2023,1.25,13.16,9.14,23.02,81.22,1.54,28.45,291.61
601288.XSHG,2019,1.59,15.12,11.55,31.27,68.835,2.33,20.1855,252.18
601288.XSHG,2020,1.4,16.13,11.24,30.49,72.0511,2.23,22.3823,295.45
601288.XSHG,2021,1.57,16.59,11.04,29.23,74.4638,2.2,17.1563,266.2
601288.XSHG,2022,1.43,17.13,11.44,30.46,78.3995,2.12,19.7145,299.73
601288.XSHG,2023,1.37,17.2,11.15,32.81,78.6744,1.9,18.6106,302.6
601328.XSHG,2019,1.49,14.37,11.16,31.5,84.7976,1.51,38.4408,173.13
601328.XSHG,2020,1.47,14.83,11.22,30.11,87.3432,1.58,38.0214,171.77
601328.XSHG,2021,1.67,15.25,10.87,26.81,88.5142,1.57,37.7189,143.87
601328.XSHG,2022,1.48,15.45,10.62,27.67,93.1905,1.56,39.9781,166.5
601328.XSHG,2023,1.35,14.97,10.06,29.65,92.005,1.48,31.8392,180.68
601398.XSHG,2019,1.52,15.39,12.98,23.91,71.0,2.36,26.0111,175.76
601398.XSHG,2020,1.43,16.77,13.2,23.27,71.6,2.3,29.0,199.32
601398.XSHG,2021,1.58,16.88,13.18,22.3,72.8,2.15,26.7,180.68
601398.XSHG,2022,1.42,18.02,13.31,23.97,77.3,2.11,26.74,205.84
601398.XSHG,2023,1.38,19.26,14.04,26.05,76.7,1.92,24.4,209.47
601528.XSHG,2022,1.25,18.85,15.41,32.22,84.51,2.34,9.5039,252.9
601528.XSHG,2023,1.08,15.58,14.42,33.3,80.17,2.21,9.5464,280.5
601577.XSHG,2019,1.29,12.24,9.53,34.12,59.26,2.45,17.1493,275.4
601577.XSHG,2020,1.22,13.25,9.16,30.72,66.8,2.6,22.4292,279.98
601577.XSHG,2021,1.21,13.6,8.61,29.69,66.64,2.58,16.9862,292.68
601577.XSHG,2022,1.2,13.66,9.69,28.44,69.7,2.4,22.79,297.87
601577.XSHG,2023,1.16,13.41,9.7,28.3,70.25,2.41,21.429,311.09
601658.XSHG,2020,0.86,13.52,9.9,56.57,53.41,2.53,13.2167,389.45
601658.XSHG,2021,0.88,13.88,9.6,57.88,55.19,2.42,11.47,408.06
601658.XSHG,2022,0.82,14.78,9.92,59.01,56.84,2.36,15.49,418.61
601658.XSHG,2023,0.84,13.82,9.36,61.41,56.71,2.2,18.3197,385.51
601665.XSHG,2022,1.35,15.31,9.65,26.27,58.5,2.02,26.3779,253.95
601665.XSHG,2023,1.29,14.47,9.56,26.46,73.58,1.96,22.4951,281.06
601818.XSHG,2019,1.59,13.01,9.15,28.79,94.1433,1.97,44.6292,176.16
601818.XSHG,2020,1.56,13.47,9.2,27.29,89.8709,2.31,23.2615,181.62
601818.XSHG,2021,1.38,13.9,9.02,26.41,86.4628,2.29,22.3064,182.71
601818.XSHG,2022,1.25,13.37,8.91,28.02,89.9765,2.16,26.5766,187.02
601818.XSHG,2023,1.25,12.95,8.72,27.88,91.4572,2.01,25.0455,187.93
601825.XSHG,2022,0.95,15.28,13.06,29.95,71.7326,1.86,19.84,442.5
601825.XSHG,2023,0.94,15.46,12.96,30.5,69.7571,1.83,19.01,445.32
601838.XSHG,2019,1.54,14.08,11.14,25.77,53.72,2.21,16.5314,237.01
601838.XSHG,2020,1.43,15.69,10.13,26.52,62.27,2.16,18.89,253.88
601838.XSHG,2021,1.37,14.23,9.26,23.87,66.66,2.19,18.9923,293.43
601838.XSHG,2022,0.98,13.0,8.7,22.8,74.76,2.3714,19.3877,402.88
601838.XSHG,2023,0.78,13.15,8.47,24.39,77.57,2.04,18.3918,501.57
601916.XSHG,2020,1.37,14.24,9.64,26.24,84.4,2.39,26.94,220.8
601916.XSHG,2021,1.42,12.93,8.75,25.96,83.7,2.19,22.24,191.01
601916.XSHG,2022,1.53,12.89,8.13,25.31,91.0,2.27,22.98,174.61
601916.XSHG,2023,1.47,11.6,8.05,27.46,84.82,2.21,22.96,182.19
601939.XSHG,2019,1.46,17.19,13.83,26.42,80.568,2.36,26.1975,208.37
601939.XSHG,2020,1.42,17.52,13.88,26.53,77.68,2.32,27.63,227.69
601939.XSHG,2021,1.56,17.06,13.62,25.12,78.49,2.19,23.81,213.59
601939.XSHG,2022,1.42,17.85,13.59,27.43,84.04299999999999,2.13,26.55,239.96
601939.XSHG,2023,1.38,18.42,13.69,27.83,84.71799999999999,2.01,17.0329,241.53
601963.XSHG,2022,1.3,12.99,9.36,21.44,93.91,2.06,20.1062,274.01
601963.XSHG,2023,1.38,12.72,9.52,25.25,92.15,1.74,19.73,211.19
601988.XSHG,2019,1.42,14.97,11.41,28.09,79.4114,1.95,28.64,181.97
601988.XSHG,2020,1.37,15.59,11.3,28.0,82.6221,1.89,31.85,182.86
601988.XSHG,2021,1.46,16.22,11.28,26.73,84.225,1.85,26.46,177.84
601988.XSHG,2022,1.33,16.53,11.3,28.17,82.5,1.75,29.79,187.05
601988.XSHG,2023,1.32,17.52,11.84,28.92,82.9,1.75,25.46,188.73
601997.XSHG,2019,1.35,12.97,9.61,26.73,54.5,2.33,12.4876,266.05
601997.XSHG,2020,1.45,13.61,9.39,26.3,61.37,2.4,16.0068,291.86
601997.XSHG,2021,1.53,12.88,9.3,23.84,65.05,2.52,14.697,277.3
601997.XSHG,2022,1.45,13.96,10.62,27.46,70.88,2.26,13.4049,271.03
601997.XSHG,2023,1.45,14.16,10.95,26.8,74.36,2.27,11.5809,260.86
601998.XSHG,2019,1.77,12.47,8.62,30.57,54.1,2.31,31.5,157.98
601998.XSHG,2020,1.65,12.44,8.69,27.7,98.1521,2.45,32.2,175.25
601998.XSHG,2021,1.64,13.01,8.74,26.65,97.8352,2.26,22.7,171.68
601998.XSHG,2022,1.39,13.53,8.85,29.2,101.3779,2.05,27.7,180.07
601998.XSHG,2023,1.27,13.18,8.74,30.53,100.2344,1.97,28.74,201.19
603323.XSHG,2019,1.31,14.89,10.99,34.18,71.92,2.84,14.7714,248.18
603323.XSHG,2020,1.33,14.67,12.17,34.61,72.38,2.71,16.7464,249.32
603323.XSHG,2021,1.28,13.53,11.38,32.72,73.61,2.5,19.9898,305.31
603323.XSHG,2022,1.0,12.99,10.72,32.88,77.68,2.24,20.8294,412.22
603323.XSHG,2023,0.95,12.09,10.17,34.1,78.0,2.04,22.2867,442.83
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
        log.info('No expanding annual plan available for %s' % str(factor_date))
        return

    factor_specs = plan['primary_factors'] if g.strategy_line == 'primary' else plan['benchmark_factors']
    tradable = get_tradable_stocks(context, g.bank_stocks)
    if len(tradable) < g.group_count:
        log.info('Tradable bank count is too small: %d' % len(tradable))
        return

    score_df = build_score_frame(tradable, factor_date, factor_specs)
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
    target_weight = 1.0 / float(len(long_list))

    if g.debug:
        log.info('========== V4 annual rebalance expanding ==========')
        log.info('current_date=%s factor_date=%s plan=%s line=%s' % (
            str(context.current_dt.date()),
            str(factor_date),
            plan['plan_id'],
            g.strategy_line,
        ))
        log.info('selected_count=%d long_list=%s' % (len(long_list), str(long_list)))
        log.info('top_score_preview=%s' % build_score_preview(score_df.head(10)))

    execute_target_weights(context, long_list, target_weight)
    g.plan_usage_log.append({
        'rebalance_date': str(context.current_dt.date()),
        'factor_date': str(factor_date),
        'plan_id': plan['plan_id'],
        'strategy_line': g.strategy_line,
        'holding_count': len(long_list),
        'holdings': '|'.join(long_list),
    })


def build_score_frame(stocks, factor_date, factor_specs):
    current_snapshot = fetch_current_snapshot_factors(stocks, factor_date)
    if current_snapshot.empty:
        return pd.DataFrame()

    previous_rebalance_date = get_previous_rebalance_factor_date(factor_date)
    previous_snapshot = fetch_current_snapshot_factors(stocks, previous_rebalance_date) if previous_rebalance_date else pd.DataFrame()
    yoy_snapshot_date = get_yoy_snapshot_factor_date(factor_date)
    yoy_snapshot = fetch_current_snapshot_factors(stocks, yoy_snapshot_date) if yoy_snapshot_date else pd.DataFrame()

    current_bank_source_year = get_current_bank_source_year(factor_date)
    previous_bank_source_year = current_bank_source_year - 1 if current_bank_source_year is not None else None
    current_bank = fetch_bank_indicator_snapshot(stocks, current_bank_source_year)
    previous_bank = fetch_bank_indicator_snapshot(stocks, previous_bank_source_year) if previous_bank_source_year is not None else pd.DataFrame()

    score_df = pd.DataFrame(index=stocks)
    score_df['code'] = score_df.index

    for spec in factor_specs:
        factor_name = spec['name']
        raw_series = compute_factor_series(
            factor_name=factor_name,
            current_snapshot=current_snapshot,
            previous_snapshot=previous_snapshot,
            yoy_snapshot=yoy_snapshot,
            current_bank=current_bank,
            previous_bank=previous_bank,
        )
        if raw_series is None:
            continue
        raw_series = raw_series.reindex(stocks)
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
            continue
        weight = float(spec['train_ic'])
        valid_series = pd.to_numeric(score_df[adj_col], errors='coerce')
        weighted_part = valid_series * weight
        weighted_score = weighted_part if weighted_score is None else (weighted_score + weighted_part)
        factor_count = valid_series.notna().astype(int) if factor_count is None else (factor_count + valid_series.notna().astype(int))
        weight_sum += weight
        valid_factor_names.append(factor_name)

    if weighted_score is None or weight_sum <= 0:
        return pd.DataFrame()

    score_df['final_score'] = weighted_score / weight_sum
    score_df['factor_count'] = factor_count
    score_df = score_df.dropna(subset=['final_score']).copy()
    min_required = min(2, len(valid_factor_names)) if valid_factor_names else 0
    if min_required > 0:
        score_df = score_df[score_df['factor_count'] >= min_required].copy()
    return score_df


def compute_factor_series(factor_name, current_snapshot, previous_snapshot, yoy_snapshot, current_bank, previous_bank):
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
    if factor_name == 'bank_indicator__core_level_capital_adequacy_ratio':
        return current_bank.get('bank_indicator__core_level_capital_adequacy_ratio')
    if factor_name == 'bank_indicator__cost_to_income_ratio':
        return current_bank.get('bank_indicator__cost_to_income_ratio')
    if factor_name == 'bank_indicator__deposit_loan_ratio':
        return current_bank.get('bank_indicator__deposit_loan_ratio')
    if factor_name == 'bank_indicator__net_interest_margin':
        return current_bank.get('bank_indicator__net_interest_margin')
    if factor_name == 'bank_indicator__non_interest_income_ratio':
        return current_bank.get('bank_indicator__non_interest_income_ratio')
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
        query(balance.code, balance.total_assets).filter(balance.code.in_(stocks)),
        date=factor_date,
    )
    if balance_df is not None and len(balance_df) > 0:
        balance_df = balance_df.set_index('code')
        result['balance__total_assets'] = pd.to_numeric(balance_df['total_assets'], errors='coerce')

    income_df = get_fundamentals(
        query(income.code, income.operating_revenue, income.investment_income).filter(income.code.in_(stocks)),
        date=factor_date,
    )
    if income_df is not None and len(income_df) > 0:
        income_df = income_df.set_index('code')
        result['income__operating_revenue'] = pd.to_numeric(income_df['operating_revenue'], errors='coerce')
        result['income__investment_income'] = pd.to_numeric(income_df['investment_income'], errors='coerce')

    cash_flow_df = get_fundamentals(
        query(cash_flow.code, cash_flow.staff_behalf_paid).filter(cash_flow.code.in_(stocks)),
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
        row = {'code': stock}
        row.update(yearly_data)
        records.append(row)

    if not records:
        return result

    df = pd.DataFrame(records).set_index('code')
    for col in df.columns:
        result[col] = pd.to_numeric(df[col], errors='coerce')
    return result


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
                log.info('sell failed %s %s' % (stock, str(exc)))

    for stock in long_list:
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
    factor_columns = [col for col in df.columns if col not in ['code', 'source_year']]
    for _, row in df.iterrows():
        code = row['code']
        source_year = int(row['source_year'])
        yearly_data = {}
        for col in factor_columns:
            yearly_data[col] = safe_float(row[col])
        data.setdefault(code, {})[source_year] = yearly_data
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
        log.info('========== V4 annual expanding plan usage ==========')
        for item in g.plan_usage_log:
            log.info(str(item))
