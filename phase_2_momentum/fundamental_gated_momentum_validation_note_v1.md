# Fundamental Gated Momentum Validation Note V1

Conclusion:
- the first-pass `fundamental gate + momentum rank` test did not yet show incremental value over direct momentum
- but the main reason is not that the idea failed
- the main reason is that the current monthly tradable pool is already too small, so the fundamental gate did not become binding

## Result

Current ranking:

- `direct_mom12_top6` cum return = `0.010592`
- `gated_top16_mom12_top6` cum return = `0.010592`
- `gated_top20_mom12_top6` cum return = `0.010592`
- `fundamental_top16_equal` cum return = `0.007548`
- `fundamental_top20_equal` cum return = `0.007548`

## Why The Gated Variants Matched Direct Momentum

The current monthly statistics explain it clearly:

- mean candidate count = `13.65`
- average hold count for the momentum strategies = `6`

So in this first-pass setup:

- the monthly direct momentum universe was already only about `13` to `14` names on average
- that means a `Top 16` or `Top 20` fundamental gate almost never removes anything
- therefore `gated_top16_mom12_top6` and `gated_top20_mom12_top6` collapse into the same effective portfolio as direct momentum

## What Has Actually Been Learned

This test still gives one useful conclusion:

- inside the current narrow monthly tradable pool, `mom_12_1` top-6 ranking is stronger than equal-weight fundamental holding

But it does **not** yet answer the real structural question:

- whether fundamental admission improves momentum selection when the candidate set is genuinely wider

## Current Judgment

The idea should not be rejected yet.

Instead, the correct interpretation is:

- the present rolling test is underpowered for the gating question
- because the candidate pool is already pre-shrunk before the gate is applied

## Practical Next Step

If this branch is continued later, the next valid test should change only one thing:

- widen the pre-gate monthly candidate universe

Then re-test:

- direct momentum on the wider universe
- fundamental top-16 or top-20 gate, then momentum top-6

Only under that setup can we judge whether the fundamental gate adds value.

## References

- [fundamental_gated_momentum_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_gated_momentum_rolling_validation_v1.md)
- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
