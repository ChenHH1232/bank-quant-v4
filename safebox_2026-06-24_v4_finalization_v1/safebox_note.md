# Safebox Note

Archive: `safebox_2026-06-24_v4_finalization_v1`

Date: `2026-06-24`

## Purpose

This safebox consolidates the final V4 decision packet after the latest JoinQuant executions changed the formal ranking.

It also captures several important files that had already been produced in the current V4 cycle but had not yet been copied into a dedicated safebox snapshot.

## Newly Backed Finalization Layer

These files represent the latest formal conclusion layer:

- `v4_final_candidate_ranking_2026-06-23.md`
- `v4_final_structure_2026-06-23.md`
- `balanced_corelevel_shortbond_overlay_rolling_validation_v1.md`
- `balanced_corelevel_shortbond_overlay_rolling_validation_v1_config_results.csv`
- `build_balanced_corelevel_shortbond_overlay_rolling_validation_v1.py`
- `joinquant_v4_annual_backtest_strategy_manual_style_shortbond_overlay_switch_v1.py`

Why they matter:

- they freeze the new final ranking
- they document the shortbond overlay promotion from optional defensive study to formal candidate layer
- they preserve the initialize-switch JoinQuant implementation for the two overlay-enhanced main lines

## Newly Backed Supporting Research Layer

These files were also copied because they remained important to the current final decision logic and had not yet been gathered into one final archive packet:

- `shortbond_6040_4055_local_neighborhood_check_2026-06-23.md`
- `three_step_followup_summary_2026-06-23.md`
- `execution_faithful_validation_v1.md`
- `execution_faithful_validation_v1_joinquant_checklist.md`
- `execution_faithful_validation_v1_local_summary.csv`
- `execution_faithful_validation_v1_local_detail.csv`
- `dual_engine_joinquant_manual_style_switch_summary_2026-06-23.md`
- `fundamental_momentum_dual_engine_rolling_test_v3.md`
- `fundamental_momentum_dual_engine_rolling_test_v3_detail.csv`
- `joinquant_v4_dual_engine_manual_style_switch_v1.py`

Why they matter:

- they preserve the evidence trail for formally rejecting the momentum dual-engine line
- they keep the execution-faithful validation project attached to the final V4 record
- they preserve the last validated dual-engine JoinQuant implementation as an archived research branch

## Relationship To Earlier Safeboxes

Earlier focused safeboxes remain valid and are not superseded as detailed research snapshots, especially:

- `phase_1_fundamental/safebox_2026-06-23_manual_style_switch_mainline_v1`
- `phase_1_fundamental/safebox_2026-06-23_pure_fundamental_two_branch_followup_v1`
- `phase_2_momentum/safebox_2026-06-22_allocation_vs_selection_v1`

This safebox is the final cross-branch consolidation packet, not a replacement for every narrower research archive.

## Explicitly Not Backed Here

The following were intentionally not treated as final archive artifacts in this packet:

- shell history files such as `.Rhistory`
- temporary debug folders such as `tmp_*`
- temporary image files
- broad legacy untracked research files that were not part of the current final ranking update

## Frozen Final Ranking

The formal candidate ordering frozen by this safebox is:

1. `core_level_shadow_shortbond_overlay`
2. `balanced_shortbond_overlay`
3. `pure core_level_shadow`
4. `pure balanced`
