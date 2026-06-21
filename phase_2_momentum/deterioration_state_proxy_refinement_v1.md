# Deterioration State Proxy Refinement V1

Protocol:
- research scope = pre-2021 only
- objective = refine only the deterioration-based observable state family
- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`
- momentum engine = deployment-safe `mom_12_1`
- train-set terciles define `weak_down / neutral_flat / strong_up`
- state allocation mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

- fold count: `2`
- candidate count: `18`

Candidate ranking:
- `delta_median_only` | formula=`+ 1.0*score_delta_median` | snapshots=`8` | mean_return=`0.000576` | cum_return=`0.004610` | mean_cash=`0.231136`
- `breadth_only` | formula=`- 1.0*deterioration_ratio` | snapshots=`8` | mean_return=`0.000575` | cum_return=`0.004602` | mean_cash=`0.204982`
- `breadth_plus_median` | formula=`- 1.0*deterioration_ratio + 1.0*score_delta_median` | snapshots=`8` | mean_return=`0.000575` | cum_return=`0.004602` | mean_cash=`0.204982`
- `breadth_mean_bottom` | formula=`- 1.0*deterioration_ratio + 1.0*score_delta_mean + 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000568` | cum_return=`0.004548` | mean_cash=`0.229886`
- `breadth_mean_stdneg` | formula=`- 1.0*deterioration_ratio + 1.0*score_delta_mean - 1.0*score_delta_std` | snapshots=`8` | mean_return=`0.000568` | cum_return=`0.004548` | mean_cash=`0.229886`
- `breadth_median_bottom` | formula=`- 1.0*deterioration_ratio + 1.0*score_delta_median + 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000568` | cum_return=`0.004548` | mean_cash=`0.229886`
- `breadth_plus_mean` | formula=`- 1.0*deterioration_ratio + 1.0*score_delta_mean` | snapshots=`8` | mean_return=`0.000568` | cum_return=`0.004548` | mean_cash=`0.229886`
- `v1_base` | formula=`- 1.0*deterioration_ratio + 1.0*score_delta_mean + 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000568` | cum_return=`0.004548` | mean_cash=`0.229886`
- `top_bottom_spread_only` | formula=`+ 1.0*score_delta_top_bottom_spread` | snapshots=`8` | mean_return=`0.000543` | cum_return=`0.004349` | mean_cash=`0.096929`
- `delta_mean_only` | formula=`+ 1.0*score_delta_mean` | snapshots=`8` | mean_return=`0.000542` | cum_return=`0.004339` | mean_cash=`0.204886`
- `fixed_blend_60_40` | formula=`fixed_60_40` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_cash=`0.081127`
- `breadth_plus_bottom` | formula=`- 1.0*deterioration_ratio + 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000532` | cum_return=`0.004261` | mean_cash=`0.254886`
- `mean_plus_bottom` | formula=`+ 1.0*score_delta_mean + 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000532` | cum_return=`0.004261` | mean_cash=`0.254886`
- `median_plus_bottom` | formula=`+ 1.0*score_delta_median + 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000532` | cum_return=`0.004261` | mean_cash=`0.254886`
- `severe_plus_mean` | formula=`- 1.0*severe_deterioration_ratio + 1.0*score_delta_mean` | snapshots=`8` | mean_return=`0.000516` | cum_return=`0.004131` | mean_cash=`0.179886`
- `severe_plus_bottom` | formula=`- 1.0*severe_deterioration_ratio + 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000511` | cum_return=`0.004087` | mean_cash=`0.261818`
- `severe_breadth_only` | formula=`- 1.0*severe_deterioration_ratio` | snapshots=`8` | mean_return=`0.000504` | cum_return=`0.004035` | mean_cash=`0.109126`
- `bottom_quartile_only` | formula=`+ 1.0*score_delta_bottom_quartile_mean` | snapshots=`8` | mean_return=`0.000489` | cum_return=`0.003913` | mean_cash=`0.268750`

Top candidate state mix:
- `delta_median_only` `strong_up` | snapshots=`3` | mean_return=`0.001999` | mean_f_budget=`0.60` | mean_m_budget=`0.40`
- `delta_median_only` `weak_down` | snapshots=`5` | mean_return=`-0.000278` | mean_f_budget=`1.00` | mean_m_budget=`0.00`
- `breadth_only` `strong_up` | snapshots=`2` | mean_return=`0.002321` | mean_f_budget=`0.60` | mean_m_budget=`0.40`
- `breadth_only` `neutral_flat` | snapshots=`2` | mean_return=`0.000760` | mean_f_budget=`0.80` | mean_m_budget=`0.20`
- `breadth_only` `weak_down` | snapshots=`4` | mean_return=`-0.000391` | mean_f_budget=`1.00` | mean_m_budget=`0.00`
- `breadth_plus_median` `strong_up` | snapshots=`2` | mean_return=`0.002321` | mean_f_budget=`0.60` | mean_m_budget=`0.40`
- `breadth_plus_median` `neutral_flat` | snapshots=`2` | mean_return=`0.000760` | mean_f_budget=`0.80` | mean_m_budget=`0.20`
- `breadth_plus_median` `weak_down` | snapshots=`4` | mean_return=`-0.000391` | mean_f_budget=`1.00` | mean_m_budget=`0.00`
- `breadth_mean_bottom` `strong_up` | snapshots=`2` | mean_return=`0.002321` | mean_f_budget=`0.60` | mean_m_budget=`0.40`
- `breadth_mean_bottom` `neutral_flat` | snapshots=`1` | mean_return=`0.001295` | mean_f_budget=`0.80` | mean_m_budget=`0.20`
- `breadth_mean_bottom` `weak_down` | snapshots=`5` | mean_return=`-0.000278` | mean_f_budget=`1.00` | mean_m_budget=`0.00`
- `breadth_mean_stdneg` `strong_up` | snapshots=`2` | mean_return=`0.002321` | mean_f_budget=`0.60` | mean_m_budget=`0.40`
- `breadth_mean_stdneg` `neutral_flat` | snapshots=`1` | mean_return=`0.001295` | mean_f_budget=`0.80` | mean_m_budget=`0.20`
- `breadth_mean_stdneg` `weak_down` | snapshots=`5` | mean_return=`-0.000278` | mean_f_budget=`1.00` | mean_m_budget=`0.00`

Output:
- [deterioration_state_proxy_refinement_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\deterioration_state_proxy_refinement_v1_detail.csv)
