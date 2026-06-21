# Defensive Bond Switch Draft V1

Positioning:
- this draft extends the dual-engine bank framework with a defensive asset sleeve
- the purpose is to answer whether weak-state momentum budget should leave the bank universe instead of flowing back into bank fundamentals
- this is a research draft, not a promoted deployment rule

## Core Hypothesis

The hypothesis is:

- in weak bank-trend states, reallocating the momentum budget back into bank fundamentals may be too narrow
- because the real problem may not be `which bank to hold`
- the real problem may be `whether bank equity should keep full portfolio share at all`

So the weak-state fallback should test:

- defensive asset substitution

instead of only:

- internal bank reallocation

## First-Pass Design

Keep the existing bank framework intact:

- fundamental engine stays unchanged
- momentum engine stays unchanged
- state only changes the destination of the momentum sleeve

This means:

- no mixed score
- no rewrite of the bank factor stack
- no forced full exit from the bank universe in the first pass

## Three-State Allocation Mapping

The first-pass allocation draft is:

- `strong_up` => `60%` bank fundamental + `40%` bank momentum
- `neutral_flat` => `80%` bank fundamental + `20%` bank momentum
- `weak_down` => `60%` bank fundamental + `40%` defensive bond ETF

Interpretation:

- `strong_up`: fully allow the momentum sleeve to work
- `neutral_flat`: keep some momentum, but reduce it
- `weak_down`: preserve the fundamental bank core, but move the tactical sleeve out of bank equity

## Why Not Full Exit First

The first pass should not jump immediately to:

- `weak_down` => `100%` bond ETF

Reason:

- that would turn the framework into a much more aggressive asset-allocation regime
- it would be harder to interpret whether any improvement comes from better bank timing or simply from leaving the asset class entirely

So the cleaner first test is:

- keep the structural bank allocation
- only redirect the tactical sleeve

## Defensive Asset Candidate

The first candidate defensive asset should be a liquid government-bond ETF that is easy to execute in JoinQuant.

Preferred first-pass candidate:

- `511010.XSHG`

Reason:

- clean interpretation
- practical tradability
- consistent with the goal of using a low-risk parking sleeve rather than introducing a second risky style

## State Definition Constraint

The same discipline still applies:

- state must be defined only from decision-time observable information
- no future-defined dispersion terms
- no post-period realized labels inside the deployed rule

So this branch should inherit the same state-research discipline as the state-gated momentum branch.

## Evaluation Question

The main question is:

- in weak states, is `bond substitution` better than `momentum shutdown with bank-only fallback`

That means the first comparison set should include:

- fixed `60/40` dual engine
- state-gated bank-only dual engine
- state-gated bond-switch dual engine
- pure fundamental

## Expected Interpretation

If bond-switch wins, the implication is:

- weak-state problems are not just about overusing bank momentum
- they are about keeping too much capital inside bank equity during bad regimes

If bond-switch does not win, the implication is:

- the issue is still mostly inside bank-stock cross-sectional allocation
- or the current state proxy is still too weak to time the switch correctly

## Practical Next Step

The next concrete task should be:

- define a `pre-2021 rolling` validation version of the bond-switch rule

The first-pass test should keep everything else fixed and only replace:

- weak-state `0%` momentum

with:

- weak-state `40%` defensive bond ETF

## References

- [momentum_on_off_rule_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_on_off_rule_draft_v1.md)
- [state_gated_dual_engine_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\state_gated_dual_engine_validation_note_v1.md)
- [fundamental_momentum_dual_engine_rolling_test_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_test_v1.md)
