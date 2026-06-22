# Sector Relative Mean Reversion Rolling Validation V4

Purpose:
- test zscore and lower-bollinger deviation on stock-vs-ETF price ratio
- sector ETF proxy = `sh512800`
- ratio definition = `stock close / ETF close`
- bollinger setup = rolling mean +/- `2.0` * rolling std

Frozen setup:
- fold count: `38` monthly rolling folds
- ETF history start: `2017-08-03`
- ETF history end: `2026-06-22`
- target: next-month return `y_month_total_return_close`
- factor set: `ratio_z_10d, ratio_z_20d, ratio_z_40d, ratio_below_lower_10d, ratio_below_lower_20d, ratio_below_lower_40d`

Validation and review summary:
- `ratio_below_lower_10d` `review` | folds=`38` | mean_rank_ic=`0.001746` | mean_rank_ic_ir=`-0.052969` | mean_positive_ic_ratio=`0.462148` | mean_top_minus_bottom=`-0.009633` | mean_missing_ratio=`0.000382`
- `ratio_z_40d` `review` | folds=`38` | mean_rank_ic=`-0.007429` | mean_rank_ic_ir=`-0.016593` | mean_positive_ic_ratio=`0.456140` | mean_top_minus_bottom=`-0.000136` | mean_missing_ratio=`0.004325`
- `ratio_z_10d` `review` | folds=`38` | mean_rank_ic=`-0.008478` | mean_rank_ic_ir=`-0.045903` | mean_positive_ic_ratio=`0.471491` | mean_top_minus_bottom=`0.000505` | mean_missing_ratio=`0.000382`
- `ratio_below_lower_40d` `review` | folds=`38` | mean_rank_ic=`-0.020846` | mean_rank_ic_ir=`-0.120689` | mean_positive_ic_ratio=`0.443228` | mean_top_minus_bottom=`-0.008321` | mean_missing_ratio=`0.004325`
- `ratio_z_20d` `review` | folds=`38` | mean_rank_ic=`-0.022759` | mean_rank_ic_ir=`-0.071571` | mean_positive_ic_ratio=`0.449561` | mean_top_minus_bottom=`-0.001749` | mean_missing_ratio=`0.002057`
- `ratio_below_lower_20d` `review` | folds=`38` | mean_rank_ic=`-0.026197` | mean_rank_ic_ir=`-0.162233` | mean_positive_ic_ratio=`0.464746` | mean_top_minus_bottom=`-0.009793` | mean_missing_ratio=`0.002057`
- `ratio_z_40d` `validation` | folds=`38` | mean_rank_ic=`0.019353` | mean_rank_ic_ir=`0.069580` | mean_positive_ic_ratio=`0.508772` | mean_top_minus_bottom=`0.001181` | mean_missing_ratio=`0.011244`
- `ratio_below_lower_40d` `validation` | folds=`38` | mean_rank_ic=`0.004873` | mean_rank_ic_ir=`0.025461` | mean_positive_ic_ratio=`0.499558` | mean_top_minus_bottom=`-0.007512` | mean_missing_ratio=`0.011244`
- `ratio_z_20d` `validation` | folds=`38` | mean_rank_ic=`-0.000592` | mean_rank_ic_ir=`0.012227` | mean_positive_ic_ratio=`0.462719` | mean_top_minus_bottom=`0.003487` | mean_missing_ratio=`0.005324`
- `ratio_z_10d` `validation` | folds=`38` | mean_rank_ic=`-0.012912` | mean_rank_ic_ir=`-0.051415` | mean_positive_ic_ratio=`0.457237` | mean_top_minus_bottom=`0.000275` | mean_missing_ratio=`0.002445`
- `ratio_below_lower_20d` `validation` | folds=`38` | mean_rank_ic=`-0.021655` | mean_rank_ic_ir=`-0.126517` | mean_positive_ic_ratio=`0.505103` | mean_top_minus_bottom=`-0.009665` | mean_missing_ratio=`0.005324`
- `ratio_below_lower_10d` `validation` | folds=`38` | mean_rank_ic=`-0.024847` | mean_rank_ic_ir=`-0.137150` | mean_positive_ic_ratio=`0.409057` | mean_top_minus_bottom=`-0.007363` | mean_missing_ratio=`0.002445`

Current best zscore/bollinger candidate:
- `ratio_below_lower_10d` | review mean_rank_ic=`0.001746` | review mean_top_minus_bottom=`-0.009633`

Outputs:
- [sector_relative_mean_reversion_rolling_validation_v4_results.csv](D:\hh\codex\v4\phase_2_momentum\sector_relative_mean_reversion_rolling_validation_v4_results.csv)
- ETF cache: [benchmark_512800_sina_daily.csv](D:\hh\codex\v4\phase_2_momentum\raw_downloads\benchmark_512800_sina_daily.csv)
