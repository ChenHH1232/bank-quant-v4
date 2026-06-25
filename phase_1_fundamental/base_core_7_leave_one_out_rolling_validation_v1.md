# Base Core 7 Leave-One-Out Rolling Validation V1

Protocol:
- baseline factor shell = annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- each leave-one-out variant removes exactly one resident `base_core` factor from the executable universe
- annual factor-refresh rules, layer caps, and combo scoring stay unchanged
- strategy readout uses the same top-bucket return logic on each rebalance snapshot

Resident factor set tested:
- `indicator__roe`
- `indicator__eps`
- `derived__log_total_assets`
- `bank_indicator__Nonperforming_loan_rate`
- `bank_indicator__non_performing_loan_provision_coverage`
- `bank_indicator__deposit_loan_ratio`
- `bank_indicator__capital_adequacy_ratio`

Baseline means:
- mean_train_cum=`0.004775`
- mean_test_cum=`0.003700`
- mean_review_cum=`0.001024`

Leave-one-out ranking:
- remove `derived__log_total_assets` | folds=`5` | mean_train_cum=`0.005130` | mean_test_cum=`0.003908` | mean_review_cum=`0.001239` | delta_test=`0.000208` | delta_review=`0.000215` | mean_selected_factor_count=`3.600000`
- remove `bank_indicator__non_performing_loan_provision_coverage` | folds=`5` | mean_train_cum=`0.004092` | mean_test_cum=`0.003652` | mean_review_cum=`0.000993` | delta_test=`-0.000049` | delta_review=`-0.000031` | mean_selected_factor_count=`3.800000`
- remove `bank_indicator__deposit_loan_ratio` | folds=`5` | mean_train_cum=`0.005410` | mean_test_cum=`0.003556` | mean_review_cum=`0.001183` | delta_test=`-0.000145` | delta_review=`0.000160` | mean_selected_factor_count=`3.600000`
- remove `bank_indicator__Nonperforming_loan_rate` | folds=`5` | mean_train_cum=`0.004371` | mean_test_cum=`0.003441` | mean_review_cum=`0.001136` | delta_test=`-0.000259` | delta_review=`0.000112` | mean_selected_factor_count=`4.000000`
- remove `indicator__roe` | folds=`5` | mean_train_cum=`0.007361` | mean_test_cum=`0.003357` | mean_review_cum=`0.001061` | delta_test=`-0.000344` | delta_review=`0.000038` | mean_selected_factor_count=`4.000000`
- remove `indicator__eps` | folds=`5` | mean_train_cum=`0.004251` | mean_test_cum=`0.003256` | mean_review_cum=`0.001070` | delta_test=`-0.000445` | delta_review=`0.000046` | mean_selected_factor_count=`4.000000`
- remove `bank_indicator__capital_adequacy_ratio` | folds=`5` | mean_train_cum=`0.005441` | mean_test_cum=`0.003233` | mean_review_cum=`0.000800` | delta_test=`-0.000467` | delta_review=`-0.000224` | mean_selected_factor_count=`3.400000`

Outputs:
- [base_core_7_leave_one_out_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_7_leave_one_out_rolling_validation_v1_config_results.csv)
