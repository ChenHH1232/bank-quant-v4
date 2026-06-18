# Single-Factor Test Results Core V2

Scope:
- only `final_core_factor_pool_v2` factors
- includes `core_keep`, `secondary_candidate`, and `watch_only`

- Tested factors: `15`
- A: `9`
- B: `1`
- C: `5`
- D: `0`

## core_keep
- `bank_indicator__non_performing_loan_provision_coverage` | status=`A` | val_ic=`0.492055` | target=`y_year_avg_daily_return_close`
- `bank_indicator__Nonperforming_loan_rate` | status=`A` | val_ic=`0.440019` | target=`y_year_avg_daily_return_close`
- `bank_indicator__deposit_loan_ratio` | status=`A` | val_ic=`0.310985` | target=`y_year_avg_daily_return_close`
- `bank_indicator__capital_adequacy_ratio` | status=`A` | val_ic=`0.193768` | target=`y_year_avg_daily_return_close`
- `indicator__roe` | status=`A` | val_ic=`0.186312` | target=`y_quarter_avg_daily_return_close`
- `bank_indicator__non_interest_income_ratio` | status=`A` | val_ic=`0.051413` | target=`y_year_avg_daily_return_close`
- `derived__log_total_assets` | status=`A` | val_ic=`0.016987` | target=`y_quarter_avg_daily_return_close`
- `bank_indicator__net_interest_margin` | status=`A` | val_ic=`0.008822` | target=`y_year_avg_daily_return_close`
- `bank_indicator__core_level_capital_adequacy_ratio` | status=`C` | val_ic=`-0.026605` | target=`y_year_avg_daily_return_close`
- `indicator__inc_net_profit_to_shareholders_annual` | status=`C` | val_ic=`-0.071523` | target=`y_quarter_avg_daily_return_close`
- `bank_indicator__cost_to_income_ratio` | status=`C` | val_ic=`-0.107921` | target=`y_year_avg_daily_return_close`

## secondary_candidate
- `derived__investment_income_to_operating_revenue` | status=`C` | val_ic=`-0.011143` | target=`y_quarter_avg_daily_return_close`
- `derived__staff_cash_to_operating_revenue` | status=`C` | val_ic=`-0.046765` | target=`y_quarter_avg_daily_return_close`

## watch_only
- `indicator__eps` | status=`A` | val_ic=`0.253266` | target=`y_quarter_avg_daily_return_close`
- `income__minority_profit` | status=`B` | val_ic=`0.005915` | target=`y_quarter_avg_daily_return_close`

Output:
- [single_factor_test_results_core_v2.csv](D:\hh\codex\v4\phase_1_fundamental\single_factor_test_results_core_v2.csv)