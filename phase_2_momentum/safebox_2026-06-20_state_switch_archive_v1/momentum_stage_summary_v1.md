# Momentum Stage Summary V1

Scope:
- research window: `2014-01-01` to `2020-12-31`
- out-of-sample deployment window: `2021-05-31` to `2026-05-29`
- objective: summarize what has been established so far for the bank momentum line before moving to the next phase

## Core Findings

- `mom_6_1` is the strongest pure momentum signal in pre-2021 monthly research on average
- but `mom_6_1` is highly state-dependent and works mainly in clear trend-up years
- `mom_12_1` is weaker as pure momentum, but behaves more like a slow, durable bank-style filter
- direct neutralization improved research-layer rolling metrics, but did not improve out-of-sample JoinQuant deployment

## Supporting Evidence

Pre-2021 mechanism review:
- `mom_6_1` full pre-2021 average `rank_ic = 0.035067`, above `mom_12_1 = 0.010507`
- `mom_12_1` has stronger positive association with liquidity and `pb_ratio`, suggesting stronger style-loading than `mom_6_1`
- `mom_3_1` is weak overall and should not be treated as the main momentum backbone

Pre-2021 state review:
- trend-up years: `2017`, `2019`
- weak-down years: `2015`, `2018`, `2020`
- mixed-flat years: `2016`
- in `trend_up`, `mom_6_1` is best: `ic = 0.273155`, `spread = 0.027736`
- in `weak_down`, `mom_6_1` is worst of the main candidates: `ic = -0.112213`
- in `weak_down`, `mom_12_1` is still weak, but damage is smaller and spread is slightly positive: `0.000305`

Out-of-sample deployment:
- `v1` remained the best practical execution baseline
- `v2` neutralized version underperformed `v1`
- `v3` pure `mom_6_1` version failed clearly in the `2021-2026` JoinQuant run
- the state-switch branch produced a strong pre-2021 research candidate, but the original `state_score_v2` used a future-defined component and therefore could not be promoted directly
- the executable observable-proxy state-switch version achieved positive out-of-sample return, but did not show strong enough quality to replace `v1`

## Current Judgment

- if the question is `which signal is stronger in research alpha terms`, the answer is `mom_6_1`
- if the question is `which backbone is safer for annual refresh plus monthly execution deployment`, the answer is closer to `mom_12_1`
- therefore the present momentum line should be understood as a trade-off between offensive trend capture and cross-state survivability
- state-switch remains the most interesting momentum upgrade path, but it is still archived as a research candidate rather than a promoted deployment line

## Process Discipline

- the `2021-05-31` onward JoinQuant window is now frozen as out-of-sample acceptance
- do not continue tuning factor plans on the same out-of-sample segment
- any future redesign must be justified by pre-2021 train/validation research

## Practical Impact

- keep `joinquant_v4_monthly_momentum_strategy_v1.py` as the archived deployment baseline
- treat `v2` and `v3` as negative out-of-sample validation branches
- treat the state-switch branch as a positive research branch with an unresolved observability problem
- separate future momentum research from mean-reversion research instead of mixing the two explanations

## Reference Files

- [momentum_pre2021_mechanism_review_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_pre2021_mechanism_review_v1.md)
- [momentum_pre2021_state_review_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_pre2021_state_review_v1.md)
- [momentum_joinquant_v1_v2_comparison_2021_2026.md](D:\hh\codex\v4\phase_2_momentum\momentum_joinquant_v1_v2_comparison_2021_2026.md)
- [momentum_state_switch_final_acceptance_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_final_acceptance_v1.md)
- [README.md](D:\hh\codex\v4\phase_2_momentum\README.md)
