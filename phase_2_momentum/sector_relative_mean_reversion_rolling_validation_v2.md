# Sector Relative Mean Reversion Rolling Validation V2

Purpose:
- replace the equal-weight bank proxy with a real tradeable sector ETF proxy
- sector ETF proxy = `sh512800`
- test whether stock-versus-ETF relative underperformance is a better mean reversion anchor than raw stock-only pullback

Frozen setup:
- fold count: `38` monthly rolling folds
- ETF history start: `2017-08-03`
- ETF history end: `2026-06-22`
- target: next-month return `y_month_total_return_close`
- factor set: `rel_etf_rev_5d, rel_etf_rev_10d, rel_etf_rev_20d`

Validation and review summary:
- `rel_etf_rev_20d` `review` | folds=`38` | mean_rank_ic=`0.069258` | mean_rank_ic_ir=`0.249502` | mean_positive_ic_ratio=`0.551037` | mean_top_minus_bottom=`0.010248` | mean_missing_ratio=`0.000000`
- `rel_etf_rev_5d` `review` | folds=`38` | mean_rank_ic=`-0.008378` | mean_rank_ic_ir=`-0.055787` | mean_positive_ic_ratio=`0.438597` | mean_top_minus_bottom=`-0.002172` | mean_missing_ratio=`0.000000`
- `rel_etf_rev_10d` `review` | folds=`38` | mean_rank_ic=`-0.035873` | mean_rank_ic_ir=`-0.162693` | mean_positive_ic_ratio=`0.442983` | mean_top_minus_bottom=`-0.002342` | mean_missing_ratio=`0.000000`
- `rel_etf_rev_10d` `validation` | folds=`38` | mean_rank_ic=`0.009824` | mean_rank_ic_ir=`0.053673` | mean_positive_ic_ratio=`0.531798` | mean_top_minus_bottom=`0.003933` | mean_missing_ratio=`0.000000`
- `rel_etf_rev_5d` `validation` | folds=`38` | mean_rank_ic=`-0.014083` | mean_rank_ic_ir=`-0.064158` | mean_positive_ic_ratio=`0.446272` | mean_top_minus_bottom=`-0.002959` | mean_missing_ratio=`0.000000`
- `rel_etf_rev_20d` `validation` | folds=`38` | mean_rank_ic=`-0.049922` | mean_rank_ic_ir=`-0.163019` | mean_positive_ic_ratio=`0.430921` | mean_top_minus_bottom=`-0.005140` | mean_missing_ratio=`0.000000`

Current best ETF-relative candidate:
- `rel_etf_rev_20d` | review mean_rank_ic=`0.069258` | review mean_top_minus_bottom=`0.010248`

Outputs:
- [sector_relative_mean_reversion_rolling_validation_v2_results.csv](D:\hh\codex\v4\phase_2_momentum\sector_relative_mean_reversion_rolling_validation_v2_results.csv)
- ETF cache: [benchmark_512800_sina_daily.csv](D:\hh\codex\v4\phase_2_momentum\raw_downloads\benchmark_512800_sina_daily.csv)
