# Mean Reversion Stage Summary V1

This document freezes the current stage conclusion for the bank mean-reversion branch after the first full cycle of field check, factor construction, signal validation, execution comparison, annual-pool overlay testing, and JoinQuant out-of-sample deployment comparison.

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
- mean reversion looked more useful as annual-basket entry timing than as weekly full holding replacement in local research
- `timed_entry_rev5_abnvol` was the strongest local return-first candidate
- `staggered_entry_50_50` was the best local practical balance candidate because it gave up some upside but improved drawdown versus both immediate entry and full-delay aggressiveness
- however, that local advantage did not survive the final JoinQuant out-of-sample comparison against direct annual entry

Take-profit findings:
- the first minimal `overheat_score_v1` trim test showed only weak positive evidence
- partial trimming reduced drawdown somewhat, but also reduced total return noticeably
- the current safe interpretation is: mean reversion is more useful on the buy side than on the sell side

## What Was Not Confirmed

These ideas do not have promotion evidence:

- `rev_10d` and `rev_20d` as robust primary reversion signals
- daily execution as the default execution rhythm
- weekly `rev5_abnvol` overlay as a default execution override on top of the annual approved pool
- a fully locked universal entry-delay rule that dominates direct annual entry in real out-of-sample deployment
- a strong enough sell-side overheat rule to justify default promotion as a stop-profit layer

In the frozen post-2021 acceptance window:
- annual approved-pool baseline total return = `0.584687`
- annual approved-pool plus weekly reversion overlay total return = `0.568945`
- overlay drawdown was also slightly worse

So the current overlay version did not improve the annual backbone.

In the final JoinQuant out-of-sample comparison:
- annual-pool mean-reversion entry strategy return = `37.13%`
- annual-pool direct-entry strategy return = `44.51%`
- drawdown difference was only marginal

So the current entry-timing version also did not improve the annual backbone.

## Frozen Interpretation

The current safest interpretation is:

- mean reversion is a real short-horizon tactical signal in bank stocks
- but it is not proven as a deployable strategy layer in the frozen post-2021 acceptance window
- therefore it should remain an archived tactical research branch rather than being promoted into the main deployment stack
- entry timing was the most promising local use, but it still failed final deployment confirmation
- within the current evidence set, buy-side use is stronger than sell-side use

## Recommended Status

Current status labels:
- research signal validity: `confirmed`
- preferred execution rhythm: `weekly`
- standalone tactical branch: `rejected for deployment`
- annual-pool overlay promotion: `not approved`
- entry-timing branch: `locally positive, deployment not approved`
- take-profit branch: `weak positive evidence, not approved`
- formal branch status: `archived`

## Valid Next Steps

If this branch is revisited later, the most valid next directions are:

1. only reopen the branch with a genuinely new regime-filter hypothesis
2. test conditional activation by regime instead of all-week always-on overlay
3. test overlay on a momentum-approved subset instead of the annual approved pool directly
4. keep sell-side mean-reversion ideas as secondary and lower-priority than buy-side timing ideas
5. avoid treating prior local entry-timing wins as enough evidence by themselves

## What To Avoid

- do not retune `rev5_abnvol` on the same post-2021 acceptance window because the first overlay version underperformed
- do not reinterpret the current evidence as proof that mean reversion should become a third annual main line
- do not mix mean reversion conclusions into momentum conclusions
- do not use the local entry-timing result alone to justify deployment promotion
