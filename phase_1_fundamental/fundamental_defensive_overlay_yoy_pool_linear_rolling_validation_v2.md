# Fundamental Defensive Overlay YOY Pool Linear Rolling Validation V2

Protocol:
- base execution line = annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- overlay compares each active annual factor against the same seasonal point one year earlier
- deterioration is measured inside the candidate pool after score availability plus liquidity and market-cap filters
- one stock is counted as deteriorated when its deteriorated-factor share crosses the tested threshold
- treasury weight is mapped linearly from deteriorated-stock ratio
- tested stock deterioration thresholds = `40% / 50% / 60%`
- defensive asset = `treasury_etf_511010`

Chosen fold results:
- `annual_01` | status=`chosen_overlay` | config=`yoy_pool_linear__thr_40__asset_treasury_etf_511010` | threshold=`0.4` | train_cum=`0.069073` | test_cum=`0.032671` | review_cum=`0.030014` | review_mean_signal=`0.562500` | review_mean_treasury_weight=`0.562500`
- `annual_02` | status=`chosen_overlay` | config=`yoy_pool_linear__thr_50__asset_treasury_etf_511010` | threshold=`0.5` | train_cum=`0.070391` | test_cum=`0.020761` | review_cum=`0.003613` | review_mean_signal=`0.156822` | review_mean_treasury_weight=`0.156822`
- `annual_03` | status=`chosen_overlay` | config=`yoy_pool_linear__thr_40__asset_treasury_etf_511010` | threshold=`0.4` | train_cum=`0.037255` | test_cum=`0.018384` | review_cum=`0.011304` | review_mean_signal=`0.268620` | review_mean_treasury_weight=`0.268620`
- `annual_04` | status=`chosen_overlay` | config=`yoy_pool_linear__thr_40__asset_treasury_etf_511010` | threshold=`0.4` | train_cum=`0.057509` | test_cum=`0.030999` | review_cum=`0.024315` | review_mean_signal=`0.524266` | review_mean_treasury_weight=`0.524266`
- `annual_05` | status=`chosen_overlay` | config=`yoy_pool_linear__thr_40__asset_treasury_etf_511010` | threshold=`0.4` | train_cum=`0.072919` | test_cum=`0.039658` | review_cum=`0.001359` | review_mean_signal=`0.066667` | review_mean_treasury_weight=`0.066667`

Chosen-vs-baseline review summary:
- mean review cumulative advantage = `0.013097`
- mean review mean-return advantage = `0.003742`
- overlay beats baseline on review cumulative in `4/5` folds

Outputs:
- [fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2_config_results.csv)
- [fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2_chosen.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2_chosen.csv)
