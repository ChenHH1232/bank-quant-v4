# Annual Factor Refresh 5Y2Y1Y Memory Carry V1

Protocol:
- annual refresh anchor = each year's realized May rebalance date
- train window: previous `5` realized May-anchor cycles
- test window: next `2` realized May-anchor cycles
- review window: next `1` realized May-anchor cycle
- baseline factor selection and layer caps stay unchanged
- added memory carry rule:
- only previous-year selected `base_core` factors can be carried
- max carry count per year = `2`
- carry requires current-year train pass, test positive ratio >= `0.5`, and test ic >= `-0.05`
- carry lasts only one annual refresh cycle unless the factor re-enters by the normal rule

- controlled factor universe size: `19`
- fold count: `5`

Fold definitions:
- `memory_01` | train=`2014-05-05` to `2019-05-05` | test=`2019-05-06` to `2021-05-05` | review=`2021-05-06` to `2022-05-05`
- `memory_02` | train=`2015-05-04` to `2020-05-05` | test=`2020-05-06` to `2022-05-04` | review=`2022-05-05` to `2023-05-04`
- `memory_03` | train=`2016-05-03` to `2021-05-05` | test=`2021-05-06` to `2023-05-03` | review=`2023-05-04` to `2024-05-03`
- `memory_04` | train=`2017-05-02` to `2022-05-04` | test=`2022-05-05` to `2024-05-05` | review=`2024-05-06` to `2025-05-05`
- `memory_05` | train=`2018-05-02` to `2023-05-03` | test=`2023-05-04` to `2025-05-05` | review=`2025-05-06` to `2026-05-05`

Annual factor selection counts:
- `memory_01` | kept=`10` / total=`19` | carried=`0`
- `memory_02` | kept=`10` / total=`19` | carried=`0`
- `memory_03` | kept=`5` / total=`19` | carried=`1`
- `memory_04` | kept=`6` / total=`19` | carried=`1`
- `memory_05` | kept=`7` / total=`19` | carried=`0`

Average review-year results by scenario and combo:
- `base_core_7` best combo: `combo__ic_weight_train` | mean_review_ic=`0.082364` | mean_review_spread=`0.00032585` | mean_selected_count=`4.8`
- `base_core_7` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.082364` | mean_review_spread=`0.00032585` | mean_review_pos_ic_ratio=`0.616667` | mean_selected_count=`4.8`
- `base_core_7` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.07847` | mean_review_spread=`0.00030301` | mean_review_pos_ic_ratio=`0.566667` | mean_selected_count=`4.8`
- `base_core_7` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`0.006326` | mean_review_spread=`0.00015487` | mean_review_pos_ic_ratio=`0.566667` | mean_selected_count=`4.8`
- `base_plus_top2_9` best combo: `combo__ic_weight_train` | mean_review_ic=`0.072787` | mean_review_spread=`0.00031187` | mean_selected_count=`6.4`
- `base_plus_top2_9` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.072787` | mean_review_spread=`0.00031187` | mean_review_pos_ic_ratio=`0.616667` | mean_selected_count=`6.4`
- `base_plus_top2_9` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.014978` | mean_review_spread=`0.00015678` | mean_review_pos_ic_ratio=`0.516667` | mean_selected_count=`6.4`
- `base_plus_top2_9` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`-0.033589` | mean_review_spread=`-5.22e-05` | mean_review_pos_ic_ratio=`0.466667` | mean_selected_count=`6.4`

Outputs:
- [annual_factor_refresh_5y2y1y_memory_carry_v1_folds.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_memory_carry_v1_folds.csv)
- [annual_factor_refresh_5y2y1y_memory_carry_v1_factor_selection.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_memory_carry_v1_factor_selection.csv)
- [annual_factor_refresh_5y2y1y_memory_carry_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_memory_carry_v1_results.csv)