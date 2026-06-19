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

## Current Judgment

What has been proven:
- the state filter is not random noise
- it improves pure `mom_6_1`
- it gives a plausible explanation for when medium-term momentum should be trusted more

What has not been proven:
- it has not yet shown enough robustness to replace the current `mom_12_1`-anchored deployment baseline
- in anchored review, it still lagged pure `mom_12_1`

So the current status should be:
- `candidate`, not `main line`

## Recommended Next Step

Most reasonable next move:
- refine the state-switch logic inside pre-2021 research only

Examples:
- test whether middle-state months should also use `mom_6_1`
- test whether low-state months should go to `mom_12_1` or to a more defensive fallback
- test whether `state_score_v2` should rebalance component weights

Promotion rule:
- only consider promoting this line if a stricter pre-2021 anchored or rolling-style validation can consistently beat pure `mom_6_1` and remain competitive with pure `mom_12_1`

## References

- [momentum_forward_state_score_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_score_v1.md)
- [momentum_state_switch_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_validation_v1.md)
- [momentum_state_switch_anchored_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_anchored_validation_v1.md)
- [momentum_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_stage_summary_v1.md)
