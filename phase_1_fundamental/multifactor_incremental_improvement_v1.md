# Multifactor Incremental Improvement V1

Baseline reference:
- combo: `combo__quarterly_plus_annual`
- validation ic: `0.077992`
- validation top-bottom: `4.619e-05`

- Improvement candidates tested: `8`
- Positive delta candidates: `8`

Top candidates by validation delta:
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | best_combo=`combo__ic_weight` | delta_ic=`0.184577` | delta_spread=`0.00041684`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | best_combo=`combo__ic_weight` | delta_ic=`0.1681` | delta_spread=`0.00089143`
- `improve__annual_delta__bank_indicator__capital_adequacy_ratio` | best_combo=`combo__ic_weight` | delta_ic=`0.144278` | delta_spread=`0.00035559`
- `improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual` | best_combo=`combo__ic_weight` | delta_ic=`0.143145` | delta_spread=`0.00038412`
- `improve__annual_delta__bank_indicator__net_interest_margin` | best_combo=`combo__ic_weight` | delta_ic=`0.112125` | delta_spread=`0.00064028`
- `improve__season_yoy_delta__derived__staff_cash_to_operating_revenue` | best_combo=`combo__ic_weight` | delta_ic=`0.103504` | delta_spread=`0.00041956`
- `improve__season_yoy_delta__indicator__eps` | best_combo=`combo__ic_weight` | delta_ic=`0.094281` | delta_spread=`0.00032859`
- `improve__season_yoy_delta__indicator__roe` | best_combo=`combo__ic_weight` | delta_ic=`0.091043` | delta_spread=`0.00033132`

Outputs:
- [multifactor_incremental_improvement_v1.csv](D:\hh\codex\v4\phase_1_fundamental\multifactor_incremental_improvement_v1.csv)