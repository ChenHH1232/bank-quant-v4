# Mean Reversion Factor Panel V1

Definition:
- reuses `momentum_factor_panel_v2.csv` as the daily base panel
- adds short-window reversal, oversold, and 20-day liquidity/size controls for mean-reversion research

- rows: `94922`
- stocks: `42`
- date span: `2014-01-02` to `2026-04-30`
- ready rows: `84398`

Non-null coverage:
- `rev_5d`: `94465`
- `rev_10d`: `94221`
- `rev_20d`: `93782`
- `close_to_ma20`: `93485`
- `intramonth_drawdown_20d`: `93485`

Output:
- [mean_reversion_factor_panel_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_factor_panel_v1.csv)
