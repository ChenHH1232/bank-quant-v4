# Balanced Core-Level Shortbond Overlay Rolling Validation V1

Protocol:
- pure-fundamental base variants = `balanced` and `core_level_shadow`
- annual shell fixed at `5y/2y/1y + combo__ic_weight_train + top_08`
- defensive overlay fixed at `shortbond_6040_4055`
- warning threshold = `40%`
- severe threshold = `55%`
- warning equity weight = `60%`
- severe equity weight = `40%`
- defensive asset = `short_bond_etf_511260`

Variant summary:
- `balanced` `pure_fundamental` | folds=`5` | mean_train_cum=`0.603109` | mean_test_cum=`0.269435` | mean_review_cum=`0.065544` | mean_review_equity_weight=`1.000000` | mean_review_signal=`n/a`
- `balanced` `shortbond_6040_4055` | folds=`5` | mean_train_cum=`0.297702` | mean_test_cum=`0.278743` | mean_review_cum=`0.069259` | mean_review_equity_weight=`0.973333` | mean_review_signal=`0.120931`
- `core_level_shadow` `pure_fundamental` | folds=`5` | mean_train_cum=`0.612214` | mean_test_cum=`0.283983` | mean_review_cum=`0.078288` | mean_review_equity_weight=`1.000000` | mean_review_signal=`n/a`
- `core_level_shadow` `shortbond_6040_4055` | folds=`5` | mean_train_cum=`0.303646` | mean_test_cum=`0.291426` | mean_review_cum=`0.082135` | mean_review_equity_weight=`0.973333` | mean_review_signal=`0.120931`

Overlay delta versus pure branch:
- `balanced` | delta_train=`-0.305408` | delta_test=`0.009308` | delta_review=`0.003716` | pure_review=`0.065544` | overlay_review=`0.069259`
- `core_level_shadow` | delta_train=`-0.308568` | delta_test=`0.007443` | delta_review=`0.003847` | pure_review=`0.078288` | overlay_review=`0.082135`

Best overlay branch by mean review cumulative return:
- `core_level_shadow` `shortbond_6040_4055` | overlay_review=`0.082135` | delta_review=`0.003847`

Outputs:
- [balanced_corelevel_shortbond_overlay_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\balanced_corelevel_shortbond_overlay_rolling_validation_v1_config_results.csv)
