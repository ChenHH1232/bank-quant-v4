# Price Overheat Defense Safebox

Date: `2026-06-23`

Purpose:

- preserve the price-overheat defensive overlay branch derived from the earlier stock-overheat research
- keep the rolling evidence, executable candidate, and final acceptance conclusion in one recoverable snapshot

Included:

- `build_base_core_6_price_overheat_without_fundamental_improve_rolling_validation_v1.py`
- `base_core_6_price_overheat_without_fundamental_improve_rolling_validation_v1.md`
- `base_core_6_price_overheat_without_fundamental_improve_rolling_validation_v1_config_results.csv`
- `joinquant_v4_annual_backtest_strategy_base_core_6_price_overheat_without_fundamental_improve_v1.py`
- `price_overheat_defense_validation_summary_2026-06-23.md`

Decision snapshot:

- research idea: record each selected stock's entry price on the rebalance day, then allow only sell-down before the next rebalance if price overheats
- the overheat cap applies only to stocks whose fundamentals did not improve enough at entry
- rolling validation showed a slight out-of-sample edge for `trigger_20 / cap_010 / maximp_1`
- JoinQuant confirmation was effectively unchanged from the current preferred pure-fundamental main candidate
- decision: archive this branch for reference and do not promote it into the JoinQuant main strategy
