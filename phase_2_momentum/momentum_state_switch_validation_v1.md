# Momentum State Switch Validation V1

Scope:
- sample window: `2014-01-01` to `2020-12-31`
- switching rule: high `state_score_v1` months use `mom_6_1`, all other months use `mom_12_1`
- purpose: test whether a simple forward state filter can make medium-term momentum more deployable than pure `mom_6_1`

Result summary:
- months: `72`
- switch total return: `0.965717`
- switch annualized return: `0.119232`
- pure `mom_6_1` total return: `0.776271`
- pure `mom_6_1` annualized return: `0.100487`
- pure `mom_12_1` total return: `0.828058`
- pure `mom_12_1` annualized return: `0.105770`
- high-state months using `mom_6_1`: `24`
- mid-state months using `mom_12_1`: `24`
- low-state months using `mom_12_1`: `24`

Interpretation:
- if the switch line beats pure `mom_6_1`, then state filtering is a viable path for medium-term momentum deployment
- if it also competes with or beats pure `mom_12_1`, then the state score is strong enough to justify further refinement
- this remains a pre-2021 research validation, not an out-of-sample deployment result

Output:
- [momentum_state_switch_validation_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_validation_v1.csv)
