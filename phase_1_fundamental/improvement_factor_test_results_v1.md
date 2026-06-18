# Improvement Factor Test Results V1

- Train window: `2014-05-01` to `2019-05-01`
- Validation window: `2019-05-01` to `2021-05-01`
- Total improvement factors tested: `22`

Status count:
- `A`: `8`
- `B`: `1`
- `C`: `13`
- `D`: `0`

Top reviewed rows:
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | status=`A` | val_ic=`0.315421` | train_ic=`0.082644`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | status=`A` | val_ic=`0.218749` | train_ic=`0.027117`
- `improve__annual_delta__bank_indicator__capital_adequacy_ratio` | status=`A` | val_ic=`0.18855` | train_ic=`0.223725`
- `improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual` | status=`A` | val_ic=`0.121612` | train_ic=`0.037665`
- `improve__season_yoy_delta__derived__staff_cash_to_operating_revenue` | status=`A` | val_ic=`0.101684` | train_ic=`0.072977`
- `improve__season_yoy_delta__indicator__eps` | status=`A` | val_ic=`0.058964` | train_ic=`0.150222`
- `improve__annual_delta__bank_indicator__net_interest_margin` | status=`A` | val_ic=`0.056672` | train_ic=`0.032488`
- `improve__season_yoy_delta__indicator__roe` | status=`A` | val_ic=`0.049069` | train_ic=`0.07912`
- `improve__snapshot_delta__indicator__eps` | status=`B` | val_ic=`0.112935` | train_ic=`0.002178`
- `improve__annual_delta__bank_indicator__core_level_capital_adequacy_ratio` | status=`C` | val_ic=`-0.00276` | train_ic=`0.088618`

Outputs:
- [improvement_factor_test_results_v1.csv](D:\hh\codex\v4\phase_1_fundamental\improvement_factor_test_results_v1.csv)
- [improvement_factor_panel_v1.csv](D:\hh\codex\v4\phase_1_fundamental\improvement_factor_panel_v1.csv)