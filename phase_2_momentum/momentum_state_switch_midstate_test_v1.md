# Momentum State Switch Mid-State Test V1

Protocol:
- monthly sample = bank pool monthly rebalance dates before 2021
- fold structure = `48m train + 12m test`
- each fold estimates only the train-period `q33` and `q67` thresholds from `state_score_v1`
- objective = compare how middle-state months should be routed under the same state definition

Rule summary:
- `high_only_mom6_baseline` | folds=`13` | mean_test_return=`0.169637` | mean_test_annualized=`0.169637` | win_vs_mom6=`13` | win_vs_mom12=`1`
- `high_use_mom6_low_blend` | folds=`13` | mean_test_return=`0.161652` | mean_test_annualized=`0.161652` | win_vs_mom6=`13` | win_vs_mom12=`2`
- `all_non_low_blend` | folds=`13` | mean_test_return=`0.157938` | mean_test_annualized=`0.157938` | win_vs_mom6=`12` | win_vs_mom12=`1`
- `high_use_mom6_mid_blend` | folds=`13` | mean_test_return=`0.152544` | mean_test_annualized=`0.152544` | win_vs_mom6=`13` | win_vs_mom12=`1`
- `high_mid_use_mom6` | folds=`13` | mean_test_return=`0.135524` | mean_test_annualized=`0.135524` | win_vs_mom6=`12` | win_vs_mom12=`1`

Current best-by-mean-return rule:
- `high_only_mom6_baseline` with mean test return `0.169637`

Outputs:
- [momentum_state_switch_midstate_test_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_midstate_test_v1.csv)
