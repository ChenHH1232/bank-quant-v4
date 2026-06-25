# JoinQuant V4 Success Snapshot 2026-06-19

## What Is Confirmed

- The JoinQuant V4 annual strategy is executable and no longer suffers from the early empty-position issue.
- `bank_indicator` runtime access in JoinQuant backtest was replaced with embedded annual static data, which restored full scoring coverage for the required windows.
- The `primary` line and the `benchmark` line have both been run successfully over the same backtest window.
- Their rebalance logs, annual plan usage, holdings, and yearly performance splits have been archived locally.

## Core Result

- Full-window `primary` return: `44.48%`
- Full-window `benchmark` return: `43.06%`
- Full-window return gap: `+1.42%` in favor of `primary`

## Annual Result Pattern

- `primary` is stronger in:
  - 2021
  - 2022
  - 2025
- `benchmark` is stronger in:
  - 2023
  - 2024

## What This Means

- The permanent fundamental backbone is valid on its own.
- The improvement layer helps in some years, but it is not a stable all-weather enhancement.
- Any future rule that conditionally enables the improvement layer must be validated in a clean rolling framework and must not be justified by reading the current out-of-sample years backward.

## Key Local Files

- `joinquant_v4_annual_backtest_strategy.py`
- `joinquant_v4_annual_attribution_v1.csv`
- `joinquant_v4_annual_yearly_summary_v1.csv`
- `joinquant_v4_benchmark_yearly_summary_v1.csv`
- `joinquant_v4_primary_vs_benchmark_yearly_comparison_v1.md`
- `joinquant_v4_yearly_return_drawdown_comparison_v1.csv`
- `joinquant_v4_daily_nav_input_from_results_v1.csv`

## Current Research Boundary

- We can treat conditional improvement-layer activation as a new research hypothesis.
- We should not treat it as a validated production rule yet.
- The next valid step is rolling verification under a pre-declared decision rule.

## Later Comparison Addendum

- a later expanding-memory comparison has now also been completed on the pure-fundamental annual refresh branch
- protocol:
  - keep `2Y` test and `1Y` review unchanged
  - change only the train-memory rule from fixed `5Y` to expanding `5Y -> 6Y -> 7Y -> 8Y -> 9Y`
- current rolling conclusion:
  - expanding memory is executable and does retain more factors in later years
  - but it does **not** beat the fixed `5Y` baseline on the main review-year scoring results
- a later JoinQuant executable check also confirmed the same direction:
  - expanding `benchmark` return = `39.33%`
  - expanding `primary` return = `32.39%`
  - both remain weaker than the archived fixed-window main line
- so the current safe reading is:
  - expanding memory is a valid comparison branch
  - but fixed `5Y` remains the default pure-fundamental execution baseline

- a further `5Y fixed + memory carry` comparison has also now been tested
- protocol:
  - keep the train window fixed at the latest `5Y`
  - allow up to `2` previous-year selected `base_core` factors to survive for one extra year
  - require train pass, test positive ratio >= `0.5`, and test ic >= `-0.05`
- current result:
  - factor retention becomes slightly smoother in the middle folds
  - but the main review-year `ic_weight_train` result still weakens relative to the original fixed `5Y` line
- so the current safe reading is:
  - memory carry `v1` is mechanically viable
  - but it is not yet strong enough to replace the original fixed-window refresh rule

## Current Baseline Status

- default pure-fundamental baseline still = fixed `5Y` annual refresh
- expanding memory = archived executable comparison branch
- memory carry `v1` = archived stability experiment, not promoted
