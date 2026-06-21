# State-Gated Dual-Engine Rolling Validation V1

Protocol:
- research scope = pre-2021 only
- state proxy = observable-only `z_mcap + z_mom6_positive_ratio - z_money`
- train-set terciles define `weak_down / neutral_flat / strong_up`
- allocation mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum
- momentum engine = deployment-safe `mom_12_1`
- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`
- engine stock cap = `5%`
- final stock cap = `8%`

- fold count: `2`
- strategy snapshots: `32`

Strategy summary:
- `blend_60_40` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_invested_weight=`0.918873` | mean_cash_weight=`0.081127`
- `blend_80_20` | snapshots=`8` | mean_return=`0.000481` | cum_return=`0.003852` | mean_invested_weight=`0.881154` | mean_cash_weight=`0.118846`
- `state_gated_dual_engine` | snapshots=`8` | mean_return=`0.000439` | cum_return=`0.003511` | mean_invested_weight=`0.831250` | mean_cash_weight=`0.168750`
- `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750`

State mix summary:
- `neutral_flat` | snapshots=`6` | mean_return=`0.000389` | mean_f_budget=`0.80` | mean_m_budget=`0.20`
- `weak_down` | snapshots=`2` | mean_return=`0.000590` | mean_f_budget=`1.00` | mean_m_budget=`0.00`

Fold summary:
- `fold_01` `fundamental_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000`
- `fold_01` `blend_80_20` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001375` | mean_cash=`0.150192`
- `fold_01` `blend_60_40` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001528` | mean_cash=`0.090862`
- `fold_01` `state_gated_dual_engine` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001320` | mean_cash=`0.200000`
- `fold_02` `fundamental_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500`
- `fold_02` `blend_80_20` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002474` | mean_cash=`0.087500`
- `fold_02` `blend_60_40` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002792` | mean_cash=`0.071392`
- `fold_02` `state_gated_dual_engine` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002188` | mean_cash=`0.137500`

Interpretation:
- this validation asks whether disabling momentum in weak states improves the fixed-budget dual-engine baseline
- the observable state proxy is intentionally simple and leak-free
- if state-gated results do not beat fixed `60/40`, the next step should focus on better state observables rather than more allocation complexity

Output:
- [state_gated_dual_engine_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\state_gated_dual_engine_rolling_validation_v1_detail.csv)
