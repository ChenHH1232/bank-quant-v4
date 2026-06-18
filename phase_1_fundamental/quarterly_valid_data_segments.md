# Quarterly Valid Data Segments

Rule:
- A quarter is valid only after all five mandatory quarterly statement families are available.
- The effective start date is the day after the latest mandatory quarterly publish date for that quarter.
- A quarter also needs at least one annual `bank_indicator` snapshot published on or before that quarter's rebalance reference date.
- This file labels data availability only; the future top-80% liquidity and market-cap stock-pool filter is a later overlay at rebalance time.

- Banks covered: `42`
- Banks with at least one valid quarter: `41`
- Quarter rows: `1539`
- Valid quarter rows: `1328`
- Invalid quarter rows: `211`

Invalid reason counts:
- `missing_quarterly_families:parent_balance`: `194`
- `no_prior_annual_bank_indicator`: `17`

Output:
- [quarterly_valid_data_segments.csv](D:\hh\codex\v4\phase_1_fundamental\quarterly_valid_data_segments.csv)