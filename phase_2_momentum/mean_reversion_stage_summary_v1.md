# Mean Reversion Stage Summary V1

This document freezes the current stage conclusion for the bank mean-reversion branch after the first full cycle of field check, factor construction, signal validation, execution comparison, and annual-pool overlay testing.

## What Was Confirmed

Data readiness:
- no new download was required for the first-pass mean-reversion branch
- the existing momentum daily panel already contained enough base fields
- the missing research fields could be derived locally

Signal findings:
- the first confirmed mean-reversion signal is `rev_5d`
- its valid direction is `smaller_better`
- this means recent short-term losers have rebound tendency in the bank universe

Composite findings:
- the strongest current composite is `rev5_abnvol = -0.7 * rev_5d + 0.3 * abnormal_volume_ratio`
- anchored validation showed a small but consistent improvement versus raw `rev_5d`

Execution findings:
- standalone tactical mean reversion works better with `weekly` execution than with `daily` execution
- therefore the current safe execution preference is `weekly`

Entry-timing findings:
- mean reversion looks more useful as annual-basket entry timing than as weekly full holding replacement
- `timed_entry_rev5_abnvol` is the strongest current return-first candidate
- `staggered_entry_50_50` is the best current practical balance candidate because it gives up some upside but improves drawdown versus both immediate entry and full-delay aggressiveness

## What Was Not Confirmed

These ideas do not yet have promotion evidence:

- `rev_10d` and `rev_20d` as robust primary reversion signals
- daily execution as the default execution rhythm
- weekly `rev5_abnvol` overlay as a default execution override on top of the annual approved pool
- a fully locked universal entry-delay rule that dominates in every case

In the frozen post-2021 acceptance window:
- annual approved-pool baseline total return = `0.584687`
- annual approved-pool plus weekly reversion overlay total return = `0.568945`
- overlay drawdown was also slightly worse

So the current overlay version did not improve the annual backbone.

## Frozen Interpretation

The current safest interpretation is:

- mean reversion is a real short-horizon tactical signal in bank stocks
- but it is not yet proven as a default override layer for the annual backbone
- therefore it should remain a tactical branch rather than being promoted into the main deployment stack
- its most promising current use is entry timing, not full weekly basket replacement

## Recommended Status

Current status labels:
- research signal validity: `confirmed`
- preferred execution rhythm: `weekly`
- standalone tactical branch: `keep alive`
- annual-pool overlay promotion: `not approved`
- entry-timing branch: `promising`

## Valid Next Steps

If this branch is continued later, the most valid next directions are:

1. prioritize entry-timing style use cases over full weekly replacement
2. test conditional activation by regime instead of all-week always-on overlay
3. test overlay on a momentum-approved subset instead of the annual approved pool directly
4. if implementation is needed, compare `full-delay` versus `50/50 staggered` as the first practical deployment choice

## What To Avoid

- do not retune `rev5_abnvol` on the same post-2021 acceptance window because the first overlay version underperformed
- do not reinterpret the current evidence as proof that mean reversion should become a third annual main line
- do not mix mean reversion conclusions into momentum conclusions
