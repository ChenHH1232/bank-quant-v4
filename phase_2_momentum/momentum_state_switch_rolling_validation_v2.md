# Momentum State Switch Rolling Validation V2

Protocol:
- monthly sample = bank pool monthly rebalance dates before 2021
- fold structure = `48m train + 12m test`
- this replaces the infeasible `60m + 24m + 12m` state-switch draft because the pre-2021 monthly sample has only `72` usable months
- train window estimates only the state-score `33%` and `67%` thresholds
- test window applies: high state uses `mom_6_1`, otherwise use `mom_12_1`

- fold count: `13`

Average fold test results:
- mean_test_switch_total_return=`0.169637`
- mean_test_mom6_total_return=`0.119686`
- mean_test_mom12_total_return=`0.180519`
- mean_test_switch_annualized=`0.169637`

Win counts:
- test switch > mom6 folds: `13`
- test switch > mom12 folds: `1`
- test mom12 > mom6 folds: `12`

Average state usage in test windows:
- high-state months using `mom_6_1`: `1.62`
- mid-state months using `mom_12_1`: `5.00`
- low-state months using `mom_12_1`: `5.38`

Interpretation:
- if the switch line often beats pure `mom_6_1`, the state filter is adding protection against 6-1 overuse
- if it also stays close to or beats pure `mom_12_1`, then the switch candidate remains promotion-worthy
- if it still trails `mom_12_1` in most folds, keep it as a research candidate rather than a deployment replacement

Outputs:
- [momentum_state_switch_rolling_validation_v2_folds.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v2_folds.csv)
- [momentum_state_switch_rolling_validation_v2_results.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v2_results.csv)
