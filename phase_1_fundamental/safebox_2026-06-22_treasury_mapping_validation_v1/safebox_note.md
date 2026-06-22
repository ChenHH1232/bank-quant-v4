# Treasury Mapping Validation Safebox

Date: `2026-06-22`

Purpose:

- preserve the `thr50` treasury mapping validation branch before any further research changes
- keep both the rolling-validation evidence and the JoinQuant candidate files in one recoverable snapshot

Included:

- `build_fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1.py`
- `fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1.md`
- `fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1_config_results.csv`
- `fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1_chosen.csv`
- `fundamental_defensive_overlay_project_summary_2026-06-22.md`
- `fundamental_defensive_overlay_yoy_pool_linear_v2_threshold_freeze_summary.md`
- `joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_half_v1.py`
- `joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_cap40_v1.py`
- `joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_scale70_v1.py`

Decision snapshot:

- do not continue optimizing `thr50` treasury sizing with additional soft mappings
- fixed-`thr50` rolling mapping validation favored `full` in `4/5` folds and `cap40` in `1/5`
- `half` and `scale70` looked more comfortable in full-sample JoinQuant backtests than in rolling validation
- treasury remains an archived secondary branch behind `shortbond_6040_4055`
