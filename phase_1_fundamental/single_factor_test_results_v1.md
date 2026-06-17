# Single-Factor Test Results V1

Window:
- training: `2014-05-01` to `2019-05-01`
- validation: `2019-05-01` to `2021-05-01`
- sample: `rebalance_stock_pool_flag = 1`

- Total tested factors: `74`
- A: `42`
- B: `5`
- C: `27`
- D: `0`

Top A factors:
- `cash_flow__subtotal_operate_cash_inflow` | val_ic=`0.12737` | val_spread=`-5e-07`
- `indicator__roe` | val_ic=`0.124165` | val_spread=`0.00042852`
- `income__minority_profit` | val_ic=`0.113868` | val_spread=`0.00050207`
- `indicator__inc_return` | val_ic=`0.111121` | val_spread=`0.00042852`
- `cash_flow__subtotal_operate_cash_outflow` | val_ic=`0.102315` | val_spread=`0.00045649`
- `bank_indicator__cost_to_income_ratio` | val_ic=`0.101345` | val_spread=`-0.00010232`
- `bank_indicator__deposit_loan_ratio` | val_ic=`0.101253` | val_spread=`0.00031277`
- `indicator__inc_net_profit_annual` | val_ic=`0.089146` | val_spread=`0.00022187`
- `bank_indicator__capital_adequacy_ratio` | val_ic=`0.088512` | val_spread=`0.00012455`
- `income__investment_income` | val_ic=`0.086041` | val_spread=`0.00019026`

Top B factors:
- `bank_indicator__total_deposit` | val_ic=`0.272624` | val_spread=`0.00010158`
- `indicator__net_profit_margin` | val_ic=`0.179843` | val_spread=`0.0003966`
- `indicator__net_profit_to_total_revenue` | val_ic=`0.179843` | val_spread=`0.0003966`
- `cash_flow__subtotal_finance_cash_outflow` | val_ic=`0.040043` | val_spread=`4.73e-05`
- `cash_flow__interest_and_commission_cashin` | val_ic=`0.012403` | val_spread=`-9.047e-05`

Output:
- [single_factor_test_results_v1.csv](D:\hh\codex\v4\phase_1_fundamental\single_factor_test_results_v1.csv)