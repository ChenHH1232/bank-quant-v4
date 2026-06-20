# Mean Reversion Entry Timing Plan V1

This note defines the first minimal validation plan for using mean reversion as entry timing rather than as a full holding-replacement overlay.

## Why This Path

Current evidence already says:
- standalone mean reversion has tactical value
- weekly execution is better than daily
- but full weekly replacement inside the annual approved pool did not improve the mainline baseline

So the cleaner next question is no longer:
- should mean reversion replace approved holdings every week

The cleaner next question becomes:
- can mean reversion help us choose a better entry week for the same approved holdings

## Minimal Validation Principle

The first entry-timing test should be intentionally conservative:

- do not change the approved annual holding list
- do not change the annual factor plan
- do not change holding weights
- only change the entry timing rule immediately after an annual rebalance date

This keeps the test focused on one narrow question:
- does `rev5_abnvol` help us avoid poor immediate entry timing

## V1 Test Design

Upper pool:
- use the real annual `primary` approved holding list from [joinquant_v4_annual_attribution_v1.csv](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_attribution_v1.csv)

Baseline:
- on each annual rebalance date, buy the full approved pool immediately at that week

Timing variant:
- after each annual rebalance date, allow a short observation window
- inside that window, choose the first weekly point where the approved pool has the best mean-reversion entry condition
- then buy the same approved pool, still equal weight

## First Frozen Entry Proxy

The first timing proxy should stay simple:

- signal: average `rev5_abnvol` across the approved pool
- interpretation: lower is better for entry
- search window: the rebalance week plus the next `3` weekly checkpoints
- selected entry date: the lowest pool-average `rev5_abnvol` within that short window

Why this proxy:
- it respects the current evidence that the signal works as a short-horizon repair measure
- it avoids designing name-level partial entry rules too early
- it tests whether mean reversion helps entry timing for the whole approved basket

## What This Test Does Not Do

This is not:
- weekly replacement of holdings
- dynamic position sizing
- regime switching
- adding or removing stocks from the approved list

It is only:
- delayed entry timing for the same annual basket

## Success Standard

The timing version is useful only if it improves at least one of:

- full-window total return
- drawdown during the early post-rebalance phase
- average short-window entry outcome after annual rebalance dates

If it fails these tests:
- then current mean reversion evidence is more tactical and cross-sectional than basket-level entry useful

## Next Step

Build a minimal local comparison:

1. immediate annual entry
2. short-window delayed entry using pool-average `rev5_abnvol`

Only after that should we consider:
- staggered entry
- partial entry
- regime-gated entry timing
