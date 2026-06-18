# Improvement Factor Test Results V1

- Train window: `2014-05-01` to `2019-05-01`
- Validation window: `2019-05-01` to `2021-05-01`
- Total improvement factors tested: `22`

Status count:
- `A`: `6`
- `B`: `0`
- `C`: `9`
- `D`: `7`

Top reviewed rows:
- `improve__snapshot_delta__derived__log_total_assets` | status=`A` | val_ic=`0.151246` | train_ic=`0.036329`
- `improve__annual_delta__bank_indicator__capital_adequacy_ratio` | status=`A` | val_ic=`0.139468` | train_ic=`0.024091`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | status=`A` | val_ic=`0.115305` | train_ic=`0.253151`
- `improve__annual_delta__bank_indicator__core_level_capital_adequacy_ratio` | status=`A` | val_ic=`0.099452` | train_ic=`0.198023`
- `improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual` | status=`A` | val_ic=`0.057866` | train_ic=`0.011189`
- `improve__snapshot_delta__income__minority_profit` | status=`A` | val_ic=`0.004594` | train_ic=`0.114093`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | status=`C` | val_ic=`-0.00186` | train_ic=`0.208335`
- `improve__annual_delta__bank_indicator__cost_to_income_ratio` | status=`C` | val_ic=`-0.023138` | train_ic=`0.220256`
- `improve__snapshot_delta__indicator__eps` | status=`C` | val_ic=`-0.023527` | train_ic=`0.058543`
- `improve__annual_delta__bank_indicator__non_performing_loan_provision_coverage` | status=`C` | val_ic=`-0.062306` | train_ic=`0.086292`

Outputs:
- [improvement_factor_test_results_v1.csv](D:\hh\codex\v4\phase_1_fundamental\improvement_factor_test_results_v1.csv)
- [improvement_factor_panel_v1.csv](D:\hh\codex\v4\phase_1_fundamental\improvement_factor_panel_v1.csv)