# Sector Relative Mean Reversion Rolling Validation V3

Purpose:
- keep the same monthly rolling framework, but replace return-difference with price-ratio mean reversion
- sector ETF proxy = `sh512800`
- ratio definition = `stock close / ETF close` on each daily date
- factor definition = `ratio / rolling_mean(ratio, N) - 1`

Frozen setup:
- fold count: `38` monthly rolling folds
- ETF history start: `2017-08-03`
- ETF history end: `2026-06-22`
- target: next-month return `y_month_total_return_close`
- factor set: `ratio_to_ma_5d, ratio_to_ma_10d, ratio_to_ma_20d`

Validation and review summary:
- `ratio_to_ma_5d` `review` | folds=`38` | mean_rank_ic=`0.019830` | mean_rank_ic_ir=`0.033697` | mean_positive_ic_ratio=`0.447368` | mean_top_minus_bottom=`0.001490` | mean_missing_ratio=`0.000000`
- `ratio_to_ma_10d` `review` | folds=`38` | mean_rank_ic=`-0.011444` | mean_rank_ic_ir=`-0.058092` | mean_positive_ic_ratio=`0.500000` | mean_top_minus_bottom=`-0.000718` | mean_missing_ratio=`0.000382`
- `ratio_to_ma_20d` `review` | folds=`38` | mean_rank_ic=`-0.022168` | mean_rank_ic_ir=`-0.090520` | mean_positive_ic_ratio=`0.449561` | mean_top_minus_bottom=`-0.001442` | mean_missing_ratio=`0.002057`
- `ratio_to_ma_20d` `validation` | folds=`38` | mean_rank_ic=`0.005608` | mean_rank_ic_ir=`0.032814` | mean_positive_ic_ratio=`0.494518` | mean_top_minus_bottom=`0.004535` | mean_missing_ratio=`0.005324`
- `ratio_to_ma_10d` `validation` | folds=`38` | mean_rank_ic=`-0.001276` | mean_rank_ic_ir=`-0.001698` | mean_positive_ic_ratio=`0.532895` | mean_top_minus_bottom=`0.003028` | mean_missing_ratio=`0.002445`
- `ratio_to_ma_5d` `validation` | folds=`38` | mean_rank_ic=`-0.014123` | mean_rank_ic_ir=`-0.066850` | mean_positive_ic_ratio=`0.432018` | mean_top_minus_bottom=`-0.001469` | mean_missing_ratio=`0.000250`

Current best ratio-mean candidate:
- `ratio_to_ma_5d` | review mean_rank_ic=`0.019830` | review mean_top_minus_bottom=`0.001490`

Outputs:
- [sector_relative_mean_reversion_rolling_validation_v3_results.csv](D:\hh\codex\v4\phase_2_momentum\sector_relative_mean_reversion_rolling_validation_v3_results.csv)
- ETF cache: [benchmark_512800_sina_daily.csv](D:\hh\codex\v4\phase_2_momentum\raw_downloads\benchmark_512800_sina_daily.csv)
