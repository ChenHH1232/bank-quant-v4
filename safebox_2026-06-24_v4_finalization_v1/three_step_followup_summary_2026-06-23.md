# Three-Step Follow-Up Summary 2026-06-23

Date: `2026-06-23`

This note consolidates the three follow-up tasks we just completed:

1. `shortbond_6040_4055` local neighborhood check
2. execution-faithful validation project kickoff
3. `core_level` switched from live-branch discussion to shadow tracking

## 1. Short-Bond Defensive Overlay Neighborhood Check

Source note:

- [shortbond_6040_4055_local_neighborhood_check_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/shortbond_6040_4055_local_neighborhood_check_2026-06-23.md)

What we checked:

- local rolling robustness around the live defensive overlay candidate
- target point = `shortbond_6040_4055`
- local grid around it:
  - warning threshold `40% / 45%`
  - severe threshold `55% / 60%`
  - warning equity `60% / 80%`
  - severe equity `20% / 40%`

Main finding:

- this candidate does **not** look like an isolated local spike
- the meaningful edge is concentrated in the `warning` layer
- `warning_equity_weight = 60%` is clearly better than `80%`
- `warning_threshold 40/45` and `severe_threshold 55/60` are almost flat locally
- `severe_equity_weight 20/40` matters only slightly

Practical conclusion:

- the current short-bond branch already looks locally stable enough
- if we do one last minimal JoinQuant neighbor check, the best use is:
  - current live point = `6040_4055`
  - closest meaningful neighbor = `6020_4055`
- if `6020_4055` does not beat it in full backtest, we should stop micro-tuning this branch

## 2. Execution-Faithful Validation Project

Core files:

- [build_execution_faithful_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_execution_faithful_validation_v1.py)
- [execution_faithful_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1.md)
- [execution_faithful_validation_v1_joinquant_checklist.md](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1_joinquant_checklist.md)
- [execution_faithful_validation_v1_local_summary.csv](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1_local_summary.csv)
- [execution_faithful_validation_v1_local_detail.csv](D:/hh/codex/v4/phase_1_fundamental/execution_faithful_validation_v1_local_detail.csv)

Why we did it:

- the bigger risk now is not missing one more rule
- the bigger risk is local rolling and JoinQuant not being execution-faithful to each other
- if that gap is real, continuing to optimize rules will increase false confidence

What is frozen in v1:

- strategy scope = `base_core_7 + combo__ic_weight_train`
- selected rebalance dates:
  - `2021-05-06`
  - `2022-05-05`
  - `2024-05-06`
  - `2025-05-06`

Local truth packet already prepared:

- per stock:
  - local pool inclusion
  - raw factor values
  - standardized `z__*`
  - direction-adjusted `adj__*`
  - normalized factor weights
  - factor contribution
  - final score
  - descending rank
  - bucket
  - top-bucket flag
  - target weight
  - next-period return mapping

Local summary snapshot:

- `2021-05-06`: pool `26`, top `5`, target weight `0.2`
- `2022-05-05`: pool `27`, top `6`, target weight `0.1666666667`
- `2024-05-06`: pool `29`, top `6`, target weight `0.1666666667`
- `2025-05-06`: pool `31`, top `6`, target weight `0.1666666667`

Reconciliation order frozen:

1. pool membership
2. raw factor values
3. standardization
4. sign handling
5. final score and ranking
6. bucket / top-bucket selection
7. target weight
8. next-period return mapping

Practical conclusion:

- this is now a standalone small project
- next move should be a temporary JoinQuant debug export with the same fields and dates
- we should locate the first mismatch layer before touching strategy rules again

## 3. `core_level` Moved To Shadow Tracking

Core files:

- [pure_fundamental_shadow_tracking_note_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_shadow_tracking_note_2026-06-23.md)
- [pure_fundamental_shadow_decision_log_template_2026-06-23.csv](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_shadow_decision_log_template_2026-06-23.csv)
- updated:
  - [pure_fundamental_manual_style_switch_guide_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_manual_style_switch_guide_2026-06-23.md)
  - [pure_fundamental_two_branch_summary_2026-06-23.md](D:/hh/codex/v4/phase_1_fundamental/pure_fundamental_two_branch_summary_2026-06-23.md)

What changed:

- we intentionally did **not** promote `core_level` into a formal live switching framework
- instead:
  - live branch stays on `balanced`
  - `core_level` is tracked as a shadow branch

Why:

- `core_level` is a valid structural side candidate
- but we still do not have proof that ex-ante human branch selection is stable enough
- moving too early to live switching would mix research judgment with execution history

Shadow process now frozen:

1. before each annual window, record whether you would stay with `balanced` or prefer `core_level`
2. keep live history on `balanced`
3. record the shadow branch result after the year closes
4. after several years, evaluate whether the ex-ante calls had real discrimination power

Practical conclusion:

- this preserves optionality without contaminating the main live line
- the question changes from:
  - "should we switch now?"
- to:
  - "can future ex-ante decisions prove they add stable value?"

## Combined Interpretation

These three steps all move in the same direction:

- less parameter twitching
- more execution discipline
- more separation between live line, research line, and discretionary hypothesis

Current working posture after this round:

- defensive overlay:
  - `shortbond_6040_4055` remains the live leading candidate
- execution research:
  - prioritize local-vs-JoinQuant reconciliation before more optimization
- pure fundamental branch management:
  - live = `balanced`
  - `core_level` = shadow tracking only

## Recommended Next Steps

1. add a temporary JoinQuant debug export that matches `execution_faithful_validation_v1`
2. find the first local-vs-JoinQuant mismatch layer
3. only after that, decide whether the fix belongs in:
   - local panel construction
   - factor timing
   - score standardization
   - JoinQuant execution logic
   - or return mapping
