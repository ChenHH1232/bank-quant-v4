# Valid Data Segment Freeze

Date: 2026-06-17

This freeze records the current usable Phase 1 bank-fundamental dataset before later rebalance-date stock-pool filtering.

## Frozen Outputs

- `eastmoney_bank_indicator_extracted_values.csv`
- `eastmoney_bank_indicator_extraction_missing.csv`
- `eastmoney_bank_indicator_missing_classified.csv`
- `quarterly_valid_data_segments.csv`

## Snapshot Counts

- Eastmoney bank-indicator structured rows: `707`
- Eastmoney bank-indicator missing rows: `261`
- Quarterly valid-data rows: `1286`
- Quarterly rows total: `1539`

## Validity Interpretation

- `quarterly_valid_data_segments.csv` labels whether a `stock x quarter` observation is usable after disclosure.
- It does not yet apply the later liquidity and market-cap top-80% filter.
- That future rebalance stock pool should only be built from rows where:
  - `effective_data_flag = 1`
  - and the future rebalance liquidity/size screen also passes
- the future rebalance stock pool must be recomputed independently at every quarterly rebalance date
- we do not allow a one-time fixed stock pool to be reused across all later rebalances

## Remaining Research Gaps

- The remaining rule-upgrade gap is concentrated in `liquidity_matching_ratio`.
- Most remaining bank-indicator misses are no longer pure extraction-rule failures; they mainly come from source-text alias or disclosure-format gaps.
