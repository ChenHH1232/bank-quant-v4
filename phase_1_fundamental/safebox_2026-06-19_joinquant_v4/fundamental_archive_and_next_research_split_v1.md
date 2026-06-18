# Fundamental Archive And Next Research Split V1

## Status

- Fundamental phase status: archived for now
- Archive date: `2026-06-19`
- Current conclusion:
  - the fundamental backbone is valid
  - the improvement layer is not a stable all-weather enhancement
  - part of the observed edge may still be explained by non-fundamental market dynamics

## What This Archive Must Preserve

- What problems we hit
- How each problem was solved
- What evidence supports the current conclusions
- What remains unresolved
- How to open the next research branch without contaminating the current one

## Timeline Summary

### Stage 1: Fundamental data collection and panel construction

- Goal:
  - build the bank fundamental panel needed for annual factor testing
- Main work:
  - collect JoinQuant bank fundamentals
  - backfill missing historical `bank_indicator`
  - extend training coverage to earlier years
- Key files:
  - `phase1_training_panel.csv`
  - `bank_indicator_2013_backfill_*`
  - `apply_joinquant_2013_bank_indicator_backfill.*`

### Stage 2: Early sample repair

- Problems:
  - global rebalance date logic was wrong
  - non-trading-day forward shifting was wrong
- Fixes:
  - repaired global rebalance date selection
  - repaired non-trading-day roll-forward handling
- Result:
  - `phase1_training_panel.csv` extended to start from `2014-05-05`
  - pre-2021 rebalance dates increased to `23`
- Evidence:
  - local panel rebuild outputs
  - refreshed factor testing results after the repair

### Stage 3: Factor screening refresh

- Goal:
  - rerun single-factor, improvement-factor, and multifactor selection after data fixes
- Result:
  - refreshed candidate pool
  - current best main line became the new `7+2` candidate structure
- Key files:
  - `final_core_factor_pool_v3.csv`
  - `final_core_factor_pool_v3.md`
  - `formal_annual_backtest_summary_v1.csv`
  - `formal_annual_backtest_summary_v1.md`

### Stage 4: Annual rule drafting and rolling research framing

- Goal:
  - formalize which factors stay permanent and which rotate annually
- Result:
  - annual factor-selection logic drafted
  - yearly refresh framework clarified
- Key files:
  - `annual_factor_selection_rule_draft_v1.md`
  - `annual_factor_refresh_5y2y1y_v1.*`
  - `formal_walk_forward_validation_v1.*`

### Stage 5: JoinQuant executable strategy conversion

- Problems:
  - initial JoinQuant script paste had syntax issues
  - early strategy version only covered 20 stocks
  - `bank_indicator` query failed in backtest mode
  - 2021 early years had no trades
- Fixes:
  - repaired syntax and expanded stock universe to the full research set
  - added detailed runtime logging
  - built probe strategy to test `bank_indicator`
  - verified that JoinQuant backtest returned empty `bank_indicator` snapshots
  - replaced dynamic `bank_indicator` access with embedded annual static data
- Result:
  - JoinQuant V4 annual strategy became executable
  - early empty-position issue was removed
- Key files:
  - `joinquant_v4_annual_backtest_strategy.py`
  - `joinquant_bank_indicator_probe_strategy.py`

### Stage 6: Primary vs benchmark validation

- Goal:
  - compare permanent core vs permanent core plus improvement layer
- Result:
  - both lines completed the same JoinQuant backtest window
  - full-window:
    - `primary`: `44.48%`
    - `benchmark`: `43.06%`
  - full-window gap:
    - `+1.42%` in favor of `primary`
- Key files:
  - `joinquant_v4_primary_vs_benchmark_yearly_comparison_v1.md`
  - `joinquant_v4_benchmark_yearly_summary_v1.*`
  - `joinquant_v4_annual_yearly_summary_v1.*`

### Stage 7: Yearly return and drawdown split

- Goal:
  - move beyond full-window summary and inspect year-by-year behavior
- Result:
  - `primary` stronger in:
    - `2021`
    - `2022`
    - `2025`
  - `benchmark` stronger in:
    - `2023`
    - `2024`
- Interpretation:
  - improvement layer is not a stable yearly enhancement
  - its contribution is regime-dependent
