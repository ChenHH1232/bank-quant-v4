# V4 Full Project Report 2026-06-24

Date: `2026-06-24`

## 1. Report Purpose

This report is a full-project consolidation note for `v4`.

It summarizes:

- where the project started
- how the research branched
- which lines were validated, downgraded, or rejected
- which methodology corrections changed the workflow
- what the final formal ranking is
- which files now represent the production-facing candidate set

This is intended to be the long-form handoff document for any later review, deep analysis, or external reasoning pass.

## 2. Project Scope

The `v4` project is a bank-stock strategy research stack centered on A-share listed banks.

The research eventually separated into two major code and document domains:

- `phase_1_fundamental`
  - annual pure-fundamental selection
  - branch comparisons
  - defensive overlay work
  - JoinQuant execution versions
- `phase_2_momentum`
  - monthly/quarterly momentum
  - dual-engine fundamental + momentum combination tests
  - mean-reversion and timing-style side research

At a high level, V4 began with a broad idea:

- fundamental selection should be the strategic base
- momentum might improve path or add alpha
- mean reversion might help entry timing or short-horizon refinement
- defensive overlay might reduce absolute drawdown

By the end of the current cycle, the project no longer treats those four ideas as equal citizens.

The central conclusion is now:

> under the current A-share bank sample and execution framework, the effective core of the strategy is fundamental selection, and risk control should be handled independently rather than relying mainly on momentum to dilute equity exposure

Source:

- [v4_final_structure_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/v4_final_structure_2026-06-23.md)

## 3. Core Directory Map

The most important current files are:

### Final decision layer

- [v4_final_structure_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/v4_final_structure_2026-06-23.md)
- [v4_final_candidate_ranking_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/v4_final_candidate_ranking_2026-06-23.md)
- [safebox_2026-06-24_v4_finalization_v1/safebox_note.md](D:/hh/codex/v4/safebox_2026-06-24_v4_finalization_v1/safebox_note.md)

### Current overlay-enhanced JoinQuant code

- [joinquant_v4_annual_backtest_strategy_manual_style_shortbond_overlay_switch_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_manual_style_shortbond_overlay_switch_v1.py)

### Current plain pure-fundamental JoinQuant code

- [joinquant_v4_annual_backtest_strategy_base_core_6_manual_style_switch_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_base_core_6_manual_style_switch_v1.py)

### Final overlay rolling evidence

- [build_balanced_corelevel_shortbond_overlay_rolling_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_balanced_corelevel_shortbond_overlay_rolling_validation_v1.py)
- [balanced_corelevel_shortbond_overlay_rolling_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/balanced_corelevel_shortbond_overlay_rolling_validation_v1.md)
- [balanced_corelevel_shortbond_overlay_rolling_validation_v1_config_results.csv](D:/hh/codex/v4/phase_1_fundamental/balanced_corelevel_shortbond_overlay_rolling_validation_v1_config_results.csv)

### Final momentum rejection evidence

- [build_fundamental_momentum_dual_engine_rolling_test_v3.py](D:/hh/codex/v4/phase_2_momentum/build_fundamental_momentum_dual_engine_rolling_test_v3.py)
- [fundamental_momentum_dual_engine_rolling_test_v3.md](D:/hh/codex/v4/phase_2_momentum/fundamental_momentum_dual_engine_rolling_test_v3.md)
- [dual_engine_joinquant_manual_style_switch_summary_2026-06-23.md](D:/hh/codex/v4/phase_2_momentum/dual_engine_joinquant_manual_style_switch_summary_2026-06-23.md)
- [joinquant_v4_dual_engine_manual_style_switch_v1.py](D:/hh/codex/v4/phase_2_momentum/joinquant_v4_dual_engine_manual_style_switch_v1.py)

### Methodology correction and validation discipline

