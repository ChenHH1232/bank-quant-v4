# Single-Factor Test Results V1

Window:
- training: `2014-05-01` to `2019-05-01`
- validation: `2019-05-01` to `2021-05-01`
- sample: `rebalance_stock_pool_flag = 1`

- Total tested factors: `77`
- A: `48`
- B: `4`
- C: `25`
- D: `0`

Top A factors:
- `bank_indicator__non_performing_loan_provision_coverage` | val_ic=`0.492055` | val_spread=`0.00091862`
- `bank_indicator__Nonperforming_loan_rate` | val_ic=`0.440019` | val_spread=`0.0008321`
- `bank_indicator__deposit_loan_ratio` | val_ic=`0.310985` | val_spread=`0.00055283`
- `indicator__eps` | val_ic=`0.253266` | val_spread=`0.00076843`
- `indicator__roa` | val_ic=`0.207771` | val_spread=`0.00029087`
- `bank_indicator__capital_adequacy_ratio` | val_ic=`0.193768` | val_spread=`0.00025344`
- `indicator__inc_return` | val_ic=`0.189247` | val_spread=`0.00058607`
- `indicator__roe` | val_ic=`0.186312` | val_spread=`0.00043448`
- `cash_flow__exchange_rate_change_effect` | val_ic=`0.162715` | val_spread=`0.00022307`
- `cash_flow__subtotal_finance_cash_outflow` | val_ic=`0.108264` | val_spread=`0.00020488`

Top B factors:
- `indicator__operation_profit_to_total_revenue` | val_ic=`0.033295` | val_spread=`-0.00054215`
- `indicator__expense_to_total_revenue` | val_ic=`0.033295` | val_spread=`-0.00053061`
- `cash_flow__invest_proceeds` | val_ic=`0.008269` | val_spread=`0.00019553`
- `income__minority_profit` | val_ic=`0.005915` | val_spread=`-9.6e-06`

Output:
- [single_factor_test_results_v1.csv](D:\hh\codex\v4\phase_1_fundamental\single_factor_test_results_v1.csv)