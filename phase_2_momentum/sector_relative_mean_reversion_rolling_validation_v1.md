# Sector Relative Mean Reversion Rolling Validation V1

Purpose:
- test whether stock-versus-sector relative underperformance is a better mean reversion anchor than raw stock-only pullback
- sector proxy in this first pass = equal-weight bank-universe average return on each rebalance date
- this is a local proxy study, not yet a real JoinQuant sector-index execution study

Frozen setup:
- fold count: `38` monthly rolling folds
- target: next-month return `y_month_total_return_close`
- factor set: `rel_sector_rev_5d, rel_sector_rev_10d, rel_sector_rev_20d`

Validation and review summary:
- `rel_sector_rev_20d` `review` | folds=`38` | mean_rank_ic=`0.066455` | mean_rank_ic_ir=`0.253298` | mean_positive_ic_ratio=`0.633772` | mean_top_minus_bottom=`0.004269` | mean_usable_dates=`12.00`
- `rel_sector_rev_5d` `review` | folds=`38` | mean_rank_ic=`-0.008320` | mean_rank_ic_ir=`-0.055550` | mean_positive_ic_ratio=`0.438597` | mean_top_minus_bottom=`-0.002172` | mean_usable_dates=`12.00`
- `rel_sector_rev_10d` `review` | folds=`38` | mean_rank_ic=`-0.018947` | mean_rank_ic_ir=`-0.098217` | mean_positive_ic_ratio=`0.491228` | mean_top_minus_bottom=`-0.002912` | mean_usable_dates=`12.00`
- `rel_sector_rev_5d` `validation` | folds=`38` | mean_rank_ic=`-0.013978` | mean_rank_ic_ir=`-0.063684` | mean_positive_ic_ratio=`0.446272` | mean_top_minus_bottom=`-0.002959` | mean_usable_dates=`24.00`
- `rel_sector_rev_10d` `validation` | folds=`38` | mean_rank_ic=`-0.036445` | mean_rank_ic_ir=`-0.151921` | mean_positive_ic_ratio=`0.422149` | mean_top_minus_bottom=`-0.004056` | mean_usable_dates=`24.00`
- `rel_sector_rev_20d` `validation` | folds=`38` | mean_rank_ic=`-0.042401` | mean_rank_ic_ir=`-0.145438` | mean_positive_ic_ratio=`0.459430` | mean_top_minus_bottom=`-0.006625` | mean_usable_dates=`24.00`

Current best first-pass candidate:
- `rel_sector_rev_20d` | review mean_rank_ic=`0.066455` | review mean_top_minus_bottom=`0.004269`

Output:
- [sector_relative_mean_reversion_rolling_validation_v1_results.csv](D:\hh\codex\v4\phase_2_momentum\sector_relative_mean_reversion_rolling_validation_v1_results.csv)
