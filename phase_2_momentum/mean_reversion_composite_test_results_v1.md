# Mean Reversion Composite Test Results V1

Window:
- training: `2014-01-01` to `2019-01-01`
- validation: `2019-01-01` to `2021-01-01`
- monthly sample: first actual trade day of each month
- target: next monthly rebalance `close-to-close` total return

- Ready monthly rows: `4164`
- Monthly rebalance dates: `136`
- Tested composites: `3`
- A: `1`
- B: `0`
- C: `2`
- D: `0`

Full ranking:
- `rev5_abnvol` | status=`A` | val_ic=`0.05792` | val_spread=`0.00969369` | components=`-0.7*rev_5d + 0.3*abnormal_volume_ratio`
- `rev5_downratio` | status=`C` | val_ic=`0.018938` | val_spread=`0.00490857` | components=`-0.7*rev_5d + 0.3*down_day_ratio_20d`
- `rev5_lowpb` | status=`C` | val_ic=`-0.029805` | val_spread=`-0.0029867` | components=`-0.7*rev_5d + -0.3*pb_ratio`

Output:
- [mean_reversion_composite_test_results_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_composite_test_results_v1.csv)
