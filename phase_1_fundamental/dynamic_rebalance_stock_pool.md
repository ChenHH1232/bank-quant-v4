# Dynamic Rebalance Stock Pool Template

Rule:
- The stock pool must be recomputed independently on each rebalance date.
- A stock can enter, leave, and re-enter the pool across time.
- Only stocks with `effective_data_flag = 1` are allowed into the ranking step.
- The final pool on a rebalance date is the intersection of:
  - top 80% by liquidity
  - top 80% by market cap

Files:
- input template: [daily_market_rebalance_input.csv](D:\hh\codex\v4\phase_1_fundamental\daily_market_rebalance_input.csv)
- output template: [dynamic_rebalance_stock_pool.csv](D:\hh\codex\v4\phase_1_fundamental\dynamic_rebalance_stock_pool.csv)

- Rebalance dates currently populated from input: `38`
- Output rows currently generated: `998`