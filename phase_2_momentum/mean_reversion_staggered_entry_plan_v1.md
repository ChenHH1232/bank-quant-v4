# Mean Reversion Staggered Entry Plan V1

This note defines the first practical follow-up after the full-delay entry timing test.

## Why A Staggered Version

The full-delay timing test showed:
- delayed entry can improve the 12-week proxy outcome in aggregate
- but the win rate is not high enough to justify an all-or-nothing delay rule

That suggests the signal may be useful for:
- reducing bad immediate entry timing

but not necessarily for:
- fully replacing the original entry decision

So the next practical version should be:
- partial entry now
- partial entry later if mean reversion becomes more favorable

## V1 Staggered Structure

Baseline:
- buy `100%` of the approved annual basket immediately

Full-delay comparison:
- buy `100%` at the best entry week inside the short search window

New staggered comparison:
- buy `50%` immediately
- buy the remaining `50%` at the best weekly point inside the same search window

## Why 50/50 First

This is the simplest practical split because:
- it keeps implementation easy
- it still expresses conviction that bad initial timing can matter
- it reduces the risk of missing upside if the basket keeps rising immediately

## Frozen V1 Assumptions

- same annual approved basket
- same search window as entry timing V1
- same `rev5_abnvol` pool-average signal
- same holding horizon after each leg

## Success Standard

The staggered version is promising if it:
- keeps or improves the delayed-entry return advantage
- while reducing the downside of being wrong about waiting
- and improves stability versus the full-delay version