- [v4_methodology_correction_memo_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/safebox_2026-06-23_manual_style_switch_mainline_v1/v4_methodology_correction_memo_2026-06-23.md)
- [three_step_followup_summary_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/three_step_followup_summary_2026-06-23.md)
- [execution_faithful_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1.md)
- [execution_faithful_validation_v1_joinquant_checklist.md](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1_joinquant_checklist.md)

## 4. Original Working Thesis

The early V4 logic was broad and exploratory.

The implicit thesis was something like:

1. annual fundamental factor selection can define the main candidate bank basket
2. momentum may help with trend capture or risk-aware allocation
3. mean reversion may improve timing around entries
4. defensive overlay may reduce deep drawdowns during deterioration phases

At that stage, the project still had a strong “research completeness” bias:

- more factors seemed potentially useful
- more dynamic switching rules still looked worth testing
- the combination of fundamental + momentum + tactical timing still looked conceptually attractive

The project later moved away from that mindset after repeated rolling-vs-JoinQuant discrepancies.

## 5. Pure Fundamental Main-Line Development

### 5.1 From broader base to `base_core_6`

The pure-fundamental line gradually simplified.

One of the important transitions was:

- from a broader 7-factor shell
- to a more stable 6-factor shell

The crucial structural change was effectively:

- remove `indicator__eps`
- allow `bank_indicator__core_level_capital_adequacy_ratio` to compete as a replacement candidate

This replacement logic and its rolling evidence are preserved in:

- [build_base_core_6_replacement_rolling_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_base_core_6_replacement_rolling_validation_v1.py)
- [base_core_6_replacement_rolling_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/base_core_6_replacement_rolling_validation_v1.md)
- [base_core_6_vs_replace_eps_with_core_level_yearly_comparison_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/base_core_6_vs_replace_eps_with_core_level_yearly_comparison_2026-06-23.md)

The important conceptual result was:

- the project did not land on “one fixed universal factor list forever”
- instead it landed on two robust structural lines derived from the same annual refresh process

Those two lines became:

- `balanced`
  - base execution line
- `core_level_shadow`
  - structural side line replacing `eps` with `core_level_capital_adequacy_ratio`

### 5.2 Manual style switch as temporary framing

At one stage, the project used a manual-style-switch framing:

- [joinquant_v4_annual_backtest_strategy_base_core_6_manual_style_switch_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_base_core_6_manual_style_switch_v1.py)

This was useful because it let both branches live in one execution file:

- `balanced`
- `core_level`

But methodologically, the project later tightened the language:

- this did not prove reliable ex-ante human regime selection
- it only proved there was a valid structural alternative

That correction is explicitly recorded in:

- [v4_methodology_correction_memo_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/safebox_2026-06-23_manual_style_switch_mainline_v1/v4_methodology_correction_memo_2026-06-23.md)

### 5.3 Shadow tracking correction

The next correction was important:

- `core_level` was moved from “possible live manual switch” to “shadow tracking”

This means:

- live history should not be rewritten by after-the-fact branch picking
- `core_level` should remain visible as a structural benchmark
- future judgment about switching must be evaluated prospectively, not retrofitted

Key files:

- [pure_fundamental_shadow_tracking_note_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_shadow_tracking_note_2026-06-23.md)
- [pure_fundamental_shadow_decision_log_template_2026-06-23.csv](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_shadow_decision_log_template_2026-06-23.csv)
- [pure_fundamental_manual_style_switch_guide_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_manual_style_switch_guide_2026-06-23.md)
- [pure_fundamental_two_branch_summary_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_two_branch_summary_2026-06-23.md)

## 6. Momentum Branch Development

### 6.1 Why momentum stayed alive for a long time

Momentum was not kept alive by theory alone.

It had real intermediate evidence:

- pre-2021 rolling showed that separate-sleeve combinations could improve cumulative results
- inside those rolling tests, different fundamental sleeves paired with momentum differently
- at one point the project had a plausible case that momentum might be a valid defensive or path-smoothing layer

The final rolling test packet for that stage is:

