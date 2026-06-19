# Mean Reversion Single-Factor Test Results V1

Window:
- training: `2014-01-01` to `2019-01-01`
- validation: `2019-01-01` to `2021-01-01`
- monthly sample: first actual trade day of each month
- stock pool proxy: daily rows with `mean_reversion_ready_v1 == 1` on monthly rebalance dates
- target: next monthly rebalance `close-to-close` total return

- Monthly sample rows: `4684`
- Ready monthly rows: `4164`
- Monthly rebalance dates: `148`
- Tested factors: `4`
- A: `1`
- B: `0`
- C: `3`
- D: `0`

Full ranking:
- `rev_5d` | status=`A` | direction=`smaller_better` | train_dates=`48` | val_dates=`24` | val_ic=`0.017478` | val_spread=`0.00232963`
- `rev_10d` | status=`C` | direction=`larger_better` | train_dates=`48` | val_dates=`24` | val_ic=`-0.078141` | val_spread=`-0.01028944`
- `close_to_ma20` | status=`C` | direction=`larger_better` | train_dates=`48` | val_dates=`24` | val_ic=`-0.08278` | val_spread=`-0.00861735`
- `rev_20d` | status=`C` | direction=`larger_better` | train_dates=`48` | val_dates=`24` | val_ic=`-0.097045` | val_spread=`-0.00817972`

Outputs:
- [mean_reversion_monthly_rebalance_panel_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_monthly_rebalance_panel_v1.csv)
- [mean_reversion_single_factor_test_results_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_single_factor_test_results_v1.csv)
