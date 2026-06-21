# Weak Down Exit Validation Note V1

Conclusion:
- the first monthly `weak_down exit` rule is directionally valid
- it improves the annual-only breadth-routed branch materially
- but it still does not beat the fixed `60/40` baseline

## What Was Tested

Annual entry layer:
- annual weak-state trigger = `breadth_only`

Monthly release layer:
- release signal = monthly cross-sectional `mom_6_1` positive ratio
- release threshold = train-set upper-third cutoff
- release action = upgrade only from `weak_down` to `neutral_flat`

Compared strategies:
- fixed `60/40`
- `annual_breadth_only`
- `annual_breadth_with_monthly_exit`

## Result

Strategy ranking:

1. fixed `60/40` cum return = `0.007821`
2. `annual_breadth_with_monthly_exit` cum return = `0.006663`
3. `annual_breadth_only` cum return = `0.005463`

So the monthly release layer added clear value:

- `annual_breadth_with_monthly_exit` improved over `annual_breadth_only` by `0.001200`

## Why This Matters

This is the first direct evidence that:

- the annual deterioration layer was not the whole problem
- the delayed recovery from `weak_down` really was a meaningful bottleneck

The release behavior also supports that interpretation:

- weak-down monthly snapshots = `20`
- released to `neutral_flat` = `3`
- held in `weak_down` = `17`
- released months mean return = `0.001418`
- held months mean return = `-0.000078`

That pattern is exactly what we hoped to see:

- when the monthly repair rule fired, those months were much better than the months that stayed locked in `weak_down`

## Current Judgment

What is now established:

- `monthly release from weak_down` is a valid research direction
- it improves the annual-only state-routing branch

What is not yet established:

- the current first-pass release signal is still not strong enough to replace fixed `60/40`

So the current interpretation should be:

- the framework is now better
- but the current release trigger is still too conservative or too sparse

## Best Next Step

The next refinement should stay narrow:

- keep annual `breadth_only` weak-state entry fixed
- keep release destination fixed at `neutral_flat`
- refine only the monthly release trigger

That means:

- do not reopen annual proxy search
- do not reopen budget mapping search
- do not jump directly to `strong_up`

## References

- [weak_down_exit_rule_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_rule_draft_v1.md)
- [weak_down_exit_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_rolling_validation_v1.md)
- [deterioration_state_proxy_formal_conclusion_v1.md](D:\hh\codex\v4\phase_2_momentum\deterioration_state_proxy_formal_conclusion_v1.md)
