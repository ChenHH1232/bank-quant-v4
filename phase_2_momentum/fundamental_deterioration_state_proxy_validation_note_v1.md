# Fundamental Deterioration State Proxy Validation Note V1

Conclusion:
- the `fundamental deterioration state proxy` is the first observable state candidate that beats both the old price-state proxy and the fixed `60/40` dual-engine baseline in pre-2021 rolling validation
- it should be promoted to the current best observable state candidate for the bank dual-engine branch

## What Was Tested

Research scope:
- pre-2021 only
- same dual-engine framework as the earlier fixed-blend and state-gated tests
- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`
- momentum engine = deployment-safe `mom_12_1`

Compared state routes:
- fixed `blend_60_40`
- `price_state_proxy`
- `deterioration_state_proxy`
- `combined_state_proxy`
- `fundamental_only`

Current deterioration proxy definition:
- `- deterioration_ratio + score_delta_mean + score_delta_bottom_quartile_mean`

Allocation mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

## Result

Strategy summary:
- `deterioration_state_proxy` cum return = `0.004548`
- fixed `blend_60_40` cum return = `0.004325`
- `combined_state_proxy` cum return = `0.004261`
- `price_state_proxy` cum return = `0.003511`
- `fundamental_only` cum return = `0.002768`

So the current ranking is:

1. `deterioration_state_proxy`
2. fixed `blend_60_40`
3. `combined_state_proxy`
4. `price_state_proxy`
5. `fundamental_only`

## Interpretation

This means:

- the earlier bottleneck was not only the fallback allocation rule
- the more important problem was state recognition quality
- adding the deterioration-based observable features improved that state recognition enough to exceed the fixed `60/40` baseline

At the same time:

- the `combined_state_proxy` did not beat the deterioration-only version
- so the current price proxy is not adding useful incremental information yet
- it is more likely adding noise than helping the routing decision

## Why This Matters

This is the first time the observable-state branch has cleared the key hurdle:

- not just beating the old observable price proxy
- but also beating the current fixed dual-engine baseline

That makes the research priority much clearer:

- the active state-routing line should now focus on `fundamental deterioration`
- not on repeatedly changing fallback assets
- and not on mixing in more weak price proxies unless they add clear incremental evidence

## Practical Judgment

Current judgment should be:

- fixed `60/40` remains the clean and simple allocation baseline
- `fundamental deterioration state routing` is now the leading upgrade candidate above that baseline
- `price_state_proxy` should be demoted from lead candidate status
- `bond-switch` remains archived as a useful but currently weaker defensive branch

## Next Step

The next concrete task should be:

- run a second-pass refinement only around the deterioration proxy family

That refinement should focus on:

- alternative deterioration feature combinations
- threshold sensitivity
- whether breadth or tail deterioration is the stronger driver
- whether the state mapping should stay `60/40 -> 80/20 -> 100/0` or be adjusted only after the proxy itself is stabilized

## References

- [state_proxy_comparison_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\state_proxy_comparison_rolling_validation_v1.md)
- [state_proxy_comparison_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\state_proxy_comparison_rolling_validation_v1_detail.csv)
- [fundamental_deterioration_feature_panel_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_deterioration_feature_panel_v1.md)
- [fundamental_deterioration_state_proxy_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_deterioration_state_proxy_draft_v1.md)
- [defensive_bond_switch_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\defensive_bond_switch_validation_note_v1.md)
