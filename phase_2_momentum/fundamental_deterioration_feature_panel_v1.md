# Fundamental Deterioration Feature Panel V1

Definition:
- scenario backbone = `base_plus_top2_9`
- composite score = `combo__equal_weight`
- reference lag = previous `1` rebalance date
- score delta = current composite score minus reference composite score
- deterioration = score delta < 0

- stock panel rows: `296`
- date panel rows: `22`
- first rebalance date: `2014-09-01`
- last rebalance date: `2020-11-02`
- mean deterioration ratio: `0.5511193425`
- mean score delta: `-0.0218794870`

Candidate date-level observable fields:
- `deterioration_ratio`
- `severe_deterioration_ratio`
- `score_delta_mean`
- `score_delta_median`
- `score_delta_std`
- `score_delta_bottom_quartile_mean`
- `score_delta_top_bottom_spread`

Outputs:
- [fundamental_deterioration_stock_panel_v1.csv](D:\hh\codex\v4\phase_2_momentum\fundamental_deterioration_stock_panel_v1.csv)
- [fundamental_deterioration_date_panel_v1.csv](D:\hh\codex\v4\phase_2_momentum\fundamental_deterioration_date_panel_v1.csv)