- [fundamental_momentum_dual_engine_rolling_test_v3.md](D:/hh/codex/v4/phase_2_momentum/fundamental_momentum_dual_engine_rolling_test_v3.md)

That rolling packet said, in essence:

- `balanced` was the stronger `60/40` sleeve
- `core_level_shadow` was the stronger `70/30` sleeve
- the momentum sleeve was still competitive enough to justify JoinQuant confirmation

### 6.2 Dual-engine JoinQuant test

The project then promoted the dual-engine idea into JoinQuant code:

- [joinquant_v4_dual_engine_manual_style_switch_v1.py](D:/hh/codex/v4/phase_2_momentum/joinquant_v4_dual_engine_manual_style_switch_v1.py)

The corresponding execution summary is:

- [dual_engine_joinquant_manual_style_switch_summary_2026-06-23.md](D:/hh/codex/v4/phase_2_momentum/dual_engine_joinquant_manual_style_switch_summary_2026-06-23.md)

The important finding was not just “momentum failed”.

The more precise finding was:

- in this project’s A-share bank sample
- under `mom_12_1`
- under the independent sleeve-combination framework

momentum mostly did this:

- lowered beta
- lowered volatility
- sometimes reduced absolute drawdown

But it also systematically weakened:

- annualized return
- excess return
- alpha
- Sharpe

That is a very specific conclusion.

The project explicitly tightened the language so as not to overclaim:

- not “momentum theory does not work for all bank stocks”
- but “in this project scope and execution framework, momentum did not show stable incremental alpha”

### 6.3 Why rolling did not override JoinQuant

This became one of the most important discipline rules in V4:

- local rolling is for candidate generation
- JoinQuant executable backtest is for acceptance or rejection

This matters because the gap between them can come from:

- sleeve overlap and re-normalization
- nonlinear stock caps
- more frequent rebalancing
- transaction frictions
- mapping differences between local approximations and executable holdings

So the final methodological rule became:

- rolling-positive is not production-ready
- JoinQuant acceptance is binding

### 6.4 Final disposition of momentum

Momentum is now formally outside the default V4 stack.

It is not erased from history.
It remains archived as a meaningful research branch.

But it no longer competes for the production main line.

## 7. Mean-Reversion Branch Development

Mean reversion also remained alive for a meaningful stretch of the project.

The repository still contains many mean-reversion-related files in `phase_2_momentum`, including:

- execution comparison work
- staged entry tests
- take-profit ideas
- factor panel work
- composite tests
- anchored and rolling validations

This branch mattered because it tested whether short-horizon tactical logic could sit on top of the annual pool.

But the project gradually moved away from it for several reasons:

- added complexity
- higher dependence on execution fidelity
- weak survival under executable confirmation compared with the best pure-fundamental lines
- low marginal value relative to unresolved methodology issues

By the final structure, mean reversion is formally rejected for the default strategy stack.

It is preserved as research history, not a current formal candidate.

## 8. Defensive Overlay Development

### 8.1 Why overlay was kept separate from stock selection

One of the most important conceptual improvements in V4 was learning to separate:

- stock-selection logic
- risk-control logic

Rather than mixing everything back into one scoring rule, the project gradually treated defensive overlay as its own product line.

That separation turned out to be correct.

### 8.2 Early overlay exploration

The repository contains multiple overlay experiments:

- raw overlay rolling validation
- year-over-year pool linear mapping versions
- treasury and shortbond variants
- persistence and exit-on-improve variants

Important earlier files include:

- [fundamental_defensive_overlay_project_summary_2026-06-22.md](D:/hh/codex/v4/phase_1_fundamental/fundamental_defensive_overlay_project_summary_2026-06-22.md)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_shortbond_6040_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_shortbond_6040_v1.py)

An important intermediate insight was:

- the old overlay candidate was tied to an older pure-fundamental base
- so once the pure-fundamental main line was upgraded, the overlay had to be retested on the new `balanced / core_level_shadow` base

### 8.3 Local neighborhood stability check

Before promoting shortbond overlay further, the project did a local stability check:

