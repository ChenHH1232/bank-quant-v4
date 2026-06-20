# Mean Reversion Staggered Entry Test V1

Purpose:
- compare immediate entry, full delayed entry, and 50/50 staggered entry
- keep the annual approved basket unchanged
- only change when the second half of the basket gets deployed

Frozen setup:
- search window: `4` weekly checkpoints
- holding horizon per leg proxy: `12` weeks
- immediate leg weight: `0.5`
- delayed leg weight: `0.5`

Results:
- `immediate_entry` | total_return_proxy=`0.321575` | max_drawdown_proxy=`-0.083261` | avg_case_return_12w=`0.02161` | median_case_return_12w=`0.027169` | avg_delay_weeks_proxy=`0.0`
- `timed_entry_rev5_abnvol` | total_return_proxy=`0.38906` | max_drawdown_proxy=`-0.080203` | avg_case_return_12w=`0.024923` | median_case_return_12w=`0.056582` | avg_delay_weeks_proxy=`1.4`
- `staggered_entry_50_50` | total_return_proxy=`0.35911` | max_drawdown_proxy=`-0.077621` | avg_case_return_12w=`0.023266` | median_case_return_12w=`0.041876` | avg_delay_weeks_proxy=`0.7`

Outputs:
- [mean_reversion_staggered_entry_test_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_staggered_entry_test_v1.csv)
- [mean_reversion_staggered_entry_test_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_staggered_entry_test_v1_detail.csv)
