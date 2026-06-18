# Annual Factor Refresh 5Y2Y1Y V1

Protocol:
- annual refresh anchor = each year's realized May rebalance date, not a hard-coded `May 1` calendar boundary
- train window: previous `5` realized May-anchor cycles
- test window: next `2` realized May-anchor cycles
- review window: next `1` realized May-anchor cycle
- factor selection is refreshed once per year, then frozen for the whole review year

- controlled factor universe size: `15`
- fold count: `5`

Fold definitions:
- `annual_01` | train=`2014-05-05` to `2019-05-05` | test=`2019-05-06` to `2021-05-05` | review=`2021-05-06` to `2022-05-05`
- `annual_02` | train=`2015-05-04` to `2020-05-05` | test=`2020-05-06` to `2022-05-04` | review=`2022-05-05` to `2023-05-04`
- `annual_03` | train=`2016-05-03` to `2021-05-05` | test=`2021-05-06` to `2023-05-03` | review=`2023-05-04` to `2024-05-03`
- `annual_04` | train=`2017-05-02` to `2022-05-04` | test=`2022-05-05` to `2024-05-05` | review=`2024-05-06` to `2025-05-05`
- `annual_05` | train=`2018-05-02` to `2023-05-03` | test=`2023-05-04` to `2025-05-05` | review=`2025-05-06` to `2026-05-05`

Annual factor selection counts:
- `annual_01` | kept=`11` / total=`15`
- `annual_02` | kept=`12` / total=`15`
- `annual_03` | kept=`4` / total=`15`
- `annual_04` | kept=`4` / total=`15`
- `annual_05` | kept=`6` / total=`15`

Average review-year results by scenario and combo:
- `base_core_7` best combo: `combo__ic_weight_train` | mean_review_ic=`0.098478` | mean_review_spread=`0.00034416` | mean_selected_count=`4.6`
- `base_core_7` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.098478` | mean_review_spread=`0.00034416` | mean_review_pos_ic_ratio=`0.683333` | mean_selected_count=`4.6`
- `base_core_7` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.077927` | mean_review_spread=`0.00028152` | mean_review_pos_ic_ratio=`0.633333` | mean_selected_count=`4.6`
- `base_core_7` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`0.025888` | mean_review_spread=`0.00015538` | mean_review_pos_ic_ratio=`0.55` | mean_selected_count=`4.6`
- `base_plus_top2_9` best combo: `combo__ic_weight_train` | mean_review_ic=`0.109494` | mean_review_spread=`0.00037846` | mean_selected_count=`5.6`
- `base_plus_top2_9` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.109494` | mean_review_spread=`0.00037846` | mean_review_pos_ic_ratio=`0.683333` | mean_selected_count=`5.6`
- `base_plus_top2_9` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.062122` | mean_review_spread=`0.00018162` | mean_review_pos_ic_ratio=`0.633333` | mean_selected_count=`5.6`
- `base_plus_top2_9` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`0.002545` | mean_review_spread=`0.00012966` | mean_review_pos_ic_ratio=`0.45` | mean_selected_count=`5.6`

Outputs:
- [annual_factor_refresh_5y2y1y_v1_folds.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1_folds.csv)
- [annual_factor_refresh_5y2y1y_v1_factor_selection.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1_factor_selection.csv)
- [annual_factor_refresh_5y2y1y_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1_results.csv)