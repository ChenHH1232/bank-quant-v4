# Momentum Price Repair Run Report V1

## Scope

- Task: rebuild the momentum price layer with explicit trading dates from JoinQuant
- Universe: `42` listed bank stocks from `phase_1_fundamental/raw_downloads/all_banks/bank_universe.csv`
- Window: `2014-01-01` to `2026-05-01`
- Price fields: `open`, `close`, `high`, `low`, `volume`, `money`
- Adjustment mode: `pre`

## Execution

- Credentials source: local safebox credential file
- Validation run: first executed with `--limit 3`
- Full run: then executed with `--skip-existing` to complete the whole universe without overwriting the validated sample files

## Result

- Total bank folders produced: `42`
- Newly downloaded in the full pass: `39`
- Reused from the validation pass: `3`
- Error count: `0`
- Total repaired price rows: `94922`
- Earliest observed trade date: `2014-01-02`
- Latest observed trade date: `2026-04-30`

## Output

- Repaired dataset root: `phase_2_momentum/raw_downloads/momentum_price_repair_v1`
- Trade calendar: `phase_2_momentum/raw_downloads/momentum_price_repair_v1/trade_calendar.csv`
- Run summary: `phase_2_momentum/raw_downloads/momentum_price_repair_v1/run_summary.json`
- Dataset manifest: `phase_2_momentum/raw_downloads/momentum_price_repair_v1/manifest.json`

## Conclusion

- The previous local bank price layer was blocked for momentum research because it had no explicit date column.
- This repaired layer resolves that structural issue and is now ready to support momentum factor construction such as `mom_1m`, `mom_3m`, `mom_6m`, `mom_12m`, and `mom_12_1`.
- The next step can move directly to building the momentum factor panel on top of this repaired price layer and the existing valuation layer.
