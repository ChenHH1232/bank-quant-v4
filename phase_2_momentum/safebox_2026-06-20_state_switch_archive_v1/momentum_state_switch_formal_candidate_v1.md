# Momentum State Switch Formal Candidate V1

This document freezes the current formal research candidate for the bank momentum state-switch branch after the full pre-2021 refinement cycle.

## Candidate Rule

Rebalance rhythm:
- monthly

Backbone:
- default factor = `mom_12_1`
- switched factor = `mom_6_1`

State score:
- use `state_score_v2`

Current `state_score_v2` components:
- `cross_mcap_median` with sign `+`
- `cross_target_dispersion` with sign `+`
- `cross_mom6_top_bottom_spread` with sign `+`
- `cross_money_median` with sign `-`

Switch rule:
- estimate the train-window `state_score_v2` distribution
- if current month score is in the top `33%`, use `mom_6_1`
- otherwise use `mom_12_1`

## Why This Became The Formal Candidate

This version survived three refinement filters:

1. baseline rolling confirmation
- `state_score_v1` switch mean test return = `0.169637`
- pure `mom_6_1` mean test return = `0.119686`
- pure `mom_12_1` mean test return = `0.180519`

2. middle-state routing refinement
- pushing middle-state months toward `mom_6_1` weakened results
- so middle-state months should remain on `mom_12_1`

3. state-score refinement
- `state_score_v2` mean rolling test return = `0.189160`
- this moved above pure `mom_12_1` mean return = `0.180519`
- it also kept `13 / 13` wins versus pure `mom_6_1`

4. threshold refinement
- stricter triggers such as top `25%`, `20%`, and `15%` all underperformed the top `33%` rule
- so `top33_use_mom6` remains the best current trigger

## Current Evidence Summary

Best rolling train/test protocol:
- feasible pre-2021 monthly protocol = `48m train + 12m test`
- fold count = `13`

Current formal candidate results:
- candidate mean test return = `0.189160`
- pure `mom_12_1` mean test return = `0.180519`
- pure `mom_6_1` mean test return = `0.119686`
- candidate win count versus pure `mom_6_1` = `13 / 13`
- candidate win count versus pure `mom_12_1` = `4 / 13`
- average months using `mom_6_1` in each test window = `1.38`

Interpretation:
- the candidate is clearly better than raw `mom_6_1`
- it is also better than pure `mom_12_1` on average outcome
- but it is not yet dominant enough fold by fold to be called a fully promoted deployment replacement

## Status

Current status:
- `preferred formal candidate`
- not yet `deployment main line`

Promotion condition:
- only promote if one final acceptance step justifies moving beyond pre-2021 research
- that acceptance step should be a single frozen JoinQuant out-of-sample test, not another round of repeated tuning

## Recommended Next Step

The next valid move is:

- write one JoinQuant strategy that implements this exact candidate rule
- test it once on the frozen `2021-05-31` to `2026-05-29` out-of-sample window
- compare it only against the current monthly deployment baseline

If it does not clearly improve the deployment baseline:
- archive it as a strong research candidate
- do not keep retuning it on the same out-of-sample window

## References

- [momentum_forward_state_score_v2.md](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_score_v2.md)
- [momentum_state_switch_rolling_validation_v3.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v3.md)
- [momentum_state_switch_threshold_test_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_threshold_test_v1.md)
- [momentum_state_switch_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_candidate_v1.md)
