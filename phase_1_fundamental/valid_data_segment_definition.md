# Valid Data Segment Definition

Updated: 2026-06-17

Purpose:

- Freeze the current Phase 1 bank fundamental dataset as a usable research segment.
- Label which bank-quarter observations are safe to enter the rolling research sample.
- Separate "data availability" from the later "rebalance stock-pool filter" step.

## Current Rule

We define one candidate segment per `code x quarter_key`.

A quarter row is marked as `effective_data_flag = 1` only when all of the following are true:

1. The quarter has usable standardized rows for all five mandatory quarterly families:
   - `income`
   - `cash_flow`
   - `balance`
   - `indicator`
   - `parent_balance`
2. We can compute a `rebalance_reference_date`, defined as the latest publish date across those five quarterly families for that stock-quarter.
3. On or before that `rebalance_reference_date`, the stock already has at least one published annual `bank_indicator` snapshot available as background bank-specific context.

## Effective Dates

- `effective_from_date`:
  - the day after the quarter's `rebalance_reference_date`
- `effective_until_date`:
  - the next quarter's `rebalance_reference_date`
  - or `open` if no later quarter exists in the current standardized dataset

This gives us a time segment that can later be joined to daily market data and rebalance calendars without leaking future disclosures.

## Important Boundary

This validity label does **not** yet apply the portfolio stock-pool rule.

That later rule is still:

- on each rebalance date, inside the bank universe:
  - keep the top 80% by liquidity
  - keep the top 80% by market cap
  - use the intersection as the stock pool

Very important:

- this stock pool must be recomputed independently on every rebalance date
- the pool is not allowed to be frozen once and reused for later quarters
- a stock can enter, leave, and re-enter the pool over time
- liquidity ranking and market-cap ranking must always be based on information available on that specific rebalance date only

So the current file answers:

- "Do we have enough disclosed fundamental data to use this bank-quarter at all?"

It does **not** yet answer:

- "Did this bank survive the liquidity and size screen on that rebalance date?"

## Current Outputs

- [quarterly_valid_data_segments.csv](/D:/hh/codex/v4/phase_1_fundamental/quarterly_valid_data_segments.csv)
- [quarterly_valid_data_segments.md](/D:/hh/codex/v4/phase_1_fundamental/quarterly_valid_data_segments.md)

## Next Join Step

When we add daily market data and rebalance calendars, each rebalance observation should carry two flags:

1. `effective_data_flag`
   - whether the disclosed fundamental data is valid and visible by that date
2. `rebalance_stock_pool_flag`
   - whether the stock is still inside the top-80% liquidity and top-80% market-cap intersection on that date

Only rows where both flags equal `1` should enter the rebalance-date candidate universe.

## Dynamic Rebalance Principle

For the future quarterly strategy layer, we should treat each rebalance date as a fresh cross-section:

1. determine the bank universe visible on that rebalance date
2. keep only stocks whose disclosed-data segment is effective on that rebalance date
3. compute rolling liquidity using only the pre-rebalance lookback window
4. compute market-cap ranking using the rebalance date snapshot
5. select the top 80% by liquidity
6. select the top 80% by market cap
7. use the intersection as the final rebalance-date stock pool

This means the stock pool is intentionally time-varying.
