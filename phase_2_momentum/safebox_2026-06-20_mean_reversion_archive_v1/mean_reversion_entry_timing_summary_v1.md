# Mean Reversion Entry Timing Summary V1

This document freezes the current conclusion of the mean-reversion entry-timing branch.

## What Was Tested

Three entry styles were compared while keeping the annual approved basket unchanged:

1. `immediate_entry`
- buy the full approved basket immediately

2. `timed_entry_rev5_abnvol`
- delay the full basket entry
- choose the best weekly point inside a short post-rebalance window using pool-average `rev5_abnvol`

3. `staggered_entry_50_50`
- buy `50%` immediately
- buy the remaining `50%` at the best weekly point inside the same short window

## Frozen Results

Full-delay timing:
- total return proxy = `0.38906`
- max drawdown proxy = `-0.080203`
- median 12-week case return = `0.056582`

Immediate entry:
- total return proxy = `0.321575`
- max drawdown proxy = `-0.083261`
- median 12-week case return = `0.027169`

Staggered 50/50 entry:
- total return proxy = `0.35911`
- max drawdown proxy = `-0.077621`
- median 12-week case return = `0.041876`

## Current Interpretation

The current safest interpretation is:

- if the objective is return-first, the best current candidate is `timed_entry_rev5_abnvol`
- if the objective is a more practical balance between return and stability, the best current candidate is `staggered_entry_50_50`

This means the mean-reversion signal currently looks more useful for:
- improving annual-basket entry timing

than for:
- weekly replacement of approved holdings

## Promotion Status

Current status:
- full replacement overlay: `not approved`
- entry timing use case: `promising`
- practical conservative candidate: `staggered_entry_50_50`
- aggressive candidate: `timed_entry_rev5_abnvol`

## Caution

The current entry-timing advantage is not a clean every-case dominance:
- the benefit seems to come more from avoiding some poor entry windows than from steady small wins in every rebalance

So the correct interpretation is:
- useful tactical timing evidence
- not yet a fully locked deployment rule

## Next Practical Choice

If a next implementation is needed, the decision rule is:

- choose `timed_entry_rev5_abnvol` when maximizing upside is the first priority
- choose `staggered_entry_50_50` when implementation realism and downside control matter more
