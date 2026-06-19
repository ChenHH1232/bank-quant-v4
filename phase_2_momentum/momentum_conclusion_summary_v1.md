# Momentum Conclusion Summary V1

Current conclusion:
- `mom_6_1` is the stronger pure momentum signal in pre-2021 bank cross-sectional research
- but `mom_6_1` is strongly state-dependent and works mainly in clear trend-up environments
- `mom_12_1` is weaker as pure momentum, but behaves more like a slow and durable bank-style filter

Deployment conclusion:
- the current out-of-sample deployment baseline remains [joinquant_v4_monthly_momentum_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_monthly_momentum_strategy_v1.py)
- `v2` neutralized and `v3` pure `mom_6_1` both failed to beat that baseline in the frozen `2021-05-31` to `2026-05-29` out-of-sample window
- so the safest current judgment is: `mom_6_1` is better for research alpha, while the `mom_12_1`-anchored structure is safer for deployment

Upgrade direction:
- the most promising next-generation candidate is [momentum_state_switch_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_candidate_v1.md)
- its logic is: use `mom_6_1` in high-state months and fall back to `mom_12_1` otherwise
- this candidate has passed first-layer pre-2021 evidence, but has not yet earned promotion to the deployment main line

Process discipline:
- the `2021-05-31` onward JoinQuant window is frozen as out-of-sample acceptance
- do not keep tuning momentum plans against that same out-of-sample segment
- future redesign must come from pre-2021 train and validation research only
