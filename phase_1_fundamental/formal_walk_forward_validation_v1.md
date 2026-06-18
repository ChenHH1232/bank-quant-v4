# Formal Walk-Forward Validation V1

Protocol:
- formal start: `2021-05-01`
- each rebalance date `T` is evaluated as a standalone out-of-sample walk-forward fold
- train window: previous `5` calendar years ending immediately before `T`
- minimum train history: `15` rebalance dates
- preprocessing and IC weights are refit inside each fold's train window only

Scenarios:
- `base_core_7`: `7` factors
- `base_plus_top2_9`: `9` factors

- walk-forward fold count: `15`

Fold definitions:
- `wf_01` | train=`2016-05-01` to `2021-05-05` | prediction date=`2021-05-06` | train_dates=`15`
- `wf_02` | train=`2016-09-01` to `2021-08-31` | prediction date=`2021-09-01` | train_dates=`15`
- `wf_03` | train=`2016-11-01` to `2021-10-31` | prediction date=`2021-11-01` | train_dates=`15`
- `wf_04` | train=`2017-05-01` to `2022-05-04` | prediction date=`2022-05-05` | train_dates=`15`
- `wf_05` | train=`2017-09-01` to `2022-08-31` | prediction date=`2022-09-01` | train_dates=`15`
- `wf_06` | train=`2017-11-01` to `2022-10-31` | prediction date=`2022-11-01` | train_dates=`15`
- `wf_07` | train=`2018-05-01` to `2023-05-03` | prediction date=`2023-05-04` | train_dates=`15`
- `wf_08` | train=`2018-09-01` to `2023-08-31` | prediction date=`2023-09-01` | train_dates=`15`
- `wf_09` | train=`2018-11-01` to `2023-10-31` | prediction date=`2023-11-01` | train_dates=`15`
- `wf_10` | train=`2019-05-01` to `2024-05-05` | prediction date=`2024-05-06` | train_dates=`15`
- `wf_11` | train=`2019-09-01` to `2024-09-01` | prediction date=`2024-09-02` | train_dates=`15`
- `wf_12` | train=`2019-11-01` to `2024-10-31` | prediction date=`2024-11-01` | train_dates=`15`
- `wf_13` | train=`2020-05-01` to `2025-05-05` | prediction date=`2025-05-06` | train_dates=`15`
- `wf_14` | train=`2020-09-01` to `2025-08-31` | prediction date=`2025-09-01` | train_dates=`15`
- `wf_15` | train=`2020-11-01` to `2025-11-02` | prediction date=`2025-11-03` | train_dates=`15`

Average post-2021 validation results by scenario and combo:
- `base_core_7` best combo: `combo__ic_weight_train` | mean_post2021_ic=`0.081454` | mean_post2021_spread=`0.00034303`
- `base_core_7` `combo__ic_weight_train` | folds=`15` | mean_post2021_ic=`0.081454` | mean_post2021_ic_ir=`n/a` | mean_post2021_spread=`0.00034303` | mean_post2021_pos_ic_ratio=`0.642857`
- `base_core_7` `combo__quarterly_plus_annual` | folds=`15` | mean_post2021_ic=`0.045483` | mean_post2021_ic_ir=`n/a` | mean_post2021_spread=`0.00013056` | mean_post2021_pos_ic_ratio=`0.642857`
- `base_core_7` `combo__equal_weight` | folds=`15` | mean_post2021_ic=`0.031207` | mean_post2021_ic_ir=`n/a` | mean_post2021_spread=`2.693e-05` | mean_post2021_pos_ic_ratio=`0.642857`
- `base_plus_top2_9` best combo: `combo__ic_weight_train` | mean_post2021_ic=`0.072998` | mean_post2021_spread=`0.00031966`
- `base_plus_top2_9` `combo__ic_weight_train` | folds=`15` | mean_post2021_ic=`0.072998` | mean_post2021_ic_ir=`n/a` | mean_post2021_spread=`0.00031966` | mean_post2021_pos_ic_ratio=`0.642857`
- `base_plus_top2_9` `combo__quarterly_plus_annual` | folds=`15` | mean_post2021_ic=`0.003857` | mean_post2021_ic_ir=`n/a` | mean_post2021_spread=`-4.794e-05` | mean_post2021_pos_ic_ratio=`0.571429`
- `base_plus_top2_9` `combo__equal_weight` | folds=`15` | mean_post2021_ic=`-0.001591` | mean_post2021_ic_ir=`n/a` | mean_post2021_spread=`2.1e-06` | mean_post2021_pos_ic_ratio=`0.5`

Outputs:
- [formal_walk_forward_validation_v1_folds.csv](D:\hh\codex\v4\phase_1_fundamental\formal_walk_forward_validation_v1_folds.csv)
- [formal_walk_forward_validation_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\formal_walk_forward_validation_v1_results.csv)