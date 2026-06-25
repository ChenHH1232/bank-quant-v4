# Fundamental Defensive Overlay YOY Pool Linear Persist Rolling Validation V3

Protocol:
- base execution line = annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- overlay compares each active annual factor against the same seasonal point one year earlier
- deterioration is measured inside the candidate pool after score availability plus liquidity and market-cap filters
- one stock is counted as deteriorated when its deteriorated-factor share crosses the tested threshold
- treasury weight starts from deteriorated-stock ratio
- consecutive bad rebalances add `+10%` on streak 2 and `+20%` on streak 3+
- treasury weight cap = `60%`
- tested stock deterioration thresholds = `60%`
- defensive asset = `treasury_etf_511010`

Chosen fold results:
- `annual_01` | status=`chosen_overlay` | config=`yoy_pool_linear_persist__thr_60__asset_treasury_etf_511010` | threshold=`0.6` | train_cum=`0.038077` | test_cum=`0.033351` | review_cum=`0.025423` | review_mean_signal=`0.322917` | review_mean_treasury_weight=`0.447917` | review_mean_persist_add=`0.125000` | review_max_bad_streak=`4.0`
- `annual_02` | status=`chosen_overlay` | config=`yoy_pool_linear_persist__thr_60__asset_treasury_etf_511010` | threshold=`0.6` | train_cum=`0.045200` | test_cum=`0.013875` | review_cum=`-0.000191` | review_mean_signal=`0.029647` | review_mean_treasury_weight=`0.029647` | review_mean_persist_add=`0.000000` | review_max_bad_streak=`1.0`
- `annual_03` | status=`chosen_overlay` | config=`yoy_pool_linear_persist__thr_60__asset_treasury_etf_511010` | threshold=`0.6` | train_cum=`0.053304` | test_cum=`0.026899` | review_cum=`0.016211` | review_mean_signal=`0.268620` | review_mean_treasury_weight=`0.368620` | review_mean_persist_add=`0.100000` | review_max_bad_streak=`3.0`
- `annual_04` | status=`chosen_best_available` | config=`yoy_pool_linear_persist__thr_60__asset_treasury_etf_511010` | threshold=`0.6` | train_cum=`0.005829` | test_cum=`0.001750` | review_cum=`0.004822` | review_mean_signal=`0.000000` | review_mean_treasury_weight=`0.000000` | review_mean_persist_add=`0.000000` | review_max_bad_streak=`0.0`
- `annual_05` | status=`chosen_overlay` | config=`yoy_pool_linear_persist__thr_60__asset_treasury_etf_511010` | threshold=`0.6` | train_cum=`0.057066` | test_cum=`0.026640` | review_cum=`0.001433` | review_mean_signal=`0.016667` | review_mean_treasury_weight=`0.016667` | review_mean_persist_add=`0.000000` | review_max_bad_streak=`1.0`

Chosen-vs-baseline review summary:
- mean review cumulative advantage = `0.008516`
- mean review mean-return advantage = `0.002370`
- overlay beats baseline on review cumulative in `3/5` folds

Outputs:
- [fundamental_defensive_overlay_yoy_pool_linear_persist_rolling_validation_v3_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_persist_rolling_validation_v3_config_results.csv)
- [fundamental_defensive_overlay_yoy_pool_linear_persist_rolling_validation_v3_chosen.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_persist_rolling_validation_v3_chosen.csv)
