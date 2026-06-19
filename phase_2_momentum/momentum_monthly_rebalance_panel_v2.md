# Momentum Monthly Rebalance Panel V2

Definition:
- monthly rebalance date = first actual trading day of each month
- momentum layer keeps daily-derived bank signals but samples on the monthly calendar
- monthly pool uses prior-20-trading-day average amount top 60% intersect average market-cap top 60%
- v2 research fields focus on `mom_3_1`, `mom_6_1`, `mom_12_1` style monthly momentum

- rows: `4558`
- rebalance dates: `145`
- ready rows: `4037`
- in-pool rows: `2132`

Output:
- [momentum_monthly_rebalance_panel_v2.csv](D:\hh\codex\v4\phase_2_momentum\momentum_monthly_rebalance_panel_v2.csv)
