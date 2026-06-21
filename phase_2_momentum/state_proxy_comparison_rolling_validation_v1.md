# State Proxy Comparison Rolling Validation V1

Protocol:
- research scope = pre-2021 only
- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`
- momentum engine = deployment-safe `mom_12_1`
- price proxy = observable `z_mcap + z_mom6_positive_ratio - z_money`
- deterioration proxy = `- deterioration_ratio + score_delta_mean + score_delta_bottom_quartile_mean`
- combined proxy = train-standardized price proxy plus train-standardized deterioration proxy
- train-set terciles define `weak_down / neutral_flat / strong_up` for each proxy independently
- state allocation mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum
- engine stock cap = `5%`
- final stock cap = `8%`

- fold count: `2`
- strategy snapshots: `40`

Strategy summary:
- `deterioration_state_proxy` | snapshots=`8` | mean_return=`0.000568` | cum_return=`0.004548` | mean_invested_weight=`0.770114` | mean_cash_weight=`0.229886`
- `blend_60_40` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_invested_weight=`0.918873` | mean_cash_weight=`0.081127`
- `combined_state_proxy` | snapshots=`8` | mean_return=`0.000532` | cum_return=`0.004261` | mean_invested_weight=`0.745114` | mean_cash_weight=`0.254886`
- `price_state_proxy` | snapshots=`8` | mean_return=`0.000439` | cum_return=`0.003511` | mean_invested_weight=`0.831250` | mean_cash_weight=`0.168750`
- `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750`

Proxy state mix summary:
- `price_state_proxy`
- `price_state_proxy` `neutral_flat` | snapshots=`6` | mean_return=`0.000389` | mean_f_budget=`0.80` | mean_m_budget=`0.20`
- `price_state_proxy` `weak_down` | snapshots=`2` | mean_return=`0.000590` | mean_f_budget=`1.00` | mean_m_budget=`0.00`
- `deterioration_state_proxy`
- `deterioration_state_proxy` `strong_up` | snapshots=`2` | mean_return=`0.002321` | mean_f_budget=`0.60` | mean_m_budget=`0.40`
- `deterioration_state_proxy` `neutral_flat` | snapshots=`1` | mean_return=`0.001295` | mean_f_budget=`0.80` | mean_m_budget=`0.20`
- `deterioration_state_proxy` `weak_down` | snapshots=`5` | mean_return=`-0.000278` | mean_f_budget=`1.00` | mean_m_budget=`0.00`
- `combined_state_proxy`
- `combined_state_proxy` `strong_up` | snapshots=`2` | mean_return=`0.002321` | mean_f_budget=`0.60` | mean_m_budget=`0.40`
- `combined_state_proxy` `weak_down` | snapshots=`6` | mean_return=`-0.000064` | mean_f_budget=`1.00` | mean_m_budget=`0.00`

Fold summary:
- `fold_01` `fundamental_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000`
- `fold_01` `blend_60_40` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001528` | mean_cash=`0.090862`
- `fold_01` `price_state_proxy` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001320` | mean_cash=`0.200000`
- `fold_01` `deterioration_state_proxy` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001705` | mean_cash=`0.286136`
- `fold_01` `combined_state_proxy` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001705` | mean_cash=`0.286136`
- `fold_02` `fundamental_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500`
- `fold_02` `blend_60_40` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002792` | mean_cash=`0.071392`
- `fold_02` `price_state_proxy` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002188` | mean_cash=`0.137500`
- `fold_02` `deterioration_state_proxy` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002837` | mean_cash=`0.173636`
- `fold_02` `combined_state_proxy` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002551` | mean_cash=`0.223636`

Interpretation:
- this validation asks whether deterioration-based state recognition beats the current price-breadth proxy
- the combined proxy tests whether observable price-state and fundamental-deterioration information are complementary
- if neither beats fixed `60/40`, the next step should focus on richer observable state features rather than new fallback routing

Output:
- [state_proxy_comparison_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\state_proxy_comparison_rolling_validation_v1_detail.csv)