- Key files:
  - `joinquant_v4_yearly_return_drawdown_split_v1.csv`
  - `joinquant_v4_yearly_return_drawdown_comparison_v1.csv`
  - `joinquant_v4_yearly_return_drawdown_comparison_v1.md`

## Problems And Resolutions

### Problem 1: Missing early bank indicator history

- Symptom:
  - incomplete early bank-factor coverage
- Resolution:
  - historical backfill, especially 2013 coverage repair
- Evidence:
  - backfill files and refreshed panel outputs

### Problem 2: Incorrect rebalance-date construction

- Symptom:
  - sample construction error before 2021
- Resolution:
  - fixed global rebalance-date logic and non-trading-day shifting
- Evidence:
  - panel start moved earlier
  - rebalance-date count increased

### Problem 3: JoinQuant `bank_indicator` unavailable in backtest

- Symptom:
  - empty runtime snapshots
  - no trades in early years
- Resolution:
  - built probe strategy
  - confirmed runtime query failure
  - embedded annual static bank-indicator values into the strategy
- Evidence:
  - probe logs
  - restored score coverage and normal trades after replacement

### Problem 4: Unclear attribution of improvement-layer edge

- Symptom:
  - full-window `primary` beat `benchmark`, but yearly leadership alternated
- Resolution:
  - split yearly performance and yearly holdings
- Evidence:
  - 2023-2024 favored `benchmark`
  - 2021 and 2025 favored `primary`

## Current Conclusions

### Confirmed

- Permanent fundamental core is effective.
- Improvement layer can add value in some years.
- Improvement layer is not a stable all-weather additive edge.
- Large-bank-dominant regimes can favor the simpler `benchmark` structure.

### Not Yet Confirmed

- We have not proved that the improvement-layer edge is purely fundamental.
- We have not ruled out explanations such as:
  - market style exposure
  - momentum spillover
  - mean-reversion spillover

## Evidence Map

- Fundamental annual rule and candidate evidence:
  - `formal_annual_backtest_summary_v1.csv`
  - `final_core_factor_pool_v3.csv`
- JoinQuant executable proof:
  - `joinquant_v4_annual_backtest_strategy.py`
  - `joinquant_bank_indicator_probe_strategy.py`
- Primary vs benchmark comparison:
  - `joinquant_v4_primary_vs_benchmark_yearly_comparison_v1.md`
- Yearly regime evidence:
  - `joinquant_v4_yearly_return_drawdown_comparison_v1.csv`
  - `joinquant_v4_yearly_return_drawdown_comparison_v1.md`
- Archive snapshot:
  - `joinquant_v4_success_snapshot_2026-06-19.md`

## Unresolved Question

- Is the observed improvement-layer edge truly a slow fundamental repricing effect?
- Or is it partly acting as a proxy for:
  - momentum
  - mean reversion
  - style rotation

## Next Research Split

### Recommendation

- Split `momentum` and `mean reversion` into two separate research branches first.

### Why Not Merge Them Immediately

- They are related, but they are not the same mechanism.
- If we mix them too early, we will not know whether any overlap with the fundamental-improvement layer comes from:
  - trend continuation
  - reversal after overshoot
  - or both

### Recommended Order

1. Momentum branch

- Test whether improvement-layer winners are also high recent winners.
- Control variables:
  - `1M`
  - `3M`
  - `6M`
  - `12M`
  past return
- Main question:
  - does the fundamental-improvement edge survive after momentum neutralization?

2. Mean-reversion branch

- Test whether improvement-layer winners are actually rebound candidates after prior weakness.
- Control variables:
  - short-term reversal
  - medium-term drawdown recovery
  - oversold rebound proxies
- Main question:
  - does the edge survive after reversal-neutral controls?

3. Joint explanation stage

- Only after both branches are tested separately
- Then build a joint attribution table:
  - fundamental only
  - fundamental plus momentum overlap
  - fundamental plus mean-reversion overlap

## Why This Is Methodologically Safer

- It preserves interpretability.
- It reduces the chance of inventing a mixed explanation too early.
- It lets us say, with evidence, whether the current edge is closer to:
  - true fundamental repricing
  - momentum-assisted repricing
  - reversal-assisted repricing

## Research Boundary

- Fundamental phase is archived, not abandoned.
- New branches should not rewrite the archived fundamental conclusion.
- Any later hybrid strategy must be validated as a new hypothesis, not retrofitted into the current fundamental archive.
