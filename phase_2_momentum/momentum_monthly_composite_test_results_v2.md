# Momentum Monthly Composite Test Results V2

Window:
- training: `2014-01-01` to `2019-01-01`
- validation: `2019-01-01` to `2021-01-01`
- monthly sample: first actual trade day of each month
- stock pool: top 60% by prior-20-trading-day average traded amount intersect top 60% by prior-20-trading-day average market cap
- target: next monthly rebalance `close-to-close` total return

- Monthly sample rows: `4558`
- In-pool monthly rows: `2132`
- Monthly rebalance dates: `145`
- Tested composites: `2`
- A: `0`
- B: `0`
- C: `2`
- D: `0`

Full ranking:
- `combo_631_midheavy` | status=`C` | direction=`smaller_better` | val_ic=`-0.065458` | val_spread=`-0.01847869` | components=`0.1*mom_3_1 + 0.6*mom_6_1 + 0.3*mom_12_1`
- `combo_631_balanced` | status=`C` | direction=`smaller_better` | val_ic=`-0.072775` | val_spread=`-0.01918016` | components=`0.2*mom_3_1 + 0.5*mom_6_1 + 0.3*mom_12_1`

Output:
- [momentum_monthly_composite_test_results_v2.csv](D:\hh\codex\v4\phase_2_momentum\momentum_monthly_composite_test_results_v2.csv)
