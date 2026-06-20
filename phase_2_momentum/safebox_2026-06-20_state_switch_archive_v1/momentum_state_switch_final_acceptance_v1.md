# Momentum State Switch Final Acceptance V1

This document freezes the final acceptance conclusion for the bank momentum state-switch branch after the pre-2021 refinement cycle and one frozen JoinQuant out-of-sample check.

## Final Conclusion

The current final conclusion is:

- the state-switch idea is a valid research direction
- but the original formal candidate cannot be directly promoted because its `state_score_v2` contains a future-defined component
- the executable observable-proxy version achieved positive out-of-sample performance, but not strong enough to replace the current deployment baseline
- therefore the branch should be archived as a strong research candidate, not promoted as the new momentum main line

## What Was Confirmed

The following points remain valid:

- `mom_6_1` benefits from state filtering
- leaving middle-state months on `mom_12_1` is better than expanding `mom_6_1` usage
- `state_score_v2` was the strongest pre-2021 refinement within the research loop
- stricter high-state cutoffs than top `33%` did not improve the candidate

## Critical Limitation

The original formal candidate used:

- `cross_mcap_median`
- `cross_target_dispersion`
- `cross_mom6_top_bottom_spread`
- `cross_money_median`

The problem is:

- `cross_target_dispersion` was defined from next-period return dispersion
- that makes it unavailable at the decision point in a true out-of-sample deployment setting

So:

- the research candidate is still informative
- but the exact research rule is not directly executable without leakage

## What Was Actually Tested In JoinQuant

To keep the JoinQuant acceptance run honest, a frozen observable proxy was used instead:

- `cross_mcap_median`
- `cross_mom6_positive_ratio`
- `cross_money_median`

Rule:

- monthly rebalance
- top `33%` observable proxy months use `mom_6_1`
- all other months use `mom_12_1`

This is an executable approximation of the state-switch idea, not a verbatim deployment of the original `state_score_v2`.

## JoinQuant Out-of-Sample Result

Frozen test window:
- `2021-05-31` to `2026-05-31`

Observed result:
- strategy return = `34.04%`
- annualized return = `6.24%`
- excess return = `11.83%`
- alpha = `0.024`
- beta = `1.044`
- sharpe = `0.111`
- max drawdown = `23.75%`

Interpretation:
- the executable proxy version is profitable
- it also beats the benchmark in absolute and excess-return terms
- but the risk-adjusted quality is not strong enough to justify replacing the current monthly deployment baseline

## Final Status

- research idea validity: `confirmed`
- original formal candidate executability: `not deployment-safe`
- observable proxy OOS result: `positive but not decisive`
- deployment promotion: `not approved`
- branch status: `archived as strong research candidate`

## Practical Takeaway

The safest practical interpretation is:

- state filtering is probably a real improvement path for bank momentum
- but the current strongest research version still needs a fully observable state definition before it can be judged as a true promotion candidate
- until that happens, `joinquant_v4_monthly_momentum_strategy_v1.py` remains the safer archived deployment baseline

## Discipline Note

The frozen `2021-05-31` to `2026-05-31` JoinQuant window has now been used for one acceptance check on the executable proxy version.

Therefore:

- do not keep tuning state-switch variants on this same out-of-sample window
- if the branch is reopened later, it should begin by rebuilding the state score using only contemporaneously observable inputs

## References

- [momentum_state_switch_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_formal_candidate_v1.md)
- [momentum_forward_state_score_v2.md](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_score_v2.md)
- [momentum_state_switch_rolling_validation_v3.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v3.md)
- [momentum_state_switch_threshold_test_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_threshold_test_v1.md)
- [joinquant_v4_monthly_state_switch_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_monthly_state_switch_strategy_v1.py)
