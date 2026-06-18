# Annual Factor Refresh Selection Summary V1

This summary makes the annual 5y+2y+1y refresh easier to read by showing the kept factor set for each annual fold and the year-to-year changes.

- annual fold count: `5`
- controlled factor universe size: `15`

## Annual Kept Sets

### annual_01
- kept factor count: `10`
- `bank_indicator__Nonperforming_loan_rate` | layer=`base_core`
- `bank_indicator__capital_adequacy_ratio` | layer=`base_core`
- `bank_indicator__deposit_loan_ratio` | layer=`base_core`
- `bank_indicator__net_interest_margin` | layer=`watch_layer`
- `bank_indicator__non_interest_income_ratio` | layer=`watch_layer`
- `bank_indicator__non_performing_loan_provision_coverage` | layer=`base_core`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | layer=`improvement_layer`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | layer=`improvement_layer`
- `indicator__eps` | layer=`base_core`
- `indicator__roe` | layer=`base_core`

### annual_02
- kept factor count: `9`
- `bank_indicator__Nonperforming_loan_rate` | layer=`base_core`
- `bank_indicator__capital_adequacy_ratio` | layer=`base_core`
- `bank_indicator__core_level_capital_adequacy_ratio` | layer=`watch_layer`
- `bank_indicator__deposit_loan_ratio` | layer=`base_core`
- `bank_indicator__non_performing_loan_provision_coverage` | layer=`base_core`
- `derived__log_total_assets` | layer=`base_core`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | layer=`improvement_layer`
- `indicator__eps` | layer=`base_core`
- `indicator__roe` | layer=`base_core`

### annual_03
- kept factor count: `4`
- `bank_indicator__capital_adequacy_ratio` | layer=`base_core`
- `bank_indicator__core_level_capital_adequacy_ratio` | layer=`watch_layer`
- `bank_indicator__deposit_loan_ratio` | layer=`base_core`
- `derived__log_total_assets` | layer=`base_core`

### annual_04
- kept factor count: `4`
- `bank_indicator__capital_adequacy_ratio` | layer=`base_core`
- `bank_indicator__core_level_capital_adequacy_ratio` | layer=`watch_layer`
- `derived__log_total_assets` | layer=`base_core`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | layer=`improvement_layer`

### annual_05
- kept factor count: `6`
- `bank_indicator__capital_adequacy_ratio` | layer=`base_core`
- `bank_indicator__core_level_capital_adequacy_ratio` | layer=`watch_layer`
- `bank_indicator__deposit_loan_ratio` | layer=`base_core`
- `bank_indicator__non_performing_loan_provision_coverage` | layer=`base_core`
- `derived__log_total_assets` | layer=`base_core`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | layer=`improvement_layer`

## Year-to-Year Changes

### annual_01 -> annual_02
- added count: `2`
- `bank_indicator__core_level_capital_adequacy_ratio` | layer=`watch_layer`
- `derived__log_total_assets` | layer=`base_core`
- removed count: `3`
- `bank_indicator__net_interest_margin` | layer=`watch_layer`
- `bank_indicator__non_interest_income_ratio` | layer=`watch_layer`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | layer=`improvement_layer`

### annual_02 -> annual_03
- added count: `0`
- none
- removed count: `5`
- `bank_indicator__Nonperforming_loan_rate` | layer=`base_core`
- `bank_indicator__non_performing_loan_provision_coverage` | layer=`base_core`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | layer=`improvement_layer`
- `indicator__eps` | layer=`base_core`
- `indicator__roe` | layer=`base_core`

### annual_03 -> annual_04
- added count: `1`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | layer=`improvement_layer`
- removed count: `1`
- `bank_indicator__deposit_loan_ratio` | layer=`base_core`

### annual_04 -> annual_05
- added count: `2`
- `bank_indicator__deposit_loan_ratio` | layer=`base_core`
- `bank_indicator__non_performing_loan_provision_coverage` | layer=`base_core`
- removed count: `0`
- none

## Stability Snapshot

### Always Kept
- factor count: `1`
- `bank_indicator__capital_adequacy_ratio` | layer=`base_core`

### Never Kept
- factor count: `3`
- `bank_indicator__cost_to_income_ratio` | layer=`watch_layer`
- `derived__investment_income_to_operating_revenue` | layer=`watch_layer`
- `indicator__inc_net_profit_to_shareholders_annual` | layer=`watch_layer`

### Keep Frequency
- `bank_indicator__capital_adequacy_ratio` | kept_folds=`5/5` | layer=`base_core`
- `bank_indicator__core_level_capital_adequacy_ratio` | kept_folds=`4/5` | layer=`watch_layer`
- `bank_indicator__deposit_loan_ratio` | kept_folds=`4/5` | layer=`base_core`
- `derived__log_total_assets` | kept_folds=`4/5` | layer=`base_core`
- `bank_indicator__non_performing_loan_provision_coverage` | kept_folds=`3/5` | layer=`base_core`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | kept_folds=`3/5` | layer=`improvement_layer`
- `bank_indicator__Nonperforming_loan_rate` | kept_folds=`2/5` | layer=`base_core`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | kept_folds=`2/5` | layer=`improvement_layer`
- `indicator__eps` | kept_folds=`2/5` | layer=`base_core`
- `indicator__roe` | kept_folds=`2/5` | layer=`base_core`
- `bank_indicator__net_interest_margin` | kept_folds=`1/5` | layer=`watch_layer`
- `bank_indicator__non_interest_income_ratio` | kept_folds=`1/5` | layer=`watch_layer`