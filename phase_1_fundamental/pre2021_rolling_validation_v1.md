# Pre-2021 Rolling Validation V1

Protocol used in this first rolling framework:
- research cutoff: `2021-05-01`
- train window: previous `5` calendar years, month-aligned to the validation start month
- validation window: next `4` rebalance dates
- fold step: `2` rebalance dates
- minimum train history: `16` rebalance dates
- preprocessing and IC weights are fit inside each fold's train window only

Scenarios:
- `base_core_7`: `7` factors
- `base_plus_top2_9`: `9` factors

- fold count: `2`

Fold definitions:
- `fold_01` | train=`2013-11-01` to `2018-10-31` | validation=`2018-11-01` to `2019-11-01` | train_dates=`16` | val_dates=`4`
- `fold_02` | train=`2014-09-01` to `2019-09-01` | validation=`2019-09-02` to `2020-09-01` | train_dates=`17` | val_dates=`4`

Average validation results by scenario and combo:
- `base_core_7` best combo: `combo__quarterly_plus_annual` | mean_val_ic=`0.293585` | mean_val_spread=`0.0006536`
- `base_core_7` `combo__quarterly_plus_annual` | folds=`2` | mean_val_ic=`0.293585` | mean_val_ic_ir=`3.040008` | mean_val_spread=`0.0006536` | mean_val_pos_ic_ratio=`0.875`
- `base_core_7` `combo__ic_weight_train` | folds=`2` | mean_val_ic=`0.292061` | mean_val_ic_ir=`3.800957` | mean_val_spread=`0.00074248` | mean_val_pos_ic_ratio=`1.0`
- `base_core_7` `combo__equal_weight` | folds=`2` | mean_val_ic=`0.289737` | mean_val_ic_ir=`4.010994` | mean_val_spread=`0.00074328` | mean_val_pos_ic_ratio=`1.0`
- `base_plus_top2_9` best combo: `combo__equal_weight` | mean_val_ic=`0.351131` | mean_val_spread=`0.00079853`
- `base_plus_top2_9` `combo__equal_weight` | folds=`2` | mean_val_ic=`0.351131` | mean_val_ic_ir=`6.074108` | mean_val_spread=`0.00079853` | mean_val_pos_ic_ratio=`1.0`
- `base_plus_top2_9` `combo__quarterly_plus_annual` | folds=`2` | mean_val_ic=`0.325988` | mean_val_ic_ir=`1.849506` | mean_val_spread=`0.0007857` | mean_val_pos_ic_ratio=`0.875`
- `base_plus_top2_9` `combo__ic_weight_train` | folds=`2` | mean_val_ic=`0.307048` | mean_val_ic_ir=`3.935834` | mean_val_spread=`0.00073787` | mean_val_pos_ic_ratio=`1.0`

Outputs:
- [pre2021_rolling_validation_v1_folds.csv](D:\hh\codex\v4\phase_1_fundamental\pre2021_rolling_validation_v1_folds.csv)
- [pre2021_rolling_validation_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\pre2021_rolling_validation_v1_results.csv)