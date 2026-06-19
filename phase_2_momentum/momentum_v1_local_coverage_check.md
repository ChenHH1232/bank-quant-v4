# Momentum V1 Local Coverage Check

## Scope

- Universe: `phase_1_fundamental/raw_downloads/all_banks/bank_universe.csv`
- Expected research window: `2014-01-01` to `2026-05-01`
- Backtest launch window to support first annual rebalance: `2021-05-31` onward

## Summary

- Bank count: `42`
- `daily_price.csv` exists: `42/42`
- `daily_valuation.csv` exists: `42/42`
- Price files with a date field: `0/42`
- Valuation files with a date field: `42/42`
- Valuation date span observed locally: `2014-01-02` to `2026-04-30`

## Conclusion

- Local valuation layer is structurally usable for momentum support fields such as `turnover_ratio`, `market_cap`, `circulating_market_cap`, `pe_ratio`, and `pb_ratio`.
- Local price layer is not yet directly usable for momentum because all `daily_price.csv` files are missing a transaction date column.
- Because momentum formation relies on exact trading-date alignment, the price layer should be re-downloaded or repaired from an authoritative source such as JoinQuant before formal factor construction.

## Blocking Items

- Non-ready rows: `42/42`
- Current blocking status is driven by `blocked_price_missing_date` for the whole universe.
- If we later need adjusted returns, the repaired price layer should also confirm whether it is pre-adjusted, post-adjusted, or raw.

## Output

- Detailed coverage table: `momentum_v1_local_coverage_check.csv`
