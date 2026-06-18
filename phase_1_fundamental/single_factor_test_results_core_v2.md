# Single-Factor Test Results Core V2

Scope:
- only `final_core_factor_pool_v2` factors
- includes `core_keep`, `secondary_candidate`, and `watch_only`

- Tested factors: `15`
- A: `9`
- B: `0`
- C: `6`
- D: `0`

## core_keep
- `indicator__roe` | status=`A` | val_ic=`0.124165` | target=`y_quarter_avg_daily_return_close`
- `bank_indicator__cost_to_income_ratio` | status=`A` | val_ic=`0.101345` | target=`y_year_avg_daily_return_close`
- `bank_indicator__deposit_loan_ratio` | status=`A` | val_ic=`0.101253` | target=`y_year_avg_daily_return_close`
- `bank_indicator__capital_adequacy_ratio` | status=`A` | val_ic=`0.088512` | target=`y_year_avg_daily_return_close`
- `indicator__inc_net_profit_to_shareholders_annual` | status=`A` | val_ic=`0.074383` | target=`y_quarter_avg_daily_return_close`
- `derived__log_total_assets` | status=`A` | val_ic=`0.07015` | target=`y_quarter_avg_daily_return_close`
- `bank_indicator__Nonperforming_loan_rate` | status=`C` | val_ic=`-0.001882` | target=`y_year_avg_daily_return_close`
- `bank_indicator__non_performing_loan_provision_coverage` | status=`C` | val_ic=`-0.008149` | target=`y_year_avg_daily_return_close`
- `bank_indicator__core_level_capital_adequacy_ratio` | status=`C` | val_ic=`-0.039182` | target=`y_year_avg_daily_return_close`
- `bank_indicator__non_interest_income_ratio` | status=`C` | val_ic=`-0.100422` | target=`y_year_avg_daily_return_close`
- `bank_indicator__net_interest_margin` | status=`C` | val_ic=`-0.401405` | target=`y_year_avg_daily_return_close`

## secondary_candidate
- `derived__investment_income_to_operating_revenue` | status=`A` | val_ic=`0.039656` | target=`y_quarter_avg_daily_return_close`
- `derived__staff_cash_to_operating_revenue` | status=`C` | val_ic=`-0.124607` | target=`y_quarter_avg_daily_return_close`

## watch_only
- `income__minority_profit` | status=`A` | val_ic=`0.113868` | target=`y_quarter_avg_daily_return_close`
- `indicator__eps` | status=`A` | val_ic=`0.059367` | target=`y_quarter_avg_daily_return_close`

Output:
- [single_factor_test_results_core_v2.csv](D:\hh\codex\v4\phase_1_fundamental\single_factor_test_results_core_v2.csv)