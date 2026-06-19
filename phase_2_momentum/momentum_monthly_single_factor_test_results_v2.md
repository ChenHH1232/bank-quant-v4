# Momentum Monthly Single-Factor Test Results V2

Window:
- training: `2014-01-01` to `2019-01-01`
- validation: `2019-01-01` to `2021-01-01`
- monthly sample: first actual trade day of each month
- stock pool: top 60% by prior-20-trading-day average traded amount intersect top 60% by prior-20-trading-day average market cap
- target: next monthly rebalance `close-to-close` total return

- Monthly sample rows: `4558`
- In-pool monthly rows: `2132`
- Monthly rebalance dates: `145`
- Tested factors: `3`
- A: `1`
- B: `0`
- C: `2`
- D: `0`

Full ranking:
- `mom_6_1` | status=`A` | direction=`larger_better` | train_dates=`48` | val_dates=`24` | val_ic=`0.064954` | val_spread=`0.01777839`
- `mom_3_1` | status=`C` | direction=`smaller_better` | train_dates=`48` | val_dates=`24` | val_ic=`-0.061686` | val_spread=`-0.01363127`
- `mom_12_1` | status=`C` | direction=`smaller_better` | train_dates=`48` | val_dates=`24` | val_ic=`-0.067926` | val_spread=`-0.01978097`

Output:
- [momentum_monthly_single_factor_test_results_v2.csv](D:\hh\codex\v4\phase_2_momentum\momentum_monthly_single_factor_test_results_v2.csv)
