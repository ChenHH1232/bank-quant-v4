# Dual Engine Weight Stability Note V1

Conclusion:
- the current dual-engine result is not a fragile single-point accident
- `60/40` remains the best local blend in the tested neighborhood
- but both adjacent blends, `50/50` and `70/30`, also beat the pure fundamental reference

So the correct reading is:
- `60/40` should be treated as the center of a usable stability band
- not as a one-off historical peak that only works at one exact parameter point

## What Was Tested

Research scope:
- pre-2021 only
- same common rebalance snapshots used by the earlier dual-engine rolling test

Frozen ingredients:
- fundamental engine unchanged
- momentum engine unchanged at deployment-safe `mom_12_1`
- stock caps unchanged

Only the allocation mix changed:
- `50/50`
- `60/40`
- `70/30`

Reference comparison:
- pure fundamental

## Result

Current ranking:

1. `blend_60_40`
- cum return = `0.004325`

2. `blend_50_50`
- cum return = `0.004240`

3. `blend_70_30`
- cum return = `0.004144`

4. `fundamental_only`
- cum return = `0.002768`

Local blend spread:
- best minus worst among the three blends = `0.000181`

This spread is small relative to the gap versus pure fundamental:
- `60/40 - fundamental_only` = `0.001557`
- `50/50 - fundamental_only` = `0.001472`
- `70/30 - fundamental_only` = `0.001376`

## Fold Behavior

`fold_01`
- `50/50` = `0.001522`
- `60/40` = `0.001528`
- `70/30` = `0.001457`
- `fundamental_only` = `0.000960`

`fold_02`
- `50/50` = `0.002714`
- `60/40` = `0.002792`
- `70/30` = `0.002683`
- `fundamental_only` = `0.001806`

This means:
- the neighborhood ordering is stable across both folds
- `60/40` leads in both folds
- but the neighboring blends remain clearly viable rather than collapsing

## Interpretation

This is the main thing the test needed to establish:

- the dual-engine structure itself appears valid
- the result is not driven by one knife-edge allocation choice

So later attribution should use the following wording:

- the project supports a `stable dual-engine allocation neighborhood`
- with `60/40` as the current practical center point

It should not use the weaker wording:

- `60/40` happened to be the single best backtest point

## Next Step

The next proper question is no longer:
- whether nearby blends also work

The next proper question is:
- what incremental value the dual-engine blend adds relative to pure fundamental

That means the next step should move to:
- return attribution
- drawdown comparison
- overlap and confirmation analysis

## References

- [build_dual_engine_weight_stability_validation_v1.py](D:\hh\codex\v4\phase_2_momentum\build_dual_engine_weight_stability_validation_v1.py)
- [dual_engine_weight_stability_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\dual_engine_weight_stability_validation_v1.md)
- [fundamental_momentum_dual_engine_rolling_test_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_test_v1.md)
