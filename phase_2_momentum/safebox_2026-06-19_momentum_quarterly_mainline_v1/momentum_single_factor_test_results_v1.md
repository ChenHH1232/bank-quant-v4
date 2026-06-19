# Momentum Single-Factor Test Results V1

Window:
- training: `2014-05-01` to `2019-05-01`
- validation: `2019-05-01` to `2021-05-01`
- annual sample: first actual trade day in May of each year
- stock pool: at each annual rebalance date, keep only stocks that are both top 80% by prior-20-trading-day average traded amount and top 80% by prior-20-trading-day average market cap
- target: next annual rebalance `close-to-close` total return

- Annual sample rows: `373`
- In-pool annual rows: `268`
- Annual rebalance dates: `12`
- Tested factors: `8`
- A: `0`
- B: `0`
- C: `0`
- D: `8`

Ranked results:
- `mom_12_1` | status=`D` | direction=`larger_better` | val_ic=`0.283851` | val_spread=`0.21953049`
- `liq_money_1m` | status=`D` | direction=`larger_better` | val_ic=`0.261793` | val_spread=`0.2103603`
- `mom_6_1` | status=`D` | direction=`smaller_better` | val_ic=`0.066879` | val_spread=`0.03544974`
- `mom_3m` | status=`D` | direction=`smaller_better` | val_ic=`0.003945` | val_spread=`-0.02607335`
- `mom_6m` | status=`D` | direction=`smaller_better` | val_ic=`-0.066365` | val_spread=`-0.08809138`
- `liq_turnover_1m` | status=`D` | direction=`larger_better` | val_ic=`-0.12952` | val_spread=`-0.10974334`
- `mom_1m` | status=`D` | direction=`smaller_better` | val_ic=`-0.24965` | val_spread=`-0.37173228`
- `mom_12m` | status=`D` | direction=`smaller_better` | val_ic=`-0.345172` | val_spread=`-0.34078465`

Output:
- [momentum_annual_rebalance_panel_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_annual_rebalance_panel_v1.csv)
- [momentum_single_factor_test_results_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_single_factor_test_results_v1.csv)