- [shortbond_6040_4055_local_neighborhood_check_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/shortbond_6040_4055_local_neighborhood_check_2026-06-23.md)

Main conclusion:

- `shortbond_6040_4055` did not look like an isolated spike
- the real edge was concentrated in the warning layer
- `warning_equity_weight = 60%` mattered more than additional threshold micro-tuning

This kept the branch alive, but at that point it was still not yet the final winner.

### 8.4 New overlay-on-current-mainline rolling check

The turning point came when overlay was retested directly on the two current pure-fundamental base lines:

- [build_balanced_corelevel_shortbond_overlay_rolling_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_balanced_corelevel_shortbond_overlay_rolling_validation_v1.py)
- [balanced_corelevel_shortbond_overlay_rolling_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/balanced_corelevel_shortbond_overlay_rolling_validation_v1.md)

This test asked a cleaner question:

- if we hold the fundamental base fixed at current accepted lines
- and apply the same `shortbond_6040_4055` overlay
- does the overlay still add value?

The answer was yes for both:

- `balanced` improved
- `core_level_shadow` improved

And the better review result belonged to:

- `core_level_shadow + shortbond_6040_4055`

This was a major structural shift in the project.

### 8.5 JoinQuant confirmation of overlay-enhanced lines

The overlay-enhanced lines were then promoted into unified JoinQuant code:

- [joinquant_v4_annual_backtest_strategy_manual_style_shortbond_overlay_switch_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_manual_style_shortbond_overlay_switch_v1.py)

This file allows `initialize` switching between:

- `balanced_shortbond_overlay`
- `core_level_shadow_shortbond_overlay`

The executable results changed the project ranking dramatically.

`balanced_shortbond_overlay`:

- strategy return = `51.41%`
- annualized = `8.94%`
- excess = `26.32%`
- Sharpe = `0.290`
- IR = `0.731`
- max drawdown = `21.83%`
- excess max drawdown = `11.66%`

`core_level_shadow_shortbond_overlay`:

- strategy return = `53.17%`
- annualized = `9.20%`
- excess = `27.79%`
- Sharpe = `0.313`
- IR = `0.791`
- max drawdown = `21.68%`
- excess max drawdown = `7.15%`

This moved overlay from:

- optional defensive research

to:

- formal top-ranked candidate layer

## 9. Methodology Corrections

Several important methodology corrections happened late in the cycle, and they are part of the real V4 result.

### 9.1 Correction: do not overstate style switching

The project learned to stop saying:

- “we already have a reliable manual switch strategy”

and instead say:

- `balanced` is the default line
- `core_level` is a structural variant
- manual switching is a future mechanism to validate, not a confirmed production framework

Source:

- [v4_methodology_correction_memo_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/safebox_2026-06-23_manual_style_switch_mainline_v1/v4_methodology_correction_memo_2026-06-23.md)

### 9.2 Correction: execution fidelity matters more than one more rule

The project explicitly recognized that the biggest remaining risk was no longer:

- missing another factor
- missing another threshold
- missing another switch

The biggest risk was:

- local rolling and JoinQuant not being execution-faithful to the same decision kernel

This led to the standalone validation track:

- [execution_faithful_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1.md)

### 9.3 Correction: stop treating all research branches symmetrically

By the end, the project explicitly stopped chasing:

- theoretical completeness
- symmetry between fundamental, momentum, and mean reversion

Instead it accepted asymmetry:

- fundamental is the real return engine
- overlay is the real risk-control layer
- momentum and mean reversion are not currently strong enough to remain formal candidates

## 10. Final Frozen Ranking

The final frozen ranking is:

1. `core_level_shadow_shortbond_overlay`
2. `balanced_shortbond_overlay`
3. `pure core_level_shadow`
4. `pure balanced`

Sources:

- [v4_final_candidate_ranking_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/v4_final_candidate_ranking_2026-06-23.md)
- [safebox_note.md](D:/hh/codex/v4/safebox_2026-06-24_v4_finalization_v1/safebox_note.md)

