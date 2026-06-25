# Base Core 6 Monthly Relative Momentum Branch Switch Rolling Validation V1

Protocol:
- branch A = balanced pure-fundamental `base_core_6 + top_08`
- branch B = capital-quality side candidate `base_core_6 - indicator__eps + bank_indicator__core_level_capital_adequacy_ratio`
- build daily NAV paths for both branches inside each fold
- update relative momentum monthly from branch B versus branch A, but only apply the choice when the strategy reaches the next rebalance date
- this tests whether monthly style strength can improve over annual one-shot branch switching

Rules tested:
- `branch_a_always`
- `branch_b_always`
- `branch_b_if_rel_1m_gt_0`
- `branch_b_if_rel_3m_gt_0`
- `branch_b_if_rel_3m_gt_2pct`

Ranking by mean review return:
- `branch_b_always` | folds=`5` | mean_train_cum=`0.605589` | mean_test_cum=`0.283983` | mean_review_cum=`0.078288` | delta_test_vs_branch_a=`0.014547` | delta_review_vs_branch_a=`0.012744` | mean_branch_b_period_count=`23.000000` | mean_rel_1m=`0.000006` | mean_rel_3m=`0.000146`
- `branch_b_if_rel_3m_gt_2pct` | folds=`5` | mean_train_cum=`0.595611` | mean_test_cum=`0.256862` | mean_review_cum=`0.068630` | delta_test_vs_branch_a=`-0.012574` | delta_review_vs_branch_a=`0.003086` | mean_branch_b_period_count=`1.000000` | mean_rel_1m=`0.000006` | mean_rel_3m=`0.000146`
- `branch_b_if_rel_1m_gt_0` | folds=`5` | mean_train_cum=`0.580353` | mean_test_cum=`0.275141` | mean_review_cum=`0.067126` | delta_test_vs_branch_a=`0.005705` | delta_review_vs_branch_a=`0.001582` | mean_branch_b_period_count=`8.200000` | mean_rel_1m=`0.000006` | mean_rel_3m=`0.000146`
- `branch_b_if_rel_3m_gt_0` | folds=`5` | mean_train_cum=`0.587415` | mean_test_cum=`0.272295` | mean_review_cum=`0.065678` | delta_test_vs_branch_a=`0.002860` | delta_review_vs_branch_a=`0.000134` | mean_branch_b_period_count=`8.600000` | mean_rel_1m=`0.000006` | mean_rel_3m=`0.000146`
- `branch_a_always` | folds=`5` | mean_train_cum=`0.603109` | mean_test_cum=`0.269435` | mean_review_cum=`0.065544` | delta_test_vs_branch_a=`0.000000` | delta_review_vs_branch_a=`0.000000` | mean_branch_b_period_count=`0.000000` | mean_rel_1m=`0.000006` | mean_rel_3m=`0.000146`

Outputs:
- [base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1_config_results.csv)
