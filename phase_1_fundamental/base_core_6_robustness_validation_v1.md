# Base Core 6 Robustness Validation V1

Protocol:
- factor engine = annual pure-fundamental `base_core_6`
- removed factor from mother shell = `derived__log_total_assets`
- each year still re-trains and re-selects from the remaining 6-factor shell
- this validation perturbs window lengths, combo scoring, and hold counts together
- tested train windows = `3 / 5 / 7` years
- tested test windows = `1 / 2` years
- tested review window = `1` year
- tested hold counts = `6 / 8 / 10 / 12`

Baseline config: `window_5y_2y_1y__combo__ic_weight_train__top_08`

Base candidate shell:
- `indicator__roe`
- `indicator__eps`
- `bank_indicator__Nonperforming_loan_rate`
- `bank_indicator__non_performing_loan_provision_coverage`
- `bank_indicator__deposit_loan_ratio`
- `bank_indicator__capital_adequacy_ratio`

Top configs by mean test return:
- `window_7y_2y_1y__combo__ic_weight_train__top_06` | folds=`3` | mean_train_cum=`1.024911` | mean_test_cum=`0.393178` | mean_review_cum=`0.112051` | delta_test_vs_baseline=`0.123743` | delta_review_vs_baseline=`0.046507` | mean_selected_count=`2.000000` | mean_review_cash=`0.000000`
- `window_5y_2y_1y__combo__ic_weight_train__top_06` | folds=`5` | mean_train_cum=`0.615544` | mean_test_cum=`0.321874` | mean_review_cum=`0.070514` | delta_test_vs_baseline=`0.052438` | delta_review_vs_baseline=`0.004970` | mean_selected_count=`3.600000` | mean_review_cash=`0.000546`
- `window_5y_2y_1y__combo__equal_weight__top_06` | folds=`5` | mean_train_cum=`0.682436` | mean_test_cum=`0.319330` | mean_review_cum=`0.065921` | delta_test_vs_baseline=`0.049894` | delta_review_vs_baseline=`0.000377` | mean_selected_count=`3.600000` | mean_review_cash=`0.000546`
- `window_5y_2y_1y__combo__quarterly_plus_annual__top_06` | folds=`5` | mean_train_cum=`0.687618` | mean_test_cum=`0.304703` | mean_review_cum=`0.052046` | delta_test_vs_baseline=`0.035267` | delta_review_vs_baseline=`-0.013498` | mean_selected_count=`3.600000` | mean_review_cash=`0.000546`
- `window_3y_2y_1y__combo__ic_weight_train__top_06` | folds=`7` | mean_train_cum=`0.418527` | mean_test_cum=`0.298361` | mean_review_cum=`0.066038` | delta_test_vs_baseline=`0.028926` | delta_review_vs_baseline=`0.000495` | mean_selected_count=`3.571429` | mean_review_cash=`0.000390`
- `window_3y_2y_1y__combo__equal_weight__top_06` | folds=`7` | mean_train_cum=`0.427031` | mean_test_cum=`0.294587` | mean_review_cum=`0.073725` | delta_test_vs_baseline=`0.025151` | delta_review_vs_baseline=`0.008182` | mean_selected_count=`3.571429` | mean_review_cash=`0.000390`
- `window_7y_2y_1y__combo__equal_weight__top_06` | folds=`3` | mean_train_cum=`0.927635` | mean_test_cum=`0.293784` | mean_review_cum=`0.124632` | delta_test_vs_baseline=`0.024349` | delta_review_vs_baseline=`0.059089` | mean_selected_count=`2.000000` | mean_review_cash=`0.000000`
- `window_7y_2y_1y__combo__quarterly_plus_annual__top_06` | folds=`3` | mean_train_cum=`0.927635` | mean_test_cum=`0.293784` | mean_review_cum=`0.124632` | delta_test_vs_baseline=`0.024349` | delta_review_vs_baseline=`0.059089` | mean_selected_count=`2.000000` | mean_review_cash=`0.000000`
- `window_3y_2y_1y__combo__quarterly_plus_annual__top_06` | folds=`7` | mean_train_cum=`0.396597` | mean_test_cum=`0.291543` | mean_review_cum=`0.073237` | delta_test_vs_baseline=`0.022107` | delta_review_vs_baseline=`0.007693` | mean_selected_count=`3.571429` | mean_review_cash=`0.000390`
- `window_7y_2y_1y__combo__ic_weight_train__top_08` | folds=`3` | mean_train_cum=`0.825513` | mean_test_cum=`0.274745` | mean_review_cum=`0.116079` | delta_test_vs_baseline=`0.005310` | delta_review_vs_baseline=`0.050535` | mean_selected_count=`2.000000` | mean_review_cash=`0.000000`
- `window_5y_2y_1y__combo__ic_weight_train__top_08` | folds=`5` | mean_train_cum=`0.603109` | mean_test_cum=`0.269435` | mean_review_cum=`0.065544` | delta_test_vs_baseline=`0.000000` | delta_review_vs_baseline=`0.000000` | mean_selected_count=`3.600000` | mean_review_cash=`0.000410`
- `window_7y_2y_1y__combo__equal_weight__top_08` | folds=`3` | mean_train_cum=`0.796796` | mean_test_cum=`0.255058` | mean_review_cum=`0.126401` | delta_test_vs_baseline=`-0.014377` | delta_review_vs_baseline=`0.060857` | mean_selected_count=`2.000000` | mean_review_cash=`0.000000`

Baseline means:
- mean_train_cum=`0.603109`
- mean_test_cum=`0.269435`
- mean_review_cum=`0.065544`

Outputs:
- [base_core_6_robustness_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_robustness_validation_v1_config_results.csv)