This means the final V4 structure is no longer:

- pure fundamental first
- overlay optional

It is now:

- overlay-enhanced pure-fundamental lines first
- plain pure-fundamental lines second
- momentum and mean-reversion branches archived

## 11. Final Production-Facing Interpretation

The project can now be described as four layers:

### 11.1 First main line

`core_level_shadow_shortbond_overlay`

This is the strongest current full-cycle branch.

It has:

- the highest return among the final candidates
- the highest excess return
- the highest Sharpe and IR
- lower drawdown than the plain pure-fundamental lines
- much better relative-path behavior than `balanced_shortbond_overlay`

### 11.2 Second main line

`balanced_shortbond_overlay`

This is the simpler overlay-backed production alternative.

It is meaningful because:

- it still clearly beats pure `balanced`
- it is easier to explain as “default balanced stock selection + external risk-control layer”

### 11.3 Plain reference lines

`pure core_level_shadow` and `pure balanced` are still useful.

They remain valuable as:

- structural benchmarks
- no-overlay controls
- explanatory baselines for future audits

But they are no longer top-ranked production candidates.

### 11.4 Archived side branches

Momentum and mean reversion are not deleted from project memory.

They remain archived as:

- important research history
- useful negative evidence
- possible future revisit topics if the data, universe, or execution structure changes

## 12. What Was Rejected

The following are now formally outside the default stack:

- fixed `mom_12_1` independent `40%` allocation
- monthly momentum style switching
- momentum-driven quality/profitability tilts
- general mean-reversion branch

The reason is not that they are theoretically impossible forever.

The reason is narrower and more precise:

- under the current A-share bank sample
- under the current factor definitions
- under the current execution framework

they did not justify formal promotion over the winning pure-fundamental + overlay lines.

## 13. What Remains Open

Even after final ranking freeze, some infrastructure work remains open.

The biggest open methodology project is still:

- execution-faithful validation

This matters because the project now has stronger strategy conclusions than infrastructure certainty.

The current best next non-strategy-expansion task is:

- reconcile local truth packets and JoinQuant execution on representative rebalance dates

That work is already scaffolded in:

- [build_execution_faithful_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_execution_faithful_validation_v1.py)
- [execution_faithful_validation_v1_joinquant_checklist.md](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1_joinquant_checklist.md)

## 14. Safebox and Archive State

Earlier narrow safeboxes still matter, especially:

- `phase_1_fundamental/safebox_2026-06-23_manual_style_switch_mainline_v1`
- `phase_1_fundamental/safebox_2026-06-23_pure_fundamental_two_branch_followup_v1`
- `phase_2_momentum/safebox_2026-06-22_allocation_vs_selection_v1`

But the final cross-branch consolidation packet is now:

- [safebox_2026-06-24_v4_finalization_v1/safebox_note.md](D:/hh/codex/v4/safebox_2026-06-24_v4_finalization_v1/safebox_note.md)

That safebox intentionally collects:

- final structure files
- final ranking files
- overlay rolling and JoinQuant code
- momentum rejection evidence
- execution-faithful validation packet

## 15. Final Bottom Line

The V4 project did not end by proving every originally attractive idea.

It ended by learning to rank them correctly.

The final lessons are:

1. annual fundamental selection is the true strategic core
2. `core_level_shadow` is a real structural improvement, not a cosmetic variant
3. momentum did not survive executable confirmation as a formal alpha layer
4. mean reversion did not survive as a necessary production component
5. risk control should be handled independently
6. shortbond overlay is strong enough to become part of the formal candidate stack
7. the best current branch is `core_level_shadow_shortbond_overlay`

So the real outcome of V4 is not “fundamental + momentum + mean reversion all coexist.”

The real outcome is:

- fundamental defines the stock engine
- overlay defines the risk-control engine
- everything else is judged by whether it survives executable evidence

That is the final structure currently frozen by the project.
