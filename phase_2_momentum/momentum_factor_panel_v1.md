# Momentum Factor Panel V1

Definition:
- one row per `date x code` on the repaired JoinQuant daily price layer
- merged with daily valuation support fields from the existing phase-1 raw layer
- momentum fields use fixed trading-day windows: `20/60/120/240`
- `mom_12_1` and `mom_6_1` skip the most recent `20` trading days
- intended usage: later annual rebalancing should read the latest available row before execution to avoid look-ahead

- Rows: `94922`
- Stocks: `42`
- Date span: `2014-01-02` to `2026-04-30`
- Core-ready rows: `83945`
- May core-ready rows: `6376`

Non-null coverage:
- `mom_1m`: `93782`
- `mom_3m`: `92105`
- `mom_6m`: `89588`
- `mom_12m`: `84561`
- `mom_12_1`: `84562`
- `mom_6_1`: `89586`
- `liq_money_1m`: `93485`
- `liq_turnover_1m`: `93485`

Output:
- [momentum_factor_panel_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_factor_panel_v1.csv)
