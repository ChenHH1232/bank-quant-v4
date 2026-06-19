# Momentum State Switch Rolling Validation V1

Protocol:
- monthly sample = bank pool monthly rebalance dates before 2021
- fold structure = `60m train + 24m validation + 12m review`
- train window estimates only the state-score `33%` and `67%` thresholds
- validation/review windows apply: high state uses `mom_6_1`, otherwise use `mom_12_1`

- fold count: `0`

Interpretation:
- if the switch line beats pure `mom_6_1` and often competes with `mom_12_1` out of train-sample, then state filtering is more than an in-sample story
- if review results stay weak, the state score may still be descriptive but not yet robust enough for rolling deployment

Outputs:
- [momentum_state_switch_rolling_validation_v1_folds.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v1_folds.csv)
- [momentum_state_switch_rolling_validation_v1_results.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v1_results.csv)
