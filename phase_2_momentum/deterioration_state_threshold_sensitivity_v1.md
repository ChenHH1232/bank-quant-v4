# Deterioration State Threshold Sensitivity V1

Protocol:
- research scope = pre-2021 only
- candidates = `delta_median_only`, `breadth_only`, plus fixed `60/40` baseline
- objective = test whether the deterioration-state edge survives different train-set quantile cuts
- state allocation mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

- fold count: `2`

Ranking:
- `delta_median_only` `q33_q67` | formula=`+ 1.0*score_delta_median` | snapshots=`8` | mean_return=`0.000576` | cum_return=`0.004610` | mean_cash=`0.231136`
- `breadth_only` `q30_q70` | formula=`- 1.0*deterioration_ratio` | snapshots=`8` | mean_return=`0.000575` | cum_return=`0.004602` | mean_cash=`0.204982`
- `breadth_only` `q33_q67` | formula=`- 1.0*deterioration_ratio` | snapshots=`8` | mean_return=`0.000575` | cum_return=`0.004602` | mean_cash=`0.204982`
- `breadth_only` `q25_q75` | formula=`- 1.0*deterioration_ratio` | snapshots=`8` | mean_return=`0.000574` | cum_return=`0.004598` | mean_cash=`0.179982`
- `delta_median_only` `q30_q70` | formula=`+ 1.0*score_delta_median` | snapshots=`8` | mean_return=`0.000568` | cum_return=`0.004548` | mean_cash=`0.229886`
- `delta_median_only` `q25_q75` | formula=`+ 1.0*score_delta_median` | snapshots=`8` | mean_return=`0.000553` | cum_return=`0.004428` | mean_cash=`0.211914`
- `fixed_blend_60_40` `fixed` | formula=`fixed_60_40` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_cash=`0.081127`
- `breadth_only` `q20_q80` | formula=`- 1.0*deterioration_ratio` | snapshots=`8` | mean_return=`0.000522` | cum_return=`0.004181` | mean_cash=`0.129982`
- `delta_median_only` `q20_q80` | formula=`+ 1.0*score_delta_median` | snapshots=`8` | mean_return=`0.000506` | cum_return=`0.004046` | mean_cash=`0.193846`

Output:
- [deterioration_state_threshold_sensitivity_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\deterioration_state_threshold_sensitivity_v1_detail.csv)
