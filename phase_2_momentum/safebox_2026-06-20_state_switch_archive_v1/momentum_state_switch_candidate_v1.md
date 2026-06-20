# Momentum State-Switch Candidate V1

Positioning:
- this is the strongest next-generation momentum candidate discovered after the pure `mom_6_1` and pure `mom_12_1` reviews
- it is not yet the promoted deployment main line
- it should be treated as a research candidate that has passed first-layer evidence but not full promotion

## Candidate Definition

Signal backbone:
- use `state_score_v1` as a forward state proxy
- if state is high, use `mom_6_1`
- otherwise use `mom_12_1`

Current `state_score_v1` components:
- `cross_mcap_median` with positive sign
- `cross_mom6_positive_ratio` with positive sign
- `cross_target_dispersion` with positive sign
- `cross_money_median` with negative sign

Interpretation:
- high score means the bank cross-section looks more favorable to medium-term momentum continuation
- low or middle score means the environment is less suitable for aggressive `6-1`, so the line falls back to the slower `12-1` backbone

## Evidence

State-score evidence:
- next-period pool mean return correlation: `0.207763`
- next-period `mom_6_1` IC correlation: `0.420968`
- next-period `mom_12_1` IC correlation: `0.216621`
- top-score months average `mom_6_1` IC: `0.290998`
- bottom-score months average `mom_6_1` IC: `-0.174415`

Full pre-2021 research validation:
- state-switch total return: `0.965717`
- pure `mom_6_1` total return: `0.776271`
- pure `mom_12_1` total return: `0.828058`
- this means the simple switch rule beat both single-backbone versions on the full pre-2021 sample

Anchored validation:
- train threshold estimation: `2015-01` to `2018-12`
- validation application: `2019`
- review application: `2020`

Anchored results:
- `2019` validation: switch `0.638735`, pure `mom_6_1` `0.582844`, pure `mom_12_1` `0.561352`
- `2020` review: switch `0.120102`, pure `mom_6_1` `0.070221`, pure `mom_12_1` `0.158686`

Rolling train/test results:
- feasible monthly pre-2021 rolling sample is only `2015-01` to `2020-12`, so the practical protocol is `48m train + 12m test`
- fold count: `13`
- mean test total return:
  - switch `0.169637`
  - pure `mom_6_1` `0.119686`
  - pure `mom_12_1` `0.180519`
- win counts:
  - switch > `mom_6_1`: `13 / 13`
  - switch > `mom_12_1`: `1 / 13`

Rolling interpretation:
- the switch rule consistently improves pure `mom_6_1`
- but it still fails to beat pure `mom_12_1` in most out-of-train windows
- so the state filter has real protective value, but not enough promotion evidence yet

Mid-state routing refinement:
- under the same `48m train + 12m test` rolling protocol, multiple middle-state variants were compared
- current best rule remains the original baseline:
  - `high_only_mom6_baseline` mean test return `0.169637`
- weaker alternatives:
  - `high_use_mom6_low_blend` mean test return `0.161652`
  - `all_non_low_blend` mean test return `0.157938`
  - `high_use_mom6_mid_blend` mean test return `0.152544`
  - `high_mid_use_mom6` mean test return `0.135524`

Mid-state refinement interpretation:
- pushing middle-state months toward `mom_6_1` weakens the rule
- the current evidence says middle-state months should still stay on the slower `mom_12_1` backbone

State-score V2 refinement:
- a stronger `state_score_v2` was then tested with:
  - `cross_mcap_median` `+`
  - `cross_target_dispersion` `+`
  - `cross_mom6_top_bottom_spread` `+`
  - `cross_money_median` `-`
- proxy-layer results:
  - corr to next-period `mom_6_1` IC: `0.334931`
  - corr to next-period `mom_12_1` IC: `0.161464`
  - forward return top-third minus bottom-third gap improved visibly
- rolling switch comparison under the same `48m train + 12m test` protocol:
  - `state_score_v1` mean switch return `0.169637`
  - `state_score_v2` mean switch return `0.189160`
  - pure `mom_12_1` mean return `0.180519`
  - `state_score_v2` beat `state_score_v1` in `5 / 13` folds
  - `state_score_v2` beat pure `mom_12_1` in `4 / 13` folds

State-score V2 interpretation:
- this is the first state-switch variant whose mean rolling test return moved above pure `mom_12_1`
- but the fold win rate versus `mom_12_1` is still not dominant
- so `state_score_v2` becomes the new preferred research candidate, but still not a promoted deployment main line

## Current Judgment

What has been proven:
- the state filter is not random noise
- it improves pure `mom_6_1`
- it gives a plausible explanation for when medium-term momentum should be trusted more
- in rolling train/test, it protects against `mom_6_1` overuse very consistently
- a refined `state_score_v2` can lift average rolling switch return above pure `mom_12_1` on mean outcome

What has not been proven:
- it has not yet shown enough robustness to replace the current `mom_12_1`-anchored deployment baseline
- in anchored review, it still lagged pure `mom_12_1`
- in rolling train/test, it also lagged pure `mom_12_1` in `12 / 13` folds
- even with `state_score_v2`, fold-by-fold dominance versus pure `mom_12_1` is still not strong enough

So the current status should be:
- `preferred candidate`, not `main line`

Formal frozen candidate:
- [momentum_state_switch_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_formal_candidate_v1.md)
- current exact rule = `state_score_v2 + top33_use_mom6 + otherwise mom_12_1`

## Recommended Next Step

Most reasonable next move:
- freeze `state_score_v2` as the current best switch candidate
- then run one stricter pre-2021 confirmation layer before any OOS promotion attempt

Examples:
- test whether low-state months should go to `mom_12_1` or to a more defensive fallback
- if needed, test whether `state_score_v2` should use stricter high-state cutoffs instead of new factor mixing

Promotion rule:
- only consider promoting this line if a stricter pre-2021 anchored or rolling-style validation can consistently beat pure `mom_6_1` and remain competitive with pure `mom_12_1`

## References

- [momentum_forward_state_score_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_score_v1.md)
- [momentum_forward_state_score_v2.md](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_score_v2.md)
- [momentum_state_switch_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_validation_v1.md)
- [momentum_state_switch_anchored_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_anchored_validation_v1.md)
- [momentum_state_switch_rolling_validation_v2.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v2.md)
- [momentum_state_switch_rolling_validation_v3.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_rolling_validation_v3.md)
- [momentum_state_switch_midstate_test_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_midstate_test_v1.md)
- [momentum_state_switch_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_formal_candidate_v1.md)
- [momentum_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_stage_summary_v1.md)
