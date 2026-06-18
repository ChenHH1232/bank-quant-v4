# Controlled Improvement Pool V1

This pool expands the current enhancement layer from the original top2 into a controlled top6 candidate set.

Selection logic:
- keep the current top2 enhancement factors
- add high-conviction improvement candidates with acceptable validation IC and clear economic interpretation
- do not open the full improvement universe yet

- candidate count: `6`

Candidates:
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | val_ic=`0.315421` | val_pos_ic_ratio=`1.0` | val_spread=`0.00051854`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | val_ic=`0.218749` | val_pos_ic_ratio=`0.666667` | val_spread=`0.00068503`
- `improve__annual_delta__bank_indicator__capital_adequacy_ratio` | val_ic=`0.18855` | val_pos_ic_ratio=`1.0` | val_spread=`0.00018613`
- `improve__season_yoy_delta__derived__staff_cash_to_operating_revenue` | val_ic=`0.101684` | val_pos_ic_ratio=`0.666667` | val_spread=`0.00018378`
- `improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual` | val_ic=`0.121612` | val_pos_ic_ratio=`0.833333` | val_spread=`0.00046835`
- `improve__snapshot_delta__indicator__eps` | val_ic=`0.112935` | val_pos_ic_ratio=`0.833333` | val_spread=`0.00035552`

Output:
- [controlled_improvement_pool_v1.csv](D:\hh\codex\v4\phase_1_fundamental\controlled_improvement_pool_v1.csv)