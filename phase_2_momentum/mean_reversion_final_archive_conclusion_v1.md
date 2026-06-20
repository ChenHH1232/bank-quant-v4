# Mean Reversion Final Archive Conclusion V1

This document freezes the final archive conclusion for the bank mean-reversion branch after local research validation and the `2021-05-31` to `2026-05-29` JoinQuant out-of-sample comparison.

## Final Conclusion

The current final conclusion is:

- mean reversion exists in the bank universe as a short-horizon tactical effect
- but it does not currently earn promotion into the formal deployment stack
- therefore the mean-reversion branch is archived as a research conclusion, not as a live main-line strategy

## What Was Confirmed

The following points remain valid:

- `rev_5d` is the first confirmed short-horizon reversion signal
- `rev5_abnvol = -0.7 * rev_5d + 0.3 * abnormal_volume_ratio` is the strongest first-pass composite
- weekly execution is safer than daily execution for standalone tactical testing
- mean reversion is more useful on the buy side than on the sell side

## What Failed To Earn Promotion

### 1. Standalone Mean Reversion

The standalone weekly mean-reversion JoinQuant strategy did not survive the frozen post-2021 out-of-sample window.

Observed result:
- strategy return = `-22.55%`
- annualized return = `-5.14%`
- excess return = `-35.39%`
- max drawdown = `31.63%`

Interpretation:
- standalone mean reversion is not deployable as an independent bank strategy

### 2. Weekly Full-Pool Replacement

The weekly overlay logic on top of the annual approved pool also failed to beat the direct annual backbone.

Frozen comparison:
- annual approved-pool baseline total return = `0.584687`
- annual approved-pool plus weekly reversion overlay total return = `0.568945`

Interpretation:
- weekly full-pool replacement is not approved as a default execution override

### 3. Entry Timing Promotion

Local entry-timing research was positive, especially for:

- `timed_entry_rev5_abnvol`
- `staggered_entry_50_50`

But the real JoinQuant out-of-sample comparison did not confirm deployment value.

JoinQuant comparison:
- annual-pool mean-reversion entry strategy return = `37.13%`
- annual-pool direct-entry strategy return = `44.51%`
- mean-reversion entry max drawdown = `22.29%`
- direct entry max drawdown = `22.41%`

Interpretation:
- mean-reversion entry timing gave up meaningful return
- drawdown improvement was too small to justify the tradeoff
- so entry timing remains an observation, not an approved deployment rule

### 4. Sell-Side Take-Profit

The first overheat-based partial trim test showed only weak positive evidence.

Interpretation:
- it can reduce drawdown somewhat
- but it also reduces total return too visibly
- so it is not strong enough for default promotion

## Final Status Labels

- signal existence: `confirmed`
- standalone strategy: `rejected`
- weekly overlay: `rejected`
- entry timing as deployment rule: `not approved`
- take-profit overlay: `not approved`
- formal deployment status: `archived`

## Practical Takeaway

The current safest practical takeaway is:

- fundamentals remain the annual structural backbone
- momentum remains the active trading-style extension branch
- mean reversion should stay archived as a tactical research note
- if revisited later, it should only be reconsidered under strict regime filters or as a narrowly scoped auxiliary timing idea

## Discipline Note

The `2021-05-31` to `2026-05-29` JoinQuant window has now been used as the frozen out-of-sample acceptance check for this branch.

Therefore:

- do not continue retuning mean-reversion entry rules against this same window
- do not reinterpret local positive timing tests as deployment proof
- treat the branch as concluded unless a genuinely new hypothesis is introduced
