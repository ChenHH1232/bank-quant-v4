# Phase 2: Momentum

Goal:

- Add momentum features only after the fundamental phase has a stable cleaned panel
- Test whether momentum adds incremental explanatory power

Notes:

- Keep this phase statistically separate from mean reversion
- Start with daily-frequency momentum only

Current V1 artifacts:

- `momentum_v1_field_checklist.md`: required fields and first-pass factor scope
- `momentum_v1_local_coverage_check.md` / `.csv`: local raw coverage audit
- `build_momentum_local_coverage_check_v1.py`: reproducible local coverage checker
- `download_joinquant_momentum_price_repair_v1.py`: non-destructive JoinQuant price redownload with explicit date column

Current download rule:

- Do not overwrite legacy `phase_1_fundamental/raw_downloads/all_banks/*/daily_price.csv`
- Repaired momentum price files are written under `phase_2_momentum/raw_downloads/momentum_price_repair_v1`
- Save a separate `trade_calendar.csv` for holiday-adjusted rebalance alignment

Suggested next command:

```bash
python phase_2_momentum/download_joinquant_momentum_price_repair_v1.py --username YOUR_JQ_USER --password YOUR_JQ_PASSWORD
```
