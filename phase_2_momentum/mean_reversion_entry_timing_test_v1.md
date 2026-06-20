# Mean Reversion Entry Timing Test V1

Purpose:
- test mean reversion as annual-basket entry timing rather than full holding replacement
- keep the annual approved pool unchanged
- only compare immediate entry versus delayed entry chosen by pool-average `rev5_abnvol`

Frozen setup:
- search window: `4` weekly checkpoints
- holding horizon after entry: `12` weeks
- signal: lower pool-average `rev5_abnvol` is better

Results:
- `immediate_entry` | total_return_proxy=`0.321575` | max_drawdown_proxy=`-0.083261` | avg_case_return_12w=`0.02161` | median_case_return_12w=`0.027169` | avg_delay_weeks=`0.0`
- `timed_entry_rev5_abnvol` | total_return_proxy=`0.38906` | max_drawdown_proxy=`-0.080203` | avg_case_return_12w=`0.024923` | median_case_return_12w=`0.056582` | avg_delay_weeks=`1.4`

Outputs:
- [mean_reversion_entry_timing_test_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_entry_timing_test_v1.csv)
- [mean_reversion_entry_timing_test_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_entry_timing_test_v1_detail.csv)
