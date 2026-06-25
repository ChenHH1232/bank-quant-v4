# V4 Methodology Correction Memo 2026-06-23

## Purpose

This memo records the main methodology corrections after reviewing the current `v4` pure-fundamental progress.

The goal is not to overturn the existing research conclusion.
The goal is to tighten the language, reduce over-claiming, and redirect the next stage from rule-search toward execution-faithful validation.

## What Stays Valid

The following conclusions remain valid:

- `balanced = base_core_6 + top_08` can be frozen as the default pure-fundamental main line
- `core_level = base_core_6 - indicator__eps + bank_indicator__core_level_capital_adequacy_ratio` remains an accepted structural side candidate
- persistent heavy quality overweight is rejected as an execution rule
- monthly relative-momentum-based style timing is rejected as a production path
- `shortbond_6040_4055` remains the strongest current defensive overlay candidate

These conclusions do not need to be reopened immediately.

## Main Correction

The main correction is about **how we describe and prioritize the next step**.

The current project should not be described as if it has already solved style switching.

More precise wording:

- `balanced` = formal default execution line
- `core_level` = accepted structural variant
- `manual switch` = future research mechanism, not yet a confirmed execution framework

Reason:

- we have shown that `core_level` can be stronger in some regimes
- we have **not** yet shown that a human can reliably identify that regime in advance

This distinction matters.

## Most Important Open Risk

The largest open methodology risk is:

- local rolling validation and JoinQuant execution are not yet fully execution-faithful to the same decision kernel

This is more important than finding one more factor, one more threshold, or one more switching rule.

Observed pattern:

- some rolling improvements survived
- many dynamic or timing-style improvements did not survive JoinQuant

Interpretation:

- the local approximation likely overstates the value of dynamic rules
- especially when the rule changes ranking, bucket membership, holdings, and turnover in a nonlinear way

Therefore:

- no further dynamic switching research should be prioritized until this execution gap is explicitly addressed

## Product-Line Clarification

The current `v4` structure should be treated as three separate lines:

### 1. Pure Fundamental Balanced

- formal core product line
- `base_core_6 + top_08`
- default benchmark for all future comparison

### 2. Pure Fundamental Core-Level Variant

- research product line
- accepted structural alternative
- should not yet be marketed internally as a mature manual style-switch strategy

Recommended wording:

- “accepted structural variant”
- not “confirmed manual switch strategy”

### 3. Balanced + Shortbond Defensive Overlay

- separate risk-management product line
- should be evaluated as overlay / allocation logic
- should not be mixed back into stock-selection rule search

## What To Stop Doing Now

The following should be deprioritized or stopped for the current phase:

- adding more pure-fundamental factors
- continuing new monthly switching rules
- testing more profitability/quality tilt ladders
- inventing macro narratives backward from known yearly results
- expanding search space for small incremental rolling improvements

Reason:

- the search space is already large
- many remaining “improvements” are likely pseudo-improvements
- current marginal research value is lower than the unresolved execution-validation gap

## What To Continue Next

Priority should shift to:

### 1. Execution-Faithful Validation

Build a narrow follow-up stage focused on:

- point-in-time factor visibility
- exact stock universe consistency
- ranking and top-N consistency
- rebalance-date consistency
- turnover and transaction-cost consistency
- local-versus-JoinQuant reconciliation on representative rebalance dates

This is infrastructure work, not strategy expansion.

### 2. Shortbond Overlay Stability Check

Do a minimal neighborhood stability test around the current best shortbond candidate.

Goal:

- test whether the result comes from a stable parameter region
- not to continue large-scale parameter mining

### 3. Core-Level Exposure Decomposition

Analyze whether `core_level` really captures capital-quality preference, or whether it is mostly a proxy for:

- large-cap exposure
- low-volatility exposure
- state-owned large-bank bias

This should be treated as explanation work, not immediate optimization work.

## Reporting Language Correction

When writing summaries or handoff notes, use the following language:

Correct:

- “balanced is the current robust default line”
- “core_level is an accepted structural variant”
- “manual switching remains a future discretionary workflow to be validated”
- “monthly timing did not survive execution confirmation”

Avoid:

- “we already have a reliable manual switch strategy”
- “monthly timing only needs more tuning”
- “rolling-positive means production-ready”

## Decision

For the current `phase_1_fundamental` close-out:

- freeze the pure-fundamental main line
- archive rejected dynamic branches clearly
- keep `core_level` as a monitored structural variant
- elevate execution-faithful validation into the next methodology priority
- keep shortbond overlay as a separate follow-up line

## Practical Bottom Line

The current state of `v4` is:

- strategy-level conclusions are already strong enough to freeze
- methodology-level infrastructure is not yet strong enough to justify more dynamic rule search

So the next gain should come from:

- improving validation fidelity

not from:

- inventing more switching logic
