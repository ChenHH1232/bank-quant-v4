# Dual Engine Execution Stress Test V1

Objective:
- hold the `blend_60_40` signal layer fixed
- stress only the execution layer using delayed fills and higher one-way cost assumptions
- check whether the current dual-engine baseline is execution-fragile before formal report writing

Protocol:
- research scope remains pre-2021 rolling validation folds only
- target weights are rebuilt from the same `blend_60_40` rolling logic used in the main dual-engine test
- returns are proxied from daily close-to-close paths between delayed execution dates
- each rebalance pays one-way transaction cost on realized turnover
- terminal liquidation cost is included for conservative comparability

Scenarios:
- `immediate_cost10bps` | delay=`0` trading day(s) | one_way_cost=`10.0` bps
- `delay_1d_cost10bps` | delay=`1` trading day(s) | one_way_cost=`10.0` bps
- `delay_3d_cost10bps` | delay=`3` trading day(s) | one_way_cost=`10.0` bps
- `immediate_cost30bps` | delay=`0` trading day(s) | one_way_cost=`30.0` bps

Scenario summary:
- `immediate_cost10bps` | fold_count=`2` | mean_cum_return=`0.023876` | median_cum_return=`0.023876` | range=`[-0.010577, 0.058329]` | mean_turnover=`0.343652` | mean_total_cost=`0.001718`
- `delay_3d_cost10bps` | fold_count=`2` | mean_cum_return=`0.020625` | median_cum_return=`0.020625` | range=`[-0.009890, 0.051140]` | mean_turnover=`0.343652` | mean_total_cost=`0.001718`
- `immediate_cost30bps` | fold_count=`2` | mean_cum_return=`0.020353` | median_cum_return=`0.020353` | range=`[-0.013813, 0.054520]` | mean_turnover=`0.343652` | mean_total_cost=`0.005155`
- `delay_1d_cost10bps` | fold_count=`2` | mean_cum_return=`0.016184` | median_cum_return=`0.016184` | range=`[-0.035615, 0.067983]` | mean_turnover=`0.343652` | mean_total_cost=`0.001718`

Relative to immediate_cost10bps:
- `delay_1d_cost10bps` delta_mean_cum_return=`-0.007692`
- `delay_3d_cost10bps` delta_mean_cum_return=`-0.003251`
- `immediate_cost30bps` delta_mean_cum_return=`-0.003523`

Period-level averages:
- `delay_1d_cost10bps` | mean_gross_period_return=`0.007722` | mean_net_period_return=`0.007519` | mean_invested_weight=`0.918873`
- `delay_3d_cost10bps` | mean_gross_period_return=`0.008883` | mean_net_period_return=`0.008681` | mean_invested_weight=`0.918873`
- `immediate_cost10bps` | mean_gross_period_return=`0.009670` | mean_net_period_return=`0.009466` | mean_invested_weight=`0.918873`
- `immediate_cost30bps` | mean_gross_period_return=`0.009670` | mean_net_period_return=`0.009057` | mean_invested_weight=`0.918873`

Output:
- [dual_engine_execution_stress_test_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\dual_engine_execution_stress_test_v1_detail.csv)
