# Allocation Vs Selection Framework Note V1

## Purpose

This note separates two questions that should not be mixed in the final interpretation:

1. which structure is stronger as a `portfolio allocation` framework
2. which structure is stronger as a `stock selection` framework

The current project evidence suggests that these two questions now have different leading answers.

## Question 1: Allocation Framework

Here the relevant comparison is:

- should fundamentals and momentum be managed as separate sleeves
- with explicit portfolio-level budget control
- and only combined at the final capital-allocation layer

Current strongest answer:

- `fixed_60_40`

Interpretation:

- fundamentals and momentum remain logically independent
- neither side directly rewrites the other side's raw signal
- the interaction happens only through final capital allocation

Why this line still matters:

- it is the cleanest current dual-engine construction
- it proved stable inside the local weight neighborhood
- it remains the strongest current allocation-layer baseline
- later state-routing and threshold-conditioning variants did not produce a sufficiently strong and stable upgrade over this baseline

So on the allocation question, the current answer is:

- `separate sleeves plus explicit budget control` remains the best supported structure

## Question 2: Selection Framework

Here the relevant comparison is:

- should fundamentals define admissibility first
- and momentum then decide which names to actually hold

Current strongest answer on the common rolling sample:

- `mom12_top10_then_fundamental_top6`

Interpretation:

- fundamentals define the candidate pool
- momentum selects the final winners inside that pool
- this is not a dual-engine budget-allocation line
- this is a layered stock-selection line

Why it led on rolling:

- on the current common monthly pre-2021 rolling sample
- it beat both:
  - `fixed_60_40`
  - `annual_entry_monthly_exit_slow_fundamental`

But the frozen post-2021 acceptance result did not confirm promotion over the simpler pure momentum line:

- `direct_mom12_top6`
  - strategy return = `40.09%`
  - excess return = `16.88%`
- `mom12_top10_then_fundamental_top6`
  - strategy return = `27.18%`
  - excess return = `6.10%`

So on the selection question, the safest current answer is:

- momentum-first plus fundamental refinement is a validated research structure
- but it is not the active executable momentum winner after frozen acceptance

## Why These Two Answers Can Coexist

There is no contradiction.

These two structures solve different problems:

- `fixed_60_40` answers:
  how should we combine two validated signal families at the portfolio-construction level

- `mom12_top10_then_fundamental_top6` answers:
  how should we choose names if momentum leads and fundamentals only refine quality inside the fast selector

So the current project-level reading should be:

- best allocation framework = `fixed_60_40`
- strongest rolling stock-selection research candidate = `mom12_top10_then_fundamental_top6`
- active executable momentum winner = `direct_mom12_top6`

## Practical Reporting Rule

To avoid confusion in the final report, these statements should stay separated:

- do not say `fixed_60_40` is the strongest overall candidate without qualification
- do not say the rolling stock-selection leader automatically beats the frozen executable momentum line

The cleaner wording is:

- `fixed_60_40` is the strongest current allocation-layer baseline
- `mom12_top10_then_fundamental_top6` is the strongest current rolling stock-selection research candidate
- `direct_mom12_top6` remains the active executable momentum main line after frozen acceptance

## Current Non-Promoted Branches

The following ideas currently remain weaker than the simpler leaders above:

- annual-entry monthly-exit slow-fundamental state machine
- deterioration-only weak-down entry
- two-stage deterioration warning plus price confirmation as a promoted entry rule
- fundamental-conditioned momentum release thresholds

Their common pattern is:

- good economic intuition
- but not enough rolling evidence to displace the simpler leading lines

## Final Takeaway

If we compress the current project status into one clean hierarchy:

1. allocation-layer leader:
   `fixed_60_40`

2. executable momentum leader:
   `direct_mom12_top6`

3. archived rolling-positive selection candidate:
   `mom12_top10_then_fundamental_top6`

4. archived structural alternative:
   `annual_entry_monthly_exit_slow_fundamental`

That is the safest current interpretation of the evidence.

## References

- [formal_candidate_rolling_comparison_v1.md](D:\hh\codex\v4\phase_2_momentum\formal_candidate_rolling_comparison_v1.md)
- [formal_candidate_report_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\formal_candidate_report_draft_v1.md)
- [phase2_success_summary_2026-06-19.md](D:\hh\codex\v4\phase_2_momentum\phase2_success_summary_2026-06-19.md)
