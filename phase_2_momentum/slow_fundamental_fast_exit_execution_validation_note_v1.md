# Slow Fundamental Fast Exit Execution Validation Note V1

Conclusion:
- the `slow fundamental, fast exit` execution constraint improves the current annual-entry monthly-exit candidate
- but it still does not beat the fixed `60/40` baseline
- so the rule is useful as an execution refinement, not yet as a promoted replacement

## What Was Compared

Baseline:
- fixed `60/40`

Active candidate:
- annual breadth entry + monthly `mom6_positive_ratio_q50` exit

Execution refinement:
- same active candidate signal rules
- but fundamental sleeve may rebuild only on quarterly fundamental refresh dates
- on non-quarter dates it may only sell down, not buy new fundamental positions

## Result

Current ranking:

1. fixed `60/40` cum return = `0.007940`
2. annual entry monthly exit `slow fundamental` = `0.007116`
3. annual entry monthly exit `unconstrained` = `0.006799`

So the execution constraint added value:

- constrained version improved over unconstrained version by `0.000317`

## Interpretation

This means:

- the cleaner slow-layer versus fast-layer execution boundary is directionally helpful
- the rule did not cripple the strategy
- instead, it improved the current candidate modestly

That supports the economic interpretation:

- fundamentals should remain a slower capital-allocation sleeve
- monthly repair should reactivate tactical risk, not rebuild the whole base book

## Remaining Gap

Even after the refinement:

- fixed `60/40` still remains better

So the active candidate still has not crossed the final hurdle.

This means the current bottleneck is now narrower:

- the two-layer state machine is usable
- the slow-fundamental execution discipline is mildly helpful
- but the release process still does not restore enough effective exposure to match the fixed baseline

## Current Decision

Current decision should be:

1. keep fixed `60/40` as the active baseline
2. keep annual entry + monthly exit as the active upgrade candidate
3. keep `slow fundamental, fast exit` as the preferred execution interpretation of that candidate

## References

- [slow_fundamental_fast_exit_execution_rule_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_rule_draft_v1.md)
- [slow_fundamental_fast_exit_execution_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_validation_v1.md)
- [annual_entry_monthly_exit_vs_fixed6040_note_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_vs_fixed6040_note_v1.md)
