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
- `build_momentum_factor_panel_v1.py`: daily momentum factor panel builder
- `momentum_factor_panel_v1.csv` / `.md`: first-pass daily momentum panel and summary
- `build_momentum_single_factor_tests_v1.py` / `v2.py`: annual single-factor validation drafts
- `momentum_single_factor_test_results_v1.csv` / `.md`: first annual factor test outputs
- `momentum_single_factor_test_results_v2.csv` / `.md`: annual factor test outputs with stock-pool filter
- `build_momentum_rolling_validation_v1.py`: annual rolling validation baseline
- `momentum_rolling_validation_v1_results.csv` / `_folds.csv` / `.md`: annual rolling validation outputs
- `build_momentum_annual_strategy_backtest_v1.py`: annual strategy backtest baseline
- `momentum_annual_strategy_backtest_v1_detail.csv` / `.md`: annual strategy backtest outputs
- `build_momentum_quarterly_rebalance_panel_v1.py`: quarterly rebalance panel synced to fundamental rebalance dates
- `momentum_quarterly_rebalance_panel_v1.csv` / `.md`: quarterly sample panel and summary
- `build_momentum_quarterly_rolling_validation_v1.py`: formal quarterly rolling validation
- `momentum_quarterly_rolling_validation_v1_results.csv` / `_folds.csv` / `.md`: quarterly rolling validation outputs
- `build_momentum_quarterly_strategy_backtest_v1.py`: quarterly strategy backtest on rolling-selected alpha
- `momentum_quarterly_strategy_backtest_v1_detail.csv` / `.md`: quarterly strategy backtest outputs
- `momentum_candidate_pool_draft_v1.md`: frozen momentum candidate hierarchy draft

Current download rule:

- Do not overwrite legacy `phase_1_fundamental/raw_downloads/all_banks/*/daily_price.csv`
- Repaired momentum price files are written under `phase_2_momentum/raw_downloads/momentum_price_repair_v1`
- Save a separate `trade_calendar.csv` for holiday-adjusted rebalance alignment

Current formal main line:

- Rebalance frequency is quarterly, synced to the actual fundamental rebalance trading dates from `../phase_1_fundamental/phase1_training_panel.csv`
- Training window stays at 5 years, then validates and reviews on subsequent quarterly windows
- Stock pool uses the prior-20-trading-day average turnover amount top 80% intersect the prior-20-trading-day average market cap top 80%
- Current momentum alpha main line is `mom_12_1`
- `liq_money_1m` is retained as a support or monitoring variable, not mixed into the alpha score

Suggested next command:

```bash
python phase_2_momentum/download_joinquant_momentum_price_repair_v1.py --username YOUR_JQ_USER --password YOUR_JQ_PASSWORD
```
