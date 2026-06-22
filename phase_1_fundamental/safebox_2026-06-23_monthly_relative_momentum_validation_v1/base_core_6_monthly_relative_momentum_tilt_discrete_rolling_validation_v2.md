# Base Core 6 Monthly Relative Momentum Tilt Discrete Rolling Validation V2

Protocol:
- rebalance only on the strategy's existing rebalance dates
- monthly relative momentum is used only as a state signal before each rebalance decision
- tested discrete tilt buckets centered on `50/50`, then stepping toward `40/60` or `30/70` when profitability relative momentum weakens
- profitability factors = `indicator__roe, indicator__eps`
- quality factors = `bank_indicator__Nonperforming_loan_rate, bank_indicator__non_performing_loan_provision_coverage, bank_indicator__deposit_loan_ratio, bank_indicator__capital_adequacy_ratio`

Rules tested:
- `equal_50_50`
- `quality_60_if_rel_3m_le_0_else_50`
- `quality_70_if_rel_3m_le_0_else_50`
- `quality_ladder_50_40_30_by_rel_3m`
- `symmetric_ladder_70_50_30_by_rel_3m`

Ranking by mean review return:
- `symmetric_ladder_70_50_30_by_rel_3m` | folds=`5` | mean_train_cum=`0.603100` | mean_test_cum=`0.163907` | mean_review_cum=`0.025891` | delta_test_vs_equal=`0.002377` | delta_review_vs_equal=`0.002705` | mean_profitability_weight=`0.454653` | mean_quality_weight=`0.545347` | state_50_50=`5.800000` | state_40_60=`11.800000` | state_30_70=`3.000000` | state_70_30=`3.400000`
- `quality_70_if_rel_3m_le_0_else_50` | folds=`5` | mean_train_cum=`0.605893` | mean_test_cum=`0.166272` | mean_review_cum=`0.025488` | delta_test_vs_equal=`0.004742` | delta_review_vs_equal=`0.002302` | mean_profitability_weight=`0.376340` | mean_quality_weight=`0.623660` | state_50_50=`9.200000` | state_40_60=`0.000000` | state_30_70=`14.800000` | state_70_30=`0.000000`
- `quality_ladder_50_40_30_by_rel_3m` | folds=`5` | mean_train_cum=`0.605852` | mean_test_cum=`0.163593` | mean_review_cum=`0.025178` | delta_test_vs_equal=`0.002063` | delta_review_vs_equal=`0.001991` | mean_profitability_weight=`0.425706` | mean_quality_weight=`0.574294` | state_50_50=`9.200000` | state_40_60=`11.800000` | state_30_70=`3.000000` | state_70_30=`0.000000`
- `quality_60_if_rel_3m_le_0_else_50` | folds=`5` | mean_train_cum=`0.605016` | mean_test_cum=`0.163901` | mean_review_cum=`0.024334` | delta_test_vs_equal=`0.002371` | delta_review_vs_equal=`0.001148` | mean_profitability_weight=`0.438170` | mean_quality_weight=`0.561830` | state_50_50=`9.200000` | state_40_60=`14.800000` | state_30_70=`0.000000` | state_70_30=`0.000000`
- `equal_50_50` | folds=`5` | mean_train_cum=`0.604114` | mean_test_cum=`0.161530` | mean_review_cum=`0.023186` | delta_test_vs_equal=`0.000000` | delta_review_vs_equal=`0.000000` | mean_profitability_weight=`0.500000` | mean_quality_weight=`0.500000` | state_50_50=`24.000000` | state_40_60=`0.000000` | state_30_70=`0.000000` | state_70_30=`0.000000`

Outputs:
- [base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2_config_results.csv)
