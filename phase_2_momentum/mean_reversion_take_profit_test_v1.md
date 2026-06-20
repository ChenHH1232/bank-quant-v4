# Mean Reversion Take-Profit Test V1

Purpose:
- test a minimal partial take-profit overlay inside the annual approved pool
- keep the approved holdings unchanged
- only reduce next-period exposure on names flagged as overheated

Frozen setup:
- overheat score: `0.6 * rev_5d + 0.2 * abnormal_volume_ratio + 0.2 * close_to_ma20`
- overheat threshold: top 20% within the approved pool on each weekly checkpoint
- trim ratio: `0.5`

Results:
- `baseline_hold` | total_return_proxy=`0.58484` | max_drawdown_proxy=`-0.217589` | avg_period_return_1w=`0.002233` | median_period_return_1w=`0.003062` | avg_overheat_count=`2.0`
- `partial_take_profit_trim50` | total_return_proxy=`0.518201` | max_drawdown_proxy=`-0.191025` | avg_period_return_1w=`0.001973` | median_period_return_1w=`0.001873` | avg_overheat_count=`2.0`

Outputs:
- [mean_reversion_take_profit_test_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_take_profit_test_v1.csv)
- [mean_reversion_take_profit_test_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_take_profit_test_v1_detail.csv)
