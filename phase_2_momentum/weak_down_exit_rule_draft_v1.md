# Weak Down Exit Rule Draft V1

Objective:
- keep the annual fundamental-deterioration rule as the `slow risk-off trigger`
- add a higher-frequency `weak_down exit` rule so the dual-engine branch can recover faster after a repair phase begins

## Why This Branch Is Needed

What current results suggest:
- annual deterioration-based routing can identify when the portfolio should turn defensive
- but the current executable version recovers too slowly after the weak state begins to repair
- this likely explains why:
- `fixed_60_40` stayed the best out-of-sample execution line
- `breadth_only` was defensively reasonable but still did not beat the fixed baseline
- `delta_median_only` became too conservative

So the bottleneck is now more likely:
- `exit timing from weak_down`
- not the existence of a weak-state trigger itself

## Target Structure

The intended state machine should become:

1. annual low-frequency rule decides whether to enter `weak_down`
2. monthly higher-frequency rule decides whether `weak_down` can be released early

This means:
- annual fundamentals handle `brake on`
- monthly price or momentum repair handles `brake off`

## Frozen Entry Rule

Do not change this part in the next branch:

- `weak_down` entry still comes from the annual deterioration-state proxy
- preferred annual branch for now remains:
- primary candidate: `delta_median_only`
- robust backup: `breadth_only`

## Exit Rule Design Principle

The exit rule should be:

- higher frequency than annual
- observable in real time
- simpler than the annual deterioration layer
- designed only to release `weak_down`, not to redefine the whole state system

So the first branch should avoid:

- rebuilding a full monthly 3-state classifier
- reopening the broad state-proxy search
- mixing too many new variables at once

## Recommended First-Pass Exit Candidates

Candidate A:
- monthly cross-sectional momentum repair
- example intuition:
- if the bank cross-section shows enough recovery in medium-term momentum breadth, release from `weak_down` to `neutral_flat`

Candidate B:
- monthly index-level trend repair
- example intuition:
- if the bank benchmark or bank-sector ETF price moves back above a medium moving average, release from `weak_down`

Candidate C:
- monthly bank-universe positive-ratio repair
- example intuition:
- if enough bank stocks recover into positive `mom_6_1` or `mom_3_1`, release from `weak_down`

## Recommended First Branch Scope

The cleanest next experiment should be:

- annual deterioration rule decides `weak_down`
- if not in `weak_down`, keep the current annual routed budget unchanged
- if in `weak_down`, check a monthly repair signal
- if monthly repair signal is not triggered:
- stay at `100%` fundamental + `0%` momentum
- if monthly repair signal is triggered:
- upgrade only to `neutral_flat`
- meaning `80%` fundamental + `20%` momentum

Important discipline:
- the first exit branch should not jump directly from `weak_down` to `strong_up`
- it should only test whether an earlier release to `neutral_flat` is enough

## Why `Weak Down -> Neutral Flat` First

This is the safest first design because:

- it tests whether the problem is delayed recovery
- it avoids overfitting an aggressive re-risk rule
- it preserves the annual deterioration layer as the main defensive anchor

In other words:
- we first test `partial release`
- not `full risk-on restoration`

## Most Natural First Observable Exit Candidate

Given existing momentum research, the most natural first observable exit signal is:

- monthly bank cross-sectional repair in medium-term momentum breadth

Reason:
- our earlier momentum work already showed that `mom_6_1` is the more offensive signal when trend conditions improve
- so using a monthly repair breadth measure to re-enable only a small momentum sleeve is economically consistent

## Proposed First Executable Rule Shape

Annual layer:
- if annual deterioration state is `weak_down`, enter defensive mode

Monthly exit layer:
- if a monthly repair signal exceeds its train-set threshold:
- release from `weak_down` to `neutral_flat`
- set budget to `80%` fundamental + `20%` momentum

Otherwise:
- stay in `weak_down`
- keep `100%` fundamental + `0%` momentum

## Research Discipline

The next branch should compare only:

- fixed `60/40`
- annual-only state routing
- annual entry plus monthly weak-down exit routing

Do not compare:

- many new state variants
- new annual proxies
- new engine score mixes

## Success Condition

The branch is worth keeping only if:

- it recovers some of the return lost by the annual-only state-routed versions
- without giving back too much of the drawdown or volatility improvement

So the target profile is:

- closer return to `fixed_60_40`
- while keeping some of the lower beta and lower volatility profile of `breadth_only` or `delta_median_only`

## Current Judgment

The most plausible next explanation is:

- the annual weak-state entry rule is usable
- the missing piece is a faster `repair / exit` layer

That makes `monthly weak_down release` the highest-priority next branch.

## References

- [deterioration_state_proxy_formal_conclusion_v1.md](D:\hh\codex\v4\phase_2_momentum\deterioration_state_proxy_formal_conclusion_v1.md)
- [joinquant_v4_state_routed_dual_engine_strategy_v1_note.md](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_state_routed_dual_engine_strategy_v1_note.md)
- [momentum_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_stage_summary_v1.md)
- [momentum_state_switch_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_candidate_v1.md)
