# Momentum State Switch Rolling Validation V3

Protocol:
- monthly sample = bank pool monthly rebalance dates before 2021
- fold structure = `48m train + 12m test`
- switching rule stays fixed: high state uses `mom_6_1`, otherwise use `mom_12_1`
- objective = compare `state_score_v1` and `state_score_v2` under the same rolling protocol

Score-version summary:
- `state_score_v1` | folds=`13` | mean_test_return=`0.169637` | win_vs_mom6=`13` | win_vs_mom12=`1` | avg_high_state_months=`1.62`
- `state_score_v2` | folds=`13` | mean_test_return=`0.189160` | win_vs_mom6=`13` | win_vs_mom12=`4` | avg_high_state_months=`1.38`

Direct V2 vs V1 comparison:
- v2 better than v1 folds: `5`
- mean(v2 - v1) test return: `0.019523`

Output:
- [momentum_state_switch_rolling_validation_v3_results.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v3_results.csv)
