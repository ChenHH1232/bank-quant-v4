# Fundamental Gated Momentum Rolling Validation V1

Protocol:
- research scope = pre-2021 only
- objective = test whether fundamentals should act as a candidate gate while momentum ranks inside the approved pool
- monthly momentum rank uses deployment-safe `mom_12_1` only in this first pass
- fundamental score source = quarterly `combo__equal_weight` carried forward to monthly rebalance dates
- final holdings are equal-weight within each selected set

- fold count: `2`
- strategy snapshots: `130`

Strategy summary:
- `direct_mom12_top6` | snapshots=`26` | mean_return=`0.000410` | cum_return=`0.010592` | mean_candidate_count=`13.65` | mean_holding_count=`6.00`
- `gated_top16_mom12_top6` | snapshots=`26` | mean_return=`0.000410` | cum_return=`0.010592` | mean_candidate_count=`13.65` | mean_holding_count=`6.00`
- `gated_top20_mom12_top6` | snapshots=`26` | mean_return=`0.000410` | cum_return=`0.010592` | mean_candidate_count=`13.65` | mean_holding_count=`6.00`
- `fundamental_top16_equal` | snapshots=`26` | mean_return=`0.000293` | cum_return=`0.007548` | mean_candidate_count=`13.65` | mean_holding_count=`13.65`
- `fundamental_top20_equal` | snapshots=`26` | mean_return=`0.000293` | cum_return=`0.007548` | mean_candidate_count=`13.65` | mean_holding_count=`13.65`

Interpretation targets:
- compare `gated_top16_mom12_top6` and `gated_top20_mom12_top6` against direct momentum to test whether fundamental admission improves momentum selection
- compare the gated versions against `fundamental_top16_equal` and `fundamental_top20_equal` to test whether momentum adds value after fundamental admission

Output:
- [fundamental_gated_momentum_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\fundamental_gated_momentum_rolling_validation_v1_detail.csv)
