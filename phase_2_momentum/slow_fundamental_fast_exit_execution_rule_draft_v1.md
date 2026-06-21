# Slow Fundamental Fast Exit Execution Rule Draft V1

Objective:
- define a cleaner execution-permission boundary for the active two-layer state-machine branch
- keep fundamentals as a slow layer
- keep the monthly exit logic from turning the fundamental sleeve into a pseudo-high-frequency strategy

## Core Principle

The portfolio should distinguish:

- `slow fundamental capital`
- `fast release / repair adjustment`

Meaning:

- fundamental allocation is allowed to rebuild only on fundamental rebalance dates
- monthly state repair may change exposure, but should not freely reconstruct the fundamental sleeve between those dates

## Fundamental Sleeve Trading Permission

On fundamental rebalance dates:
- fundamental sleeve may buy
- fundamental sleeve may sell
- fundamental sleeve may rotate into the refreshed approved pool

On non-fundamental rebalance dates:
- fundamental sleeve may sell
- fundamental sleeve may reduce exposure
- fundamental sleeve may not open new fundamental positions
- fundamental sleeve may not add to a fundamental position that is currently absent from the held base book

## Why This Rule Exists

Without this boundary, the monthly repair layer can accidentally do too much:

- it can turn a slow fundamental sleeve into a faster sleeve
- it can blur the difference between `signal update frequency` and `execution frequency`
- it can make the strategy look better in research while losing its original economic meaning

So this rule protects the structure:

- fundamentals remain low-frequency capital allocation
- monthly exit remains a release mechanism, not a full portfolio rebuild

## Monthly Exit Layer Permission

The monthly exit layer may:

- reduce defensive stance
- restore risk budget
- reactivate the momentum sleeve

The monthly exit layer may not:

- fully refresh the fundamental sleeve outside its own rebalance schedule

## Preferred Capital Routing After Exit

When a `weak_down -> neutral_flat` release is triggered on a non-fundamental rebalance date:

- the restored risk budget should first go to the momentum sleeve
- not to newly rebuilt fundamental positions

This is the preferred first-pass interpretation because:

- momentum is already the fast layer
- it is the natural place to absorb restored tactical risk budget
- this keeps the role split clean

## Two Practical Execution Variants

Variant A:
- non-fundamental dates: fundamental sleeve can only sell
- released capital that is not assigned to momentum stays in cash

Variant B:
- non-fundamental dates: fundamental sleeve can only sell
- released capital may be reassigned to the momentum sleeve

Current preference:
- `Variant B`

Reason:
- it matches the active two-layer state-machine logic better
- annual or quarterly fundamentals still define the slow base book
- monthly repair restores only the tactical sleeve

## Current Research Use

This rule should be treated as:

- an execution-constraint refinement
- not a new alpha signal

So it should be tested only after:

- annual entry rule is fixed
- monthly exit signal is fixed
- budget mapping is fixed

## What This Rule Is Trying To Solve

The current active candidate still trails fixed `60/40`.

One plausible reason is:

- even when the state machine is directionally right, the execution permissions are too loose or too conceptually blurred

This rule tests whether a cleaner separation between:

- slow base capital
- fast repair capital

can improve interpretability and potentially improve real execution quality.

## References

- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
- [annual_entry_monthly_exit_stability_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_stability_validation_v1.md)
