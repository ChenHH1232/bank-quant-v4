# Momentum Quarterly Rolling Validation V1

Protocol:
- quarterly rebalance dates inherit the phase-1 fundamental calendar
- fold structure = `5y train + 8q validation + 4q review`
- stock pool keeps prior-20-trading-day amount and market-cap double-top-80% rule
- alpha candidates keep the frozen momentum shortlist led by `mom_12_1`

- fold count: `7`

Average review results by scenario:
- `alpha_only` | folds=`7` | mean_review_ic=`0.240432` | mean_review_spread=`0.02552726`
- `alpha_plus_support` | folds=`7` | mean_review_ic=`0.078094` | mean_review_spread=`0.00894115`

Alpha selection frequency:
- `mom_12_1`: `7` folds

Outputs:
- [momentum_quarterly_rolling_validation_v1_folds.csv](D:\hh\codex\v4\phase_2_momentum\momentum_quarterly_rolling_validation_v1_folds.csv)
- [momentum_quarterly_rolling_validation_v1_results.csv](D:\hh\codex\v4\phase_2_momentum\momentum_quarterly_rolling_validation_v1_results.csv)
