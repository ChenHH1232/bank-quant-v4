# Fundamental Defensive Overlay YOY Pool Linear Mapping Validation V1

Protocol:
- base execution line = annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- overlay compares each active annual factor against the same seasonal point one year earlier
- deterioration is measured inside the candidate pool after score availability plus liquidity and market-cap filters
- stock deterioration threshold is fixed at `50%`
- one stock is counted as deteriorated when its deteriorated-factor share crosses the fixed threshold
- this run compares treasury sizing mappings rather than threshold levels
- tested treasury mappings = `half(scale=0.50,cap=1.00) / scale70(scale=0.70,cap=1.00) / full(scale=1.00,cap=1.00) / cap40(scale=1.00,cap=0.40)`
- defensive asset = `treasury_etf_511010`

Chosen fold results:
- `annual_01` | status=`chosen_overlay` | config=`yoy_pool_linear_mapping__thr_50__full__asset_treasury_etf_511010` | threshold=`0.5` | mapping=`full` | scale=`1.0` | cap=`1.0` | train_cum=`0.069073` | test_cum=`0.032671` | review_cum=`0.030014` | review_mean_signal=`0.562500` | review_mean_treasury_weight=`0.562500`
- `annual_02` | status=`chosen_overlay` | config=`yoy_pool_linear_mapping__thr_50__full__asset_treasury_etf_511010` | threshold=`0.5` | mapping=`full` | scale=`1.0` | cap=`1.0` | train_cum=`0.070391` | test_cum=`0.020761` | review_cum=`0.003613` | review_mean_signal=`0.156822` | review_mean_treasury_weight=`0.156822`
- `annual_03` | status=`chosen_overlay` | config=`yoy_pool_linear_mapping__thr_50__cap40__asset_treasury_etf_511010` | threshold=`0.5` | mapping=`cap40` | scale=`1.0` | cap=`0.4` | train_cum=`0.037255` | test_cum=`0.018434` | review_cum=`0.011304` | review_mean_signal=`0.268620` | review_mean_treasury_weight=`0.268620`
- `annual_04` | status=`chosen_overlay` | config=`yoy_pool_linear_mapping__thr_50__full__asset_treasury_etf_511010` | threshold=`0.5` | mapping=`full` | scale=`1.0` | cap=`1.0` | train_cum=`0.057509` | test_cum=`0.030999` | review_cum=`0.024315` | review_mean_signal=`0.524266` | review_mean_treasury_weight=`0.524266`
- `annual_05` | status=`chosen_overlay` | config=`yoy_pool_linear_mapping__thr_50__full__asset_treasury_etf_511010` | threshold=`0.5` | mapping=`full` | scale=`1.0` | cap=`1.0` | train_cum=`0.072919` | test_cum=`0.039658` | review_cum=`0.001359` | review_mean_signal=`0.066667` | review_mean_treasury_weight=`0.066667`

Chosen-vs-baseline review summary:
- mean review cumulative advantage = `0.013097`
- mean review mean-return advantage = `0.003742`
- overlay beats baseline on review cumulative in `4/5` folds

Outputs:
- [fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1_config_results.csv)
- [fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1_chosen.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1_chosen.csv)
