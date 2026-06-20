# Phase 2 Success Summary 2026-06-19

This summary freezes the current successful outcomes of the bank `Phase 2` research branch, including the completed momentum stage conclusions and the first confirmed mean-reversion findings.

## Momentum

Established conclusions:
- `mom_6_1` is the stronger pure momentum signal in pre-2021 bank cross-sectional research
- but `mom_6_1` is strongly state-dependent and works mainly in clear trend-up environments
- `mom_12_1` is weaker as pure momentum, but behaves more like a slower and more durable deployment backbone

Deployment conclusions:
- the frozen out-of-sample deployment baseline remains [joinquant_v4_monthly_momentum_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_monthly_momentum_strategy_v1.py)
- `v2` neutralized and `v3` pure `mom_6_1` both failed to beat that baseline in the frozen `2021-05-31` to `2026-05-29` JoinQuant window
- therefore the current safe interpretation is: `mom_6_1` is better for research alpha, while the `mom_12_1`-anchored structure is safer for deployment

Next-generation candidate:
- the most promising upgrade candidate is [momentum_state_switch_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_candidate_v1.md)
- its logic is: use `mom_6_1` in high-state months and fall back to `mom_12_1` otherwise
- it passed first-layer pre-2021 evidence, but has not yet earned promotion to the deployment main line

Key references:
- [momentum_conclusion_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_conclusion_summary_v1.md)
- [momentum_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_stage_summary_v1.md)
- [momentum_state_switch_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_candidate_v1.md)

## Mean Reversion

Data and research setup:
- first-pass mean-reversion research can start without a new download
- the existing daily panel already covers all required base fields, and the required missing items are derivable
- the first mean-reversion factor panel is now available in [mean_reversion_factor_panel_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_factor_panel_v1.csv)

Single-factor findings:
- the first confirmed mean-reversion signal is `rev_5d`
- its effective direction is `smaller_better`, meaning recent short-term losers show rebound tendency
- longer reversal windows such as `rev_10d` and `rev_20d` did not survive validation and likely mix into trend continuation instead of pure rebound

Composite findings:
- the current strongest mean-reversion candidate is `rev5_abnvol`
- this means `short-term selloff + abnormal volume` is stronger than plain short-term reversal
- in anchored validation, `rev5_abnvol` slightly beat raw `rev_5d` in both `2019` validation and `2020` review

Execution findings:
- standalone tactical execution prefers `weekly` over `daily` on the frozen V1 spec
- but the first weekly `rev5_abnvol` overlay did **not** improve the real annual approved-pool baseline in the frozen post-2021 acceptance window
- entry-timing tests are more promising than full replacement:
  - return-first candidate: `timed_entry_rev5_abnvol`
  - practical balance candidate: `staggered_entry_50_50`
- sell-side take-profit tests are weaker:
  - a minimal partial trim rule reduced drawdown a bit
  - but it also reduced total return materially
- so the current branch ranking is: `buy-side timing` stronger than `sell-side trimming`
- therefore mean reversion currently remains a valid tactical branch, but not an approved default execution override for the annual backbone

Interpretation:
- bank mean reversion currently looks like a short-horizon tactical repair signal
- it is better viewed as a weekly tactical layer, not as a third annual-update backbone alongside fundamentals and momentum
- current evidence supports keeping the branch alive as an execution and entry-timing layer, but not promoting it into the main deployment stack yet
- among current use cases, entry timing has the strongest evidence and stop-profit has only weak supporting evidence

Key references:
- [mean_reversion_field_coverage_check_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_field_coverage_check_v1.md)
- [mean_reversion_single_factor_test_results_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_single_factor_test_results_v1.md)
- [mean_reversion_composite_test_results_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_composite_test_results_v1.md)
- [mean_reversion_anchored_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_anchored_validation_v1.md)
- [mean_reversion_execution_comparison_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_execution_comparison_v1.md)
- [mean_reversion_overlay_conclusion_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_overlay_conclusion_v1.md)
- [mean_reversion_entry_timing_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_entry_timing_summary_v1.md)
- [mean_reversion_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_stage_summary_v1.md)

## Process Discipline

- the `2021-05-31` onward JoinQuant window is frozen as out-of-sample acceptance for momentum
- do not continue tuning momentum plans against that same out-of-sample segment
- mean-reversion should proceed as a separate short-horizon research branch and should not be mixed into the momentum explanation layer
