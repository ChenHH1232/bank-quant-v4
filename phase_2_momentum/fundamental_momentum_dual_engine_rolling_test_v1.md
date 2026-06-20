# Fundamental Momentum Dual-Engine Rolling Test V1

Protocol:
- research scope = pre-2021 only
- common rebalance dates = intersection of fundamental and momentum panels
- folds reuse the fundamental pre-2021 rolling framework
- fundamental engine = `base_plus_top2_9` with `combo__equal_weight`
- momentum engine = deployment-safe `mom_12_1` only
- engine stock cap = `5%`
- final stock cap = `8%`
- if strict cap prevents full investment, residual stays as cash in this first-pass test

- fold count: `2`
- strategy snapshots: `40`
- distinct rebalance dates per strategy: `8`

Strategy summary:
- `blend_60_40` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_invested_weight=`0.918873` | mean_cash_weight=`0.081127` | mean_overlap=`13.62`
- `blend_70_30` | snapshots=`8` | mean_return=`0.000518` | cum_return=`0.004144` | mean_invested_weight=`0.942129` | mean_cash_weight=`0.057871` | mean_overlap=`13.62`
- `blend_80_20` | snapshots=`8` | mean_return=`0.000481` | cum_return=`0.003852` | mean_invested_weight=`0.881154` | mean_cash_weight=`0.118846` | mean_overlap=`13.62`
- `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750` | mean_overlap=`0.00`
- `momentum_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750` | mean_overlap=`0.00`

Fold summary:
- `fold_01`
- `fold_01` `fundamental_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000`
- `fold_01` `momentum_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000`
- `fold_01` `blend_80_20` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001375` | mean_cash=`0.150192`
- `fold_01` `blend_70_30` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001457` | mean_cash=`0.082115`
- `fold_01` `blend_60_40` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001528` | mean_cash=`0.090862`
- `fold_02`
- `fold_02` `fundamental_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500`
- `fold_02` `momentum_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500`
- `fold_02` `blend_80_20` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002474` | mean_cash=`0.087500`
- `fold_02` `blend_70_30` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002683` | mean_cash=`0.033626`
- `fold_02` `blend_60_40` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002792` | mean_cash=`0.071392`

Interpretation:
- this first-pass test is intentionally conservative because strict `5%` single-engine caps can leave residual cash when the bank universe is small
- the main purpose is to compare whether blended allocation is more stable than pure fundamental or pure momentum on the same rebalance snapshots
- a stronger second pass would only be justified if one blend clearly beats both single-engine baselines
- `fundamental_only` and `momentum_only` are identical in this run, which suggests the current small universe plus strict cap rule is compressing the difference between the two single-engine books

Output:
- [fundamental_momentum_dual_engine_rolling_test_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_test_v1_detail.csv)
