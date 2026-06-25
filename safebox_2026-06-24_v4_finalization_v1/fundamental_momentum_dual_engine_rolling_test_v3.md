# Fundamental Momentum Dual-Engine Rolling Test V3

Protocol:
- research scope = pre-2021 only
- common rebalance dates = intersection of fundamental and momentum panels
- folds reuse the fundamental pre-2021 rolling framework
- momentum sleeve is fixed at deployment-safe `mom_12_1`
- allocation framework is unchanged: separate sleeves, fixed budgets, `5%` engine cap, `8%` final stock cap
- only the fundamental sleeve varies across the three current formal main lines

Fundamental sleeve candidates:
- `balanced` = `base_core_6 + combo__ic_weight_train`
- `core_level_shadow` = `base_core_6 - eps + core_level_capital_adequacy_ratio`
- `balanced_shortbond_6040_4055` = `balanced` stock sleeve plus short-bond defensive overlay

- fold count: `2`
- rebalance snapshots: `78`

Strategy summary by branch:
- `balanced` `blend_60_40` | snapshots=`8` | mean_return=`0.000544` | cum_return=`0.004358` | strategy_mdd=`-0.001880` | excess_return_vs_mom=`0.002614` | excess_mdd_vs_mom=`-0.001018` | mean_invested_weight=`0.924433` | mean_cash_weight=`0.075567` | mean_defensive_weight=`0.000000`
- `balanced_shortbond_6040_4055` `blend_60_40` | snapshots=`8` | mean_return=`0.000544` | cum_return=`0.004358` | strategy_mdd=`-0.001880` | excess_return_vs_mom=`0.002614` | excess_mdd_vs_mom=`-0.001018` | mean_invested_weight=`0.924433` | mean_cash_weight=`0.075567` | mean_defensive_weight=`0.000000`
- `core_level_shadow` `blend_60_40` | snapshots=`8` | mean_return=`0.000542` | cum_return=`0.004335` | strategy_mdd=`-0.001880` | excess_return_vs_mom=`0.002592` | excess_mdd_vs_mom=`-0.001018` | mean_invested_weight=`0.923540` | mean_cash_weight=`0.076460` | mean_defensive_weight=`0.000000`
- `core_level_shadow` `blend_70_30` | snapshots=`8` | mean_return=`0.000526` | cum_return=`0.004208` | strategy_mdd=`-0.001960` | excess_return_vs_mom=`0.002323` | excess_mdd_vs_mom=`-0.001178` | mean_invested_weight=`0.942129` | mean_cash_weight=`0.057871` | mean_defensive_weight=`0.000000`
- `balanced` `blend_70_30` | snapshots=`8` | mean_return=`0.000523` | cum_return=`0.004188` | strategy_mdd=`-0.001960` | excess_return_vs_mom=`0.002303` | excess_mdd_vs_mom=`-0.001178` | mean_invested_weight=`0.942129` | mean_cash_weight=`0.057871` | mean_defensive_weight=`0.000000`
- `balanced_shortbond_6040_4055` `blend_70_30` | snapshots=`8` | mean_return=`0.000523` | cum_return=`0.004188` | strategy_mdd=`-0.001960` | excess_return_vs_mom=`0.002303` | excess_mdd_vs_mom=`-0.001178` | mean_invested_weight=`0.942129` | mean_cash_weight=`0.057871` | mean_defensive_weight=`0.000000`
- `balanced` `blend_80_20` | snapshots=`8` | mean_return=`0.000481` | cum_return=`0.003852` | strategy_mdd=`-0.001786` | excess_return_vs_mom=`0.001809` | excess_mdd_vs_mom=`-0.000829` | mean_invested_weight=`0.881154` | mean_cash_weight=`0.118846` | mean_defensive_weight=`0.000000`
- `balanced_shortbond_6040_4055` `blend_80_20` | snapshots=`8` | mean_return=`0.000481` | cum_return=`0.003852` | strategy_mdd=`-0.001786` | excess_return_vs_mom=`0.001809` | excess_mdd_vs_mom=`-0.000829` | mean_invested_weight=`0.881154` | mean_cash_weight=`0.118846` | mean_defensive_weight=`0.000000`
- `core_level_shadow` `blend_80_20` | snapshots=`8` | mean_return=`0.000481` | cum_return=`0.003852` | strategy_mdd=`-0.001786` | excess_return_vs_mom=`0.001809` | excess_mdd_vs_mom=`-0.000829` | mean_invested_weight=`0.881154` | mean_cash_weight=`0.118846` | mean_defensive_weight=`0.000000`
- `balanced` `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | strategy_mdd=`-0.001371` | excess_return_vs_mom=`0.000000` | excess_mdd_vs_mom=`0.000000` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750` | mean_defensive_weight=`0.000000`
- `balanced_shortbond_6040_4055` `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | strategy_mdd=`-0.001371` | excess_return_vs_mom=`0.000000` | excess_mdd_vs_mom=`0.000000` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750` | mean_defensive_weight=`0.000000`
- `core_level_shadow` `fundamental_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | strategy_mdd=`-0.001371` | excess_return_vs_mom=`0.000000` | excess_mdd_vs_mom=`0.000000` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750` | mean_defensive_weight=`0.000000`
- `shared_momentum_baseline` `momentum_only` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | strategy_mdd=`-0.001371` | excess_return_vs_mom=`0.000000` | excess_mdd_vs_mom=`0.000000` | mean_invested_weight=`0.681250` | mean_cash_weight=`0.318750` | mean_defensive_weight=`0.000000`

Best branch inside each allocation spec:
- `fundamental_only` best branch = `balanced` | cum_return=`0.002768` | mean_return=`0.000346` | excess_mdd_vs_mom=`0.000000`
- `blend_80_20` best branch = `balanced` | cum_return=`0.003852` | mean_return=`0.000481` | excess_mdd_vs_mom=`-0.000829`
- `blend_70_30` best branch = `core_level_shadow` | cum_return=`0.004208` | mean_return=`0.000526` | excess_mdd_vs_mom=`-0.001178`
- `blend_60_40` best branch = `balanced` | cum_return=`0.004358` | mean_return=`0.000544` | excess_mdd_vs_mom=`-0.001018`

Shared baseline:
- `momentum_only` | snapshots=`8` | cum_return=`0.002768` | mean_return=`0.000346` | strategy_mdd=`-0.001371`

Interpretation targets:
- compare whether updating the fundamental sleeve ranking alone improves the old separate-budget framework
- compare whether `core_level_shadow` helps more on relative path than `balanced` inside the same momentum blend
- compare whether `balanced_shortbond_6040_4055` improves capital preservation enough to justify lower equity exposure inside the blend
- compare whether a branch with slightly lower return still earns credit by reducing excess max drawdown versus the shared momentum baseline

Output:
- [fundamental_momentum_dual_engine_rolling_test_v3_detail.csv](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_test_v3_detail.csv)
