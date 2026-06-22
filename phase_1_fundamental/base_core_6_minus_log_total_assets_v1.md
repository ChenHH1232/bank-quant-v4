# Base Core 6 Minus Log Total Assets V1

Protocol:
- annual anchor = realized May rebalance date
- rolling window = `5y train + 2y test + 1y review`
- excluded base-core factor = `derived__log_total_assets`
- fixed base candidate shell = remaining 6 resident factors
- annual thresholds and combo scoring stay unchanged

Base candidate shell:
- `indicator__roe`
- `indicator__eps`
- `bank_indicator__Nonperforming_loan_rate`
- `bank_indicator__non_performing_loan_provision_coverage`
- `bank_indicator__deposit_loan_ratio`
- `bank_indicator__capital_adequacy_ratio`

Average review-year results by scenario and combo:
- `base_core_7` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.0952472` | mean_review_spread=`0.000461874` | mean_selected_count=`3.6`
- `base_core_7` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.0823086` | mean_review_spread=`0.000423164` | mean_selected_count=`3.6`
- `base_core_7` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`0.0528368` | mean_review_spread=`0.000331956` | mean_selected_count=`3.6`
- `base_plus_top2_9` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.0952472` | mean_review_spread=`0.000461874` | mean_selected_count=`3.6`
- `base_plus_top2_9` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.0823086` | mean_review_spread=`0.000423164` | mean_selected_count=`3.6`
- `base_plus_top2_9` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`0.0528368` | mean_review_spread=`0.000331956` | mean_selected_count=`3.6`

Selection counts by fold:
- `annual_01` | kept=`14` / total=`18`
- `annual_02` | kept=`11` / total=`18`
- `annual_03` | kept=`3` / total=`18`
- `annual_04` | kept=`4` / total=`18`
- `annual_05` | kept=`8` / total=`18`

Outputs:
- [base_core_6_minus_log_total_assets_v1_folds.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_minus_log_total_assets_v1_folds.csv)
- [base_core_6_minus_log_total_assets_v1_factor_selection.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_minus_log_total_assets_v1_factor_selection.csv)
- [base_core_6_minus_log_total_assets_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_minus_log_total_assets_v1_results.csv)
