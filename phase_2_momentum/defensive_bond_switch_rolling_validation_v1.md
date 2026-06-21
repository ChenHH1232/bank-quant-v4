# Defensive Bond Switch Rolling Validation V1

Protocol:
- research scope = pre-2021 only
- state proxy = observable-only `z_mcap + z_mom6_positive_ratio - z_money`
- train-set terciles define `weak_down / neutral_flat / strong_up`
- allocation mapping:
- `strong_up` => `60%` bank fundamental + `40%` bank momentum
- `neutral_flat` => `80%` bank fundamental + `20%` bank momentum
- `weak_down` bank-only => `100%` bank fundamental + `0%` bank momentum
- `weak_down` bond-switch => `60%` bank fundamental + `40%` bond ETF
- bond ETF = `511010.XSHG`
- momentum engine = deployment-safe `mom_12_1`
- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`
- engine stock cap = `5%`
- final stock cap = `8%`

- fold count: `2`
- strategy snapshots: `32`

Strategy summary:
- `blend_60_40` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_stock_return=`0.000540` | mean_bond_contribution=`0.000000` | mean_bond_weight=`0.000000` | mean_cash_weight=`0.081127`
- `state_gated_bank_only` | snapshots=`8` | mean_return=`0.000439` | cum_return=`0.003511` | mean_stock_return=`0.000439` | mean_bond_contribution=`0.000000` | mean_bond_weight=`0.000000` | mean_cash_weight=`0.168750`
- `state_gated_bond_switch` | snapshots=`8` | mean_return=`0.000405` | cum_return=`0.003239` | mean_stock_return=`0.000425` | mean_bond_contribution=`-0.000020` | mean_bond_weight=`0.100000` | mean_cash_weight=`0.087500`
- `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_stock_return=`0.000346` | mean_bond_contribution=`0.000000` | mean_bond_weight=`0.000000` | mean_cash_weight=`0.318750`

Bond-switch state mix summary:
- `neutral_flat` | snapshots=`6` | mean_return=`0.000389` | mean_f_budget=`0.80` | mean_m_budget=`0.20` | mean_bond_budget=`0.00`
- `weak_down` | snapshots=`2` | mean_return=`0.000454` | mean_f_budget=`0.60` | mean_m_budget=`0.00` | mean_bond_budget=`0.40`

Fold summary:
- `fold_01` `fundamental_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000` | mean_bond=`0.000000`
- `fold_01` `blend_60_40` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001528` | mean_cash=`0.090862` | mean_bond=`0.000000`
- `fold_01` `state_gated_bank_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001320` | mean_cash=`0.200000` | mean_bond=`0.000000`
- `fold_01` `state_gated_bond_switch` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001370` | mean_cash=`0.100000` | mean_bond=`0.100000`
- `fold_02` `fundamental_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500` | mean_bond=`0.000000`
- `fold_02` `blend_60_40` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002792` | mean_cash=`0.071392` | mean_bond=`0.000000`
- `fold_02` `state_gated_bank_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002188` | mean_cash=`0.137500` | mean_bond=`0.000000`
- `fold_02` `state_gated_bond_switch` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001866` | mean_cash=`0.075000` | mean_bond=`0.100000`

Interpretation:
- this validation asks whether weak-state bond substitution improves the current bank-only state gate
- it also tests whether the tactical sleeve should leave bank equity in weak states rather than simply return to bank fundamentals
- if bond-switch still fails to beat fixed `60/40`, then the main bottleneck is likely state identification rather than fallback asset choice alone

Output:
- [defensive_bond_switch_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\defensive_bond_switch_rolling_validation_v1_detail.csv)
