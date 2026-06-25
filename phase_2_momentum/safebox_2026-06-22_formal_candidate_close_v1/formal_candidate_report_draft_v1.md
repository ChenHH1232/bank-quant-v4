# Formal Candidate Report Draft V1

## Objective

This note freezes the current report-level comparison among the three active `Phase 2` formal candidates under one explicit interpretation framework.

The goal is not to reopen branch search.

The goal is to state, in report-ready language:

- which line currently leads on common pre-2021 rolling evidence
- which line is the strongest allocation/risk-balancing alternative
- which line should remain archived as a structural backup instead of being promoted

## Compared Candidates

The current formal-candidate set is:

1. `fixed_60_40`
2. `annual_entry_monthly_exit_slow_fundamental`
3. `quarterly_top20_mom12_top6`

Their economic meanings are different:

- `fixed_60_40`:
  a fixed dual-engine allocation line
  fundamental and momentum stay logically separate
  interaction happens only at the final portfolio-allocation layer

- `annual_entry_monthly_exit_slow_fundamental`:
  a state-switch line
  annual observable weak-state entry logic is retained
  monthly release logic is added so recovery from weak states is faster

- `quarterly_top20_mom12_top6`:
  a layered stock-selection line
  fundamentals define admissibility
  momentum decides the final monthly winners inside that admissible pool

## Common-Sample Rolling Result

The current report-level candidate close uses the common monthly rolling sample documented in [formal_candidate_rolling_comparison_v1.md](D:\hh\codex\v4\phase_2_momentum\formal_candidate_rolling_comparison_v1.md).

Protocol:

- research scope = pre-2021 rolling validation only
- folds = `2`
- common monthly snapshots = `26`
- all three candidates are compared on the same fold structure and same monthly sample

Current ranking:

1. `quarterly_top20_mom12_top6`
   cumulative return = `0.010141`
   mean monthly return = `0.000393`
   mean invested weight = `1.000000`
   mean cash weight = `0.000000`

2. `fixed_60_40`
   cumulative return = `0.007940`
   mean monthly return = `0.000307`
   mean invested weight = `0.915145`
   mean cash weight = `0.084855`

3. `annual_entry_monthly_exit_slow_fundamental`
   cumulative return = `0.007116`
   mean monthly return = `0.000275`
   mean invested weight = `0.747738`
   mean cash weight = `0.252262`

Increment versus `fixed_60_40`:

- `quarterly_top20_mom12_top6` delta = `0.002201`
- `annual_entry_monthly_exit_slow_fundamental` delta = `-0.000824`

## Interpretation

### 1. Current return leader

On the current common monthly pre-2021 rolling sample, the strongest formal candidate is:

- `quarterly_top20_mom12_top6`

That means the best current report-level return-seeking line is:

- quarterly fundamental gate
- then monthly `mom_12_1` top-6 ranking

This is now stronger than both:

- the fixed dual-engine allocation baseline
- the annual-entry monthly-exit state-switch candidate

### 2. Strongest allocation-layer candidate

Even though it does not lead this final horse race, `fixed_60_40` still keeps a distinct role:

- it is the strongest current allocation-layer candidate
- it offers a cleaner coexistence of fundamentals and momentum without forcing a mixed score
- it keeps better balance between return and capital-preservation discipline than the slower state-switch route

So `fixed_60_40` should still be described as:

- the best current dual-engine allocation baseline

not as:

- the strongest overall formal candidate

### 3. Status of the state-switch line

`annual_entry_monthly_exit_slow_fundamental` remains economically coherent and still matters as a research result.

What it has proven is:

- annual weak-state recognition is directionally useful
- monthly release from weak states improves the annual-only route
- slow fundamental refresh plus fast exit is the preferred implementation reading inside that family

But under the current final common-sample close, it does not win the formal-candidate race.

So its report-level role should be:

- archive as the main lower-risk structural alternative

not:

- promote as the primary candidate

## Required Caveat

The current ranking should be reported with one explicit caution:

- `quarterly_top20_mom12_top6` is effectively fully invested
- `fixed_60_40` intentionally preserves residual cash under cap discipline
- `annual_entry_monthly_exit_slow_fundamental` preserves even more cash on average

So the current ordering is valid for:

- project-level candidate ranking
- current branch-priority decisions

But it is not a pure like-for-like statement about signal quality alone.

Part of the gap comes from:

- different capital deployment intensity

This caveat should stay visible in any final externalized report.

## Execution Interpretation

The most important execution note currently belongs to `fixed_60_40`.

From [dual_engine_execution_stress_test_v1.md](D:\hh\codex\v4\phase_2_momentum\dual_engine_execution_stress_test_v1.md):

- cost inflation from `10 bps` to `30 bps` does not break the line
- short timing slippage matters more than moderate cost inflation

The correct reading is:

- the dual-engine baseline is not mainly cost-fragile
- it is more sensitive to execution timing
- this should be interpreted as execution-layer sensitivity, not as rapid basic-factor decay

That distinction matters because:

- a few trading days do not materially stale bank fundamentals
- but they can materially change price path capture for the momentum and allocation layer

## Promotion Decision

Current project-level promotion decision should be:

1. primary formal candidate:
   `quarterly_top20_mom12_top6`

2. primary allocation-layer baseline:
   `fixed_60_40`

3. archived lower-risk structural alternative:
   `annual_entry_monthly_exit_slow_fundamental`

## Suggested Report Wording

If we want one concise conclusion sentence for the final report, the cleanest current wording is:

`On the current pre-2021 common monthly rolling validation, the strongest formal candidate is the quarterly fundamental gate plus monthly momentum ranking line, while fixed 60/40 remains the strongest dual-engine allocation baseline and the annual-entry monthly-exit state-switch line remains an economically coherent but weaker structural alternative.`

## References

- [formal_candidate_rolling_comparison_v1.md](D:\hh\codex\v4\phase_2_momentum\formal_candidate_rolling_comparison_v1.md)
- [quarterly_fundamental_monthly_momentum_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\quarterly_fundamental_monthly_momentum_validation_note_v1.md)
- [slow_fundamental_fast_exit_execution_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_validation_note_v1.md)
- [dual_engine_execution_stress_test_v1.md](D:\hh\codex\v4\phase_2_momentum\dual_engine_execution_stress_test_v1.md)
