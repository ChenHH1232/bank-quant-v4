# Dual Engine Weight Stability Validation V1

Objective:
- test whether the current dual-engine result depends on one fragile weight point
- compare the local neighborhood around the deployed `60/40` blend

Protocol:
- research scope = pre-2021 only
- common rebalance dates = intersection of fundamental and momentum panels
- folds reuse the fundamental pre-2021 rolling framework
- fixed candidate neighborhood = `50/50`, `60/40`, `70/30`
- pure fundamental kept as the reference base line
- factor structure remains frozen
- engine stock cap = `5%`
- final stock cap = `8%`

- fold count: `2`
- rebalance snapshots: `32`

Strategy summary:
- `blend_60_40` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_invested_weight=`0.918873` | mean_cash_weight=`0.081127` | mean_overlap=`13.62`
- `blend_50_50` | snapshots=`8` | mean_return=`0.000530` | cum_return=`0.004240` | mean_invested_weight=`0.898840` | mean_cash_weight=`0.101160` | mean_overlap=`13.62`
- `blend_70_30` | snapshots=`8` | mean_return=`0.000518` | cum_return=`0.004144` | mean_invested_weight=`0.942129` | mean_cash_weight=`0.057871` | mean_overlap=`13.62`
- `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750` | mean_overlap=`0.00`

Fold summary:
- `fold_01`
- `fold_01` `fundamental_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000`
- `fold_01` `blend_50_50` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001522` | mean_cash=`0.111825`
- `fold_01` `blend_60_40` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001528` | mean_cash=`0.090862`
- `fold_01` `blend_70_30` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001457` | mean_cash=`0.082115`
- `fold_02`
- `fold_02` `fundamental_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500`
- `fold_02` `blend_50_50` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002714` | mean_cash=`0.090494`
- `fold_02` `blend_60_40` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002792` | mean_cash=`0.071392`
- `fold_02` `blend_70_30` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002683` | mean_cash=`0.033626`

Stability judgment:
- best_blend=`blend_60_40`
- local_blend_spread=`0.000181`
- all three nearby blends beat the pure fundamental reference in cumulative return
- this supports a `stable allocation neighborhood` reading rather than a single-point accident

Interpretation:
- the goal here is not to prove one exact weight is universally optimal
- the goal is to check whether the deployed `60/40` sits inside a sensible and stable allocation band
- only after this test passes should later attribution work treat the dual-engine structure as robust

Output:
- [dual_engine_weight_stability_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\dual_engine_weight_stability_validation_v1_detail.csv)
