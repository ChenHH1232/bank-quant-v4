# Mean Reversion Overlay Conclusion V1

This note freezes the current interpretation of the first mean-reversion overlay test.

## What We Tested

Two separate questions were tested:

1. standalone execution rhythm
- compare `daily` versus `weekly`
- fixed signal: `rev5_abnvol`
- fixed holding count: `5`
- result source: [mean_reversion_execution_comparison_v1.md](D:/hh/codex/v4/phase_2_momentum/mean_reversion_execution_comparison_v1.md)

2. overlay inside the real annual approved pool
- upper pool source: annual `primary` holding schedule from [joinquant_v4_annual_attribution_v1.csv](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_attribution_v1.csv)
- compare:
  - equal-weight hold the full approved pool
  - weekly rotate to the best `5` names by `rev5_abnvol` inside that pool
- result source: [mean_reversion_overlay_on_annual_pool_v1.md](D:/hh/codex/v4/phase_2_momentum/mean_reversion_overlay_on_annual_pool_v1.md)

## Frozen Findings

Finding A:
- for standalone tactical mean reversion, `weekly` execution is better than `daily`
- this supports the interpretation that the signal is short-horizon, but not so short that daily switching is optimal

Finding B:
- inside the real annual approved pool, the current weekly mean-reversion overlay did **not** beat the baseline full-pool hold
- baseline total return was `0.584687`
- overlay total return was `0.568945`
- baseline drawdown was also slightly better

## Current Interpretation

The safest interpretation right now is:

- mean reversion does have signal value as a standalone tactical branch
- but the current `rev5_abnvol` overlay is not yet proven to improve the annual backbone in the frozen post-2021 acceptance window
- therefore mean reversion should not yet be promoted as a default execution override for the annual approved pool

## Practical Decision

Current recommended status:
- standalone mean-reversion branch: keep alive
- weekly execution preference: keep
- annual-pool overlay promotion: hold back for now

## Next Valid Directions

If we continue this branch later, valid next questions are:

- should overlay be applied only in specific regimes instead of all weeks
- should overlay work on the momentum-approved subset rather than the annual pool directly
- should overlay act only as entry timing, not as a full weekly replacement of approved holdings

What should not be done:
- do not immediately retune `rev5_abnvol` on the same post-2021 acceptance window just because this overlay failed to add value
