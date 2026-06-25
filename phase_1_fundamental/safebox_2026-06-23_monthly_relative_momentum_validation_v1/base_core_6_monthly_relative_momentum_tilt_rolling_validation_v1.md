# Base Core 6 Monthly Relative Momentum Tilt Rolling Validation V1

Protocol:
- keep profitability and quality inside the same pure-fundamental shell
- build separate daily NAV paths for the profitability sleeve and the quality sleeve
- update their relative momentum monthly and let the next rebalance lean toward the stronger sleeve
- this tests dynamic tilt, not binary style replacement

Rules tested:
- `equal_50_50`
- `profit_60_if_rel_1m_gt_0_else_quality_60`
- `profit_70_if_rel_3m_gt_0_else_quality_70`
- `profit_70_if_rel_3m_gt_2pct_else_quality_60`

Ranking by mean review return:
- `profit_70_if_rel_3m_gt_0_else_quality_70` | folds=`5` | mean_train_cum=`0.606185` | mean_test_cum=`0.163797` | mean_review_cum=`0.025972` | delta_test_vs_equal=`0.002268` | delta_review_vs_equal=`0.002785` | mean_profitability_weight=`0.444324` | mean_quality_weight=`0.555676` | mean_rel_1m=`0.000744` | mean_rel_3m=`-0.003662`
- `profit_70_if_rel_3m_gt_2pct_else_quality_60` | folds=`5` | mean_train_cum=`0.600722` | mean_test_cum=`0.165614` | mean_review_cum=`0.025163` | delta_test_vs_equal=`0.004084` | delta_review_vs_equal=`0.001977` | mean_profitability_weight=`0.447599` | mean_quality_weight=`0.552401` | mean_rel_1m=`0.000744` | mean_rel_3m=`-0.003662`
- `equal_50_50` | folds=`5` | mean_train_cum=`0.604114` | mean_test_cum=`0.161530` | mean_review_cum=`0.023186` | delta_test_vs_equal=`0.000000` | delta_review_vs_equal=`0.000000` | mean_profitability_weight=`0.500000` | mean_quality_weight=`0.500000` | mean_rel_1m=`0.000744` | mean_rel_3m=`-0.003662`
- `profit_60_if_rel_1m_gt_0_else_quality_60` | folds=`5` | mean_train_cum=`0.610956` | mean_test_cum=`0.160615` | mean_review_cum=`0.022627` | delta_test_vs_equal=`-0.000915` | delta_review_vs_equal=`-0.000559` | mean_profitability_weight=`0.502508` | mean_quality_weight=`0.497492` | mean_rel_1m=`0.000744` | mean_rel_3m=`-0.003662`

Outputs:
- [base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1_config_results.csv)
