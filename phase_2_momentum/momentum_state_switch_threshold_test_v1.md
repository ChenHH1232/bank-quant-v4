# Momentum State Switch Threshold Test V1

Protocol:
- monthly sample = bank pool monthly rebalance dates before 2021
- score backbone is frozen to `state_score_v2`
- fold structure = `48m train + 12m test`
- objective = test whether a stricter high-state trigger improves the state-switch candidate

Threshold summary:
- `top33_use_mom6` | folds=`13` | mean_test_return=`0.189160` | win_vs_mom6=`13` | win_vs_mom12=`4` | avg_use_mom6_months=`1.38`
- `top15_use_mom6` | folds=`13` | mean_test_return=`0.183207` | win_vs_mom6=`12` | win_vs_mom12=`3` | avg_use_mom6_months=`0.38`
- `top20_use_mom6` | folds=`13` | mean_test_return=`0.183207` | win_vs_mom6=`12` | win_vs_mom12=`3` | avg_use_mom6_months=`0.77`
- `top25_use_mom6` | folds=`13` | mean_test_return=`0.183207` | win_vs_mom6=`12` | win_vs_mom12=`3` | avg_use_mom6_months=`0.77`

Current best threshold:
- `top33_use_mom6` with mean test return `0.189160`

Output:
- [momentum_state_switch_threshold_test_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_threshold_test_v1.csv)
