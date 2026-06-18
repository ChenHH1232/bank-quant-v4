# Annual Factor Refresh 5Y2Y1Y V1

Protocol:
- annual refresh anchor = each year's realized May rebalance date, not a hard-coded `May 1` calendar boundary
- train window: previous `5` realized May-anchor cycles
- test window: next `2` realized May-anchor cycles
- review window: next `1` realized May-anchor cycle
- factor selection is refreshed once per year, then frozen for the whole review year
- keep rule: train_ic>`0.0`, test_ic>`0.0`, test_positive_ic_ratio>=`0.5`
- structure rule: keep only if test_top_minus_bottom>=`0.0` or test_ic>=`0.05`
- layer caps: base_core min/max=`4/7`, improvement max=`2`, watch max=`2`

- controlled factor universe size: `19`
- fold count: `5`

Fold definitions:
- `annual_01` | train=`2014-05-05` to `2019-05-05` | test=`2019-05-06` to `2021-05-05` | review=`2021-05-06` to `2022-05-05`
- `annual_02` | train=`2015-05-04` to `2020-05-05` | test=`2020-05-06` to `2022-05-04` | review=`2022-05-05` to `2023-05-04`
- `annual_03` | train=`2016-05-03` to `2021-05-05` | test=`2021-05-06` to `2023-05-03` | review=`2023-05-04` to `2024-05-03`
- `annual_04` | train=`2017-05-02` to `2022-05-04` | test=`2022-05-05` to `2024-05-05` | review=`2024-05-06` to `2025-05-05`
- `annual_05` | train=`2018-05-02` to `2023-05-03` | test=`2023-05-04` to `2025-05-05` | review=`2025-05-06` to `2026-05-05`

Annual factor selection counts:
- `annual_01` | kept=`10` / total=`19`
- `annual_02` | kept=`10` / total=`19`
- `annual_03` | kept=`4` / total=`19`
- `annual_04` | kept=`5` / total=`19`
- `annual_05` | kept=`7` / total=`19`

Average review-year results by scenario and combo:
- `base_core_7` best combo: `combo__ic_weight_train` | mean_review_ic=`0.095899` | mean_review_spread=`0.0003133` | mean_selected_count=`4.4`
- `base_core_7` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.095899` | mean_review_spread=`0.0003133` | mean_review_pos_ic_ratio=`0.683333` | mean_selected_count=`4.4`
- `base_core_7` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.080306` | mean_review_spread=`0.00028482` | mean_review_pos_ic_ratio=`0.633333` | mean_selected_count=`4.4`
- `base_core_7` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`0.00121` | mean_review_spread=`0.00010659` | mean_review_pos_ic_ratio=`0.5` | mean_selected_count=`4.4`
- `base_plus_top2_9` best combo: `combo__ic_weight_train` | mean_review_ic=`0.086609` | mean_review_spread=`0.00031724` | mean_selected_count=`6.0`
- `base_plus_top2_9` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.086609` | mean_review_spread=`0.00031724` | mean_review_pos_ic_ratio=`0.683333` | mean_selected_count=`6.0`
- `base_plus_top2_9` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.020562` | mean_review_spread=`0.00012015` | mean_review_pos_ic_ratio=`0.583333` | mean_selected_count=`6.0`
- `base_plus_top2_9` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`-0.042399` | mean_review_spread=`-7.242e-05` | mean_review_pos_ic_ratio=`0.4` | mean_selected_count=`6.0`

Outputs:
- [annual_factor_refresh_5y2y1y_v1_folds.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1_folds.csv)
- [annual_factor_refresh_5y2y1y_v1_factor_selection.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1_factor_selection.csv)
- [annual_factor_refresh_5y2y1y_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1_results.csv)