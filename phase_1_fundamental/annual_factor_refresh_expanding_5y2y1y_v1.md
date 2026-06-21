# Annual Factor Refresh Expanding 5Y2Y1Y V1

Protocol:
- annual refresh anchor = each year's realized May rebalance date, not a hard-coded `May 1` calendar boundary
- initial train window: first `5` realized May-anchor cycles
- expanding rule: after the first usable fold, the train start stays fixed and the train end moves forward by one realized May-anchor cycle each year
- test window: next `2` realized May-anchor cycles
- review window: next `1` realized May-anchor cycle
- factor selection is refreshed once per year, then frozen for the whole review year
- layer caps: base_core min/max=`4/7`, improvement max=`2`, watch max=`2`

- controlled factor universe size: `19`
- fold count: `5`

Fold definitions:
- `expanding_01` | train=`2014-05-05` to `2019-05-05` | test=`2019-05-06` to `2021-05-05` | review=`2021-05-06` to `2022-05-05` | train_anchor_years=`5`
- `expanding_02` | train=`2014-05-05` to `2020-05-05` | test=`2020-05-06` to `2022-05-04` | review=`2022-05-05` to `2023-05-04` | train_anchor_years=`6`
- `expanding_03` | train=`2014-05-05` to `2021-05-05` | test=`2021-05-06` to `2023-05-03` | review=`2023-05-04` to `2024-05-03` | train_anchor_years=`7`
- `expanding_04` | train=`2014-05-05` to `2022-05-04` | test=`2022-05-05` to `2024-05-05` | review=`2024-05-06` to `2025-05-05` | train_anchor_years=`8`
- `expanding_05` | train=`2014-05-05` to `2023-05-03` | test=`2023-05-04` to `2025-05-05` | review=`2025-05-06` to `2026-05-05` | train_anchor_years=`9`

Annual factor selection counts:
- `expanding_01` | train_anchor_years=`5` | kept=`10` / total=`19`
- `expanding_02` | train_anchor_years=`6` | kept=`10` / total=`19`
- `expanding_03` | train_anchor_years=`7` | kept=`5` / total=`19`
- `expanding_04` | train_anchor_years=`8` | kept=`6` / total=`19`
- `expanding_05` | train_anchor_years=`9` | kept=`8` / total=`19`

Average review-year results by scenario and combo:
- `base_core_7` best combo: `combo__equal_weight` | mean_review_ic=`0.082085` | mean_review_spread=`0.00030499` | mean_selected_count=`4.4` | mean_train_anchor_years=`7.0`
- `base_core_7` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.082085` | mean_review_spread=`0.00030499` | mean_review_pos_ic_ratio=`0.633333` | mean_selected_count=`4.4` | mean_train_anchor_years=`7.0`
- `base_core_7` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.077411` | mean_review_spread=`0.00025789` | mean_review_pos_ic_ratio=`0.566667` | mean_selected_count=`4.4` | mean_train_anchor_years=`7.0`
- `base_core_7` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`-1.1e-05` | mean_review_spread=`0.00010787` | mean_review_pos_ic_ratio=`0.4` | mean_selected_count=`4.4` | mean_train_anchor_years=`7.0`
- `base_plus_top2_9` best combo: `combo__ic_weight_train` | mean_review_ic=`0.066244` | mean_review_spread=`0.00022376` | mean_selected_count=`6.0` | mean_train_anchor_years=`7.0`
- `base_plus_top2_9` `combo__ic_weight_train` | folds=`5` | mean_review_ic=`0.066244` | mean_review_spread=`0.00022376` | mean_review_pos_ic_ratio=`0.566667` | mean_selected_count=`6.0` | mean_train_anchor_years=`7.0`
- `base_plus_top2_9` `combo__equal_weight` | folds=`5` | mean_review_ic=`0.029108` | mean_review_spread=`8.256e-05` | mean_review_pos_ic_ratio=`0.583333` | mean_selected_count=`6.0` | mean_train_anchor_years=`7.0`
- `base_plus_top2_9` `combo__quarterly_plus_annual` | folds=`5` | mean_review_ic=`-0.042971` | mean_review_spread=`-6.078e-05` | mean_review_pos_ic_ratio=`0.35` | mean_selected_count=`6.0` | mean_train_anchor_years=`7.0`

Outputs:
- [annual_factor_refresh_expanding_5y2y1y_v1_folds.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_expanding_5y2y1y_v1_folds.csv)
- [annual_factor_refresh_expanding_5y2y1y_v1_factor_selection.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_expanding_5y2y1y_v1_factor_selection.csv)
- [annual_factor_refresh_expanding_5y2y1y_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_expanding_5y2y1y_v1_results.csv)