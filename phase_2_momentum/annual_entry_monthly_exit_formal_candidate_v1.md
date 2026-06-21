# Annual Entry Monthly Exit Formal Candidate V1

Conclusion:
- the current formal candidate for the state-routed dual-engine branch is:
- `annual breadth entry + monthly mom6 breadth exit`
- its preferred execution interpretation is now:
- `slow fundamental, fast exit`

This candidate should now be treated as the frozen next-step upgrade line for further research validation.

## Candidate Definition

Annual entry layer:
- annual weak-state trigger = `breadth_only`
- annual state score = `- deterioration_ratio`
- annual cut rule = train-set `q33 / q67`

Monthly exit layer:
- monthly repair signal = bank cross-sectional `mom_6_1` positive ratio
- monthly exit threshold = train-set `q50`
- release action = if annual state is `weak_down` and monthly repair signal reaches threshold, upgrade only to `neutral_flat`

Budget mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

Important restriction:
- the monthly exit layer does not create a new `strong_up`
- it only releases `weak_down` to `neutral_flat`

Preferred execution interpretation:
- the fundamental sleeve is treated as a slow layer
- on non-fundamental rebalance dates, it may sell down but may not rebuild new fundamental positions
- restored tactical risk budget should first reactivate the momentum sleeve

## Why This Candidate Was Promoted

What has now been established:

- annual deterioration-based weak-state entry is useful, but by itself recovers too slowly
- adding a monthly weak-down release layer improves the annual-only breadth route materially
- among the tested release triggers, `mom_6_1` repair breadth with `q50` was the best first-pass choice

## Evidence

Annual-only breadth route:
- cum return = `0.005463`

First monthly-exit version:
- annual breadth entry + monthly `mom6_positive_ratio_q67`
- cum return = `0.006663`

Refined best release trigger:
- annual breadth entry + monthly `mom6_positive_ratio_q50`
- cum return = `0.006799`

Preferred execution interpretation result:
- annual breadth entry + monthly `mom6_positive_ratio_q50` exit
- with `slow fundamental, fast exit` execution discipline
- cum return = `0.007116`

Reference baseline:
- fixed `60/40`
- cum return = `0.007940`

So the current ranking is:

1. fixed `60/40`
2. annual breadth entry + monthly `mom6_positive_ratio_q50` exit with `slow fundamental, fast exit`
3. annual breadth entry + monthly `mom6_positive_ratio_q50` exit unconstrained
4. annual breadth entry + monthly `mom6_positive_ratio_q67` exit
5. annual breadth-only route

## Interpretation

This means:

- the two-layer state machine is directionally correct
- the missing piece really was faster release from `weak_down`
- the best current release signal is still a momentum-breadth repair signal, which is also economically consistent with the broader momentum research
- adding a `slow fundamental, fast exit` execution boundary improves the candidate further and is now the preferred implementation reading

At the same time:

- this candidate still does not beat the fixed `60/40` baseline
- so it should be promoted only to `formal candidate` status, not deployment main line status

## Frozen Research Scope

From this point, the active branch should stay narrow:

- keep annual entry fixed at `breadth_only`
- keep monthly exit fixed at `mom6_positive_ratio_q50`
- keep release destination fixed at `neutral_flat`
- keep the preferred execution reading fixed at `slow fundamental, fast exit`

Do not reopen:

- annual state proxy search
- broader monthly repair variable search
- aggressive `weak_down -> strong_up` release jumps

## Current Role

This candidate is best understood as:

- the leading `repair-speed upgrade` branch for the dual-engine allocation layer

It is not yet:

- the promoted replacement for fixed `60/40`

## References

- [weak_down_exit_rule_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_rule_draft_v1.md)
- [weak_down_exit_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_rolling_validation_v1.md)
- [weak_down_exit_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_validation_note_v1.md)
- [weak_down_exit_signal_refinement_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_signal_refinement_v1.md)
- [slow_fundamental_fast_exit_execution_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_validation_note_v1.md)
- [deterioration_state_proxy_formal_conclusion_v1.md](D:\hh\codex\v4\phase_2_momentum\deterioration_state_proxy_formal_conclusion_v1.md)
