# Phase 2: Momentum

Goal:

- Add momentum features only after the fundamental phase has a stable cleaned panel
- Test whether momentum adds incremental explanatory power

Notes:

- Keep this phase statistically separate from mean reversion
- Momentum and mean reversion should be documented and validated separately

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
- `build_momentum_factor_panel_v2.py`: expanded daily momentum factor panel builder for monthly research
- `momentum_factor_panel_v2.csv` / `.md`: monthly-research momentum panel and summary
- `build_momentum_monthly_rebalance_panel_v2.py`: monthly rebalance sample builder
- `momentum_monthly_rebalance_panel_v2.csv` / `.md`: monthly sample panel and summary
- `build_momentum_monthly_single_factor_tests_v2.py`: monthly single-factor validation
- `momentum_monthly_single_factor_test_results_v2.csv` / `.md`: monthly single-factor test outputs
- `build_momentum_monthly_composite_tests_v2.py`: monthly composite factor validation
- `momentum_monthly_composite_test_results_v2.csv` / `.md`: monthly composite test outputs
- `build_momentum_monthly_rolling_validation_v2.py`: monthly rolling validation baseline
- `momentum_monthly_rolling_validation_v2_results.csv` / `_folds.csv` / `.md`: monthly rolling validation outputs
- `build_momentum_monthly_neutralized_rolling_validation_v3.py`: monthly rolling validation with liquidity-and-size neutralization
- `momentum_monthly_neutralized_rolling_validation_v3_results.csv` / `_folds.csv` / `.md`: neutralized monthly rolling validation outputs
- `joinquant_v4_monthly_momentum_strategy_v1.py`: JoinQuant monthly execution baseline with annual offline factor refresh and raw scoring
- `joinquant_v4_monthly_momentum_strategy_v2.py`: JoinQuant monthly execution variant with cross-sectional neutralization
- `momentum_joinquant_v1_v2_comparison_2021_2026.md`: direct JoinQuant comparison of raw `v1` versus neutralized `v2`
- `momentum_candidate_pool_draft_v1.md`: frozen momentum candidate hierarchy draft

Current download rule:

- Do not overwrite legacy `phase_1_fundamental/raw_downloads/all_banks/*/daily_price.csv`
- Repaired momentum price files are written under `phase_2_momentum/raw_downloads/momentum_price_repair_v1`
- Save a separate `trade_calendar.csv` for holiday-adjusted rebalance alignment

Current formal research line:

- Research validation has moved from quarterly to monthly rebalance sampling
- Rolling protocol is `5y train + 2y validation + 1y review`
- Monthly stock pool uses prior-20-trading-day average traded amount top 60% intersect prior-20-trading-day average market cap top 60%
- Factor library currently centers on `mom_3_1`, `mom_6_1`, `mom_12_1`, plus selected 6-1-centered composites
- Neutralized rolling validation improved cross-sectional research metrics, but that improvement did not carry through to the current JoinQuant deployment test

Current JoinQuant execution main line:

- Execution frequency is monthly, on each month's first actual trading day
- Active JoinQuant baseline is `joinquant_v4_monthly_momentum_strategy_v1.py`
- Factor refresh is annual, using an offline factor-selection table fixed on each May rebalance trading day
- Portfolio construction is equal-weight top bucket inside the filtered bank pool
- `joinquant_v4_monthly_momentum_strategy_v2.py` is retained as a negative validation branch, not the promoted main line

Current judgment:

- For this deployment version, raw `v1` is better than neutralized `v2`
- `v1` remains more consistent with the present objective: outperform the benchmark more clearly in rising environments
- `v2` showed somewhat better downside behavior, but gave up too much upside participation

Suggested next command:

```bash
python phase_2_momentum/download_joinquant_momentum_price_repair_v1.py --username YOUR_JQ_USER --password YOUR_JQ_PASSWORD
```
