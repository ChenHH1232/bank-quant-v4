# Daily Market Rebalance Input

Source:
- built from JoinQuant raw downloads in `raw_downloads/all_banks`
- one global rebalance date per quarter
- liquidity uses pre-rebalance rolling average traded amount over the last 20 trading days
- market cap uses the rebalance-date daily valuation snapshot

- Rebalance dates: `38`
- Snapshot rows: `998`

Output:
- [daily_market_rebalance_input.csv](D:\hh\codex\v4\phase_1_fundamental\daily_market_rebalance_input.csv)