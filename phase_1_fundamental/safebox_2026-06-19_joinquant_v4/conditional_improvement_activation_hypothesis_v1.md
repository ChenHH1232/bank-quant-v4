# Conditional Improvement Activation Hypothesis V1

## Hypothesis

- The improvement-factor layer may add value only in some annual regimes rather than in every year.
- A future strategy may therefore choose between:
  - `primary`
  - `benchmark`
  based on training-period evidence available at the decision date.

## What We Can Use As Evidence

- Training-period annual review metrics
- Training-period factor spread or IC diagnostics
- Training-period comparison between the permanent core and the core-plus-improvement version

## What We Must Not Use

- We must not use realized out-of-sample backtest performance from 2021-2025 to define the switching rule after the fact.
- We must not hard-code a rule like "use benchmark in 2023-2024 because it won there" because that is sample leakage.

## Valid Next-Step Protocol

1. Define a simple switching rule using training-period inputs only.
2. Freeze that rule before looking at the corresponding out-of-sample year.
3. Re-run a rolling framework that decides `primary` vs `benchmark` at each annual boundary.
4. Evaluate the resulting walk-forward strategy as a new hypothesis test.

## Practical Standard For V1

- Keep the first conditional rule simple.
- Prefer one or two training-based conditions over a complex score.
- If the signal is weak or ambiguous, default to the simpler `benchmark` line.

## Status

- This is a research hypothesis, not a validated production conclusion.
