# Phase 2 Success Summary 2026-06-19

This summary freezes the current successful outcomes of the bank `Phase 2` research branch, including the completed momentum stage conclusions and the final archived interpretation of the mean-reversion branch.

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
- it passed first-layer pre-2021 evidence, but has not earned promotion to the deployment main line
- the strongest research version later exposed an observability problem because `state_score_v2` used a future-defined component
- the executable observable-proxy JoinQuant version was profitable, but still not strong enough to replace the baseline

Key references:
- [momentum_conclusion_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_conclusion_summary_v1.md)
- [momentum_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_stage_summary_v1.md)
- [momentum_state_switch_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_candidate_v1.md)
- [momentum_state_switch_final_acceptance_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_final_acceptance_v1.md)

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
- standalone tactical execution preferred `weekly` over `daily` on the frozen V1 spec
- but the standalone JoinQuant strategy still failed badly in the real `2021-05-31` to `2026-05-29` out-of-sample window:
  - strategy return = `-22.55%`
  - excess return = `-35.39%`
- the first weekly `rev5_abnvol` overlay also did **not** improve the annual approved-pool baseline in the frozen post-2021 acceptance window
- entry-timing tests were locally more promising than full replacement:
  - return-first candidate: `timed_entry_rev5_abnvol`
  - practical balance candidate: `staggered_entry_50_50`
- but the real JoinQuant comparison still favored direct annual entry over mean-reversion entry timing:
  - annual-pool mean-reversion entry strategy return = `37.13%`
  - annual-pool direct-entry strategy return = `44.51%`
- sell-side take-profit tests stayed weaker:
  - a minimal partial trim rule reduced drawdown a bit
  - but it also reduced total return materially
- so the current branch ranking is still: `buy-side timing` stronger than `sell-side trimming`
- however, the branch as a whole does not earn deployment promotion

Interpretation:
- bank mean reversion currently looks like a short-horizon tactical repair signal
- but it is not strong enough to become a formal third deployment line alongside fundamentals and momentum
- current evidence supports archiving the branch as a research conclusion rather than keeping it in the active deployment queue
- among current use cases, entry timing had the strongest local evidence, but it still failed final deployment confirmation
- stop-profit only has weak supporting evidence

Key references:
- [mean_reversion_field_coverage_check_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_field_coverage_check_v1.md)
- [mean_reversion_single_factor_test_results_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_single_factor_test_results_v1.md)
- [mean_reversion_composite_test_results_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_composite_test_results_v1.md)
- [mean_reversion_anchored_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_anchored_validation_v1.md)
- [mean_reversion_execution_comparison_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_execution_comparison_v1.md)
- [mean_reversion_overlay_conclusion_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_overlay_conclusion_v1.md)
- [mean_reversion_entry_timing_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_entry_timing_summary_v1.md)
- [mean_reversion_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_stage_summary_v1.md)
- [mean_reversion_final_archive_conclusion_v1.md](D:\hh\codex\v4\phase_2_momentum\mean_reversion_final_archive_conclusion_v1.md)

## Fundamental Plus Momentum Dual Engine

Research setup:
- the current dual-engine path keeps fundamentals and momentum logically separate
- the fundamental engine uses the approved annual or quasi-quarterly stock pool
- the momentum engine uses a monthly deployment-safe `mom_12_1` structure
- the two engines do not mix raw scores; they only interact at the final portfolio-allocation layer

Pre-2021 rolling evidence:
- the first-pass rolling test is archived in [fundamental_momentum_dual_engine_rolling_test_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_test_v1.md)
- within that constrained pre-2021 common-sample test, the blended allocations beat both single-engine baselines
- the current best first-pass blend is `60/40`, meaning `60%` fundamental budget plus `40%` momentum budget
- however, the current test is still conservative and constrained by strict `5%` single-engine stock caps and `8%` final stock caps
- under that setup, `fundamental_only` and `momentum_only` became identical, so the rolling evidence is useful but not yet fully discriminative

Post-2021 JoinQuant interpretation:
- the executable JoinQuant dual-engine version produced a stable but not dominant out-of-sample profile in the frozen `2021-05-31` to `2026-05-29` acceptance window
- current observed profile:
- strategy return = `35.54%`
- excess return = `13.08%`
- max drawdown = `13.74%`
- beta = `0.780`
- volatility = `0.138`
- compared with the stronger pure fundamental deployment line, the dual-engine version gives up return but improves stability materially

Current role:
- this branch should be interpreted as a `portfolio construction` or `risk-balancing` line, not as the new primary alpha main line
- it does prove that fundamental and momentum signals can coexist cleanly without forcing them into one mixed score
- at the current stage, the pure fundamental main line still keeps priority for return-seeking deployment
- the dual-engine branch is better viewed as a future allocation layer candidate for lower-drawdown capital

Key references:
- [fundamental_momentum_dual_engine_rolling_plan_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_plan_v1.md)
- [fundamental_momentum_dual_engine_rolling_test_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_test_v1.md)
- [joinquant_v4_dual_engine_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_dual_engine_strategy_v1.py)

## Process Discipline

- the `2021-05-31` onward JoinQuant window is frozen as out-of-sample acceptance for momentum
- do not continue tuning momentum plans against that same out-of-sample segment
- mean-reversion should proceed as a separate short-horizon research branch and should not be mixed into the momentum explanation layer
- dual-engine follow-up should also return to pre-2021 train and validation research first, rather than repeatedly tuning against the same frozen post-2021 acceptance window
