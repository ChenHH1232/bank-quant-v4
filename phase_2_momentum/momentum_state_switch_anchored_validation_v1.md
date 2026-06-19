# Momentum State Switch Anchored Validation V1

Protocol:
- train period: `2015-01` to `2018-12`
- validation period: `2019-01` to `2019-12`
- review period: `2020-01` to `2020-12`
- thresholds are estimated only from the train-period `state_score_v1` distribution
- switching rule: high state uses `mom_6_1`, otherwise use `mom_12_1`

Train thresholds:
- q33=`-0.224557`
- q67=`0.263670`

Validation 2019:
- switch total return=`0.638735`
- switch annualized=`0.638735`
- pure mom_6_1 total return=`0.582844`
- pure mom_12_1 total return=`0.561352`
- high-state months=`3`

Review 2020:
- switch total return=`0.120102`
- switch annualized=`0.120102`
- pure mom_6_1 total return=`0.070221`
- pure mom_12_1 total return=`0.158686`
- high-state months=`3`

Interpretation:
- if the switch line beats pure `mom_6_1` in both 2019 validation and 2020 review, the state filter has real promise
- if it only helps in validation but not review, the score is still informative but not robust enough yet

Output:
- [momentum_state_switch_anchored_validation_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_anchored_validation_v1.csv)
