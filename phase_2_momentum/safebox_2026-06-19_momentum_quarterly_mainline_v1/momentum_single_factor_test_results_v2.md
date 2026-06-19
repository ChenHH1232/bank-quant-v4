# Momentum Single-Factor Test Results V2

Window:
- training: `2014-05-01` to `2019-05-01`
- validation: `2019-05-01` to `2021-05-01`
- annual sample: first actual trade day in May of each year
- stock pool: at each annual rebalance date, keep only stocks that are both top 80% by prior-20-trading-day average traded amount and top 80% by prior-20-trading-day average market cap
- v2 change: keep the same 5-year training and 2-year validation windows, but relax annual-factor pass thresholds to suit small annual samples
- target: next annual rebalance `close-to-close` total return

- Annual sample rows: `373`
- In-pool annual rows: `268`
- Annual rebalance dates: `12`
- Tested factors: `8`
- A: `4`
- B: `0`
- C: `4`
- D: `0`

Focus factors:
- `mom_12_1` | status=`A` | direction=`larger_better` | train_rows=`56` | val_rows=`43` | val_ic=`0.283851` | val_spread=`0.21953049`
- `liq_money_1m` | status=`A` | direction=`larger_better` | train_rows=`69` | val_rows=`49` | val_ic=`0.261793` | val_spread=`0.2103603`
- `mom_6_1` | status=`A` | direction=`smaller_better` | train_rows=`57` | val_rows=`45` | val_ic=`0.066879` | val_spread=`0.03544974`
- `mom_12m` | status=`C` | direction=`smaller_better` | train_rows=`56` | val_rows=`43` | val_ic=`-0.345172` | val_spread=`-0.34078465`

Full ranking:
- `mom_12_1` | status=`A` | direction=`larger_better` | val_ic=`0.283851` | val_spread=`0.21953049`
- `liq_money_1m` | status=`A` | direction=`larger_better` | val_ic=`0.261793` | val_spread=`0.2103603`
- `mom_6_1` | status=`A` | direction=`smaller_better` | val_ic=`0.066879` | val_spread=`0.03544974`
- `mom_3m` | status=`A` | direction=`smaller_better` | val_ic=`0.003945` | val_spread=`-0.02607335`
- `mom_6m` | status=`C` | direction=`smaller_better` | val_ic=`-0.066365` | val_spread=`-0.08809138`
- `liq_turnover_1m` | status=`C` | direction=`larger_better` | val_ic=`-0.12952` | val_spread=`-0.10974334`
- `mom_1m` | status=`C` | direction=`smaller_better` | val_ic=`-0.24965` | val_spread=`-0.37173228`
- `mom_12m` | status=`C` | direction=`smaller_better` | val_ic=`-0.345172` | val_spread=`-0.34078465`

Output:
- [momentum_annual_rebalance_panel_v2.csv](D:\hh\codex\v4\phase_2_momentum\momentum_annual_rebalance_panel_v2.csv)
- [momentum_single_factor_test_results_v2.csv](D:\hh\codex\v4\phase_2_momentum\momentum_single_factor_test_results_v2.csv)
