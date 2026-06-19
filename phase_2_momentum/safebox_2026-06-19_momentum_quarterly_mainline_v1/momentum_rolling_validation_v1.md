# Momentum Rolling Validation V1

Protocol:
- annual anchor = each year's realized first May trading day
- fold structure = `5y train + 2y validation + 1y review`
- stock pool = prior-20-trading-day average traded amount top 80% intersect prior-20-trading-day average market-cap top 80%
- candidate shortlist frozen from `momentum_candidate_pool_draft_v1.md`
- factor choice is reselected inside each fold using the 2-year validation window only

- fold count: `5`

Fold definitions:
- `mom_fold_01` | train=`2014-05-05` to `2018-05-02` | validation=`2019-05-06` to `2020-05-06` | review=`2021-05-06`
- `mom_fold_02` | train=`2015-05-04` to `2019-05-06` | validation=`2020-05-06` to `2021-05-06` | review=`2022-05-05`
- `mom_fold_03` | train=`2016-05-03` to `2020-05-06` | validation=`2021-05-06` to `2022-05-05` | review=`2023-05-04`
- `mom_fold_04` | train=`2017-05-02` to `2021-05-06` | validation=`2022-05-05` to `2023-05-04` | review=`2024-05-06`
- `mom_fold_05` | train=`2018-05-02` to `2022-05-05` | validation=`2023-05-04` to `2024-05-06` | review=`2025-05-06`

Average review results by scenario:
- `alpha_only` | folds=`5` | mean_review_ic=`0.275902` | mean_review_spread=`0.07584357`
- `alpha_plus_support` | folds=`3` | mean_review_ic=`-0.044827` | mean_review_spread=`0.00126072`

Per-fold selections:
- `mom_fold_01` | alpha=`mom_12_1` | support=`liq_money_1m` | best_scenario=`alpha_plus_support` | review_ic=`0.06798` | review_spread=`0.0625134`
- `mom_fold_02` | alpha=`mom_12_1` | support=`liq_money_1m` | best_scenario=`alpha_only` | review_ic=`0.295043` | review_spread=`0.03193369`
- `mom_fold_03` | alpha=`mom_12_1` | support=`none` | best_scenario=`alpha_only` | review_ic=`0.422551` | review_spread=`0.11678181`
- `mom_fold_04` | alpha=`mom_12_1` | support=`none` | best_scenario=`alpha_only` | review_ic=`0.528869` | review_spread=`0.21770495`
- `mom_fold_05` | alpha=`mom_12_1` | support=`liq_money_1m` | best_scenario=`alpha_only` | review_ic=`` | review_spread=``

Outputs:
- [momentum_rolling_validation_v1_folds.csv](D:\hh\codex\v4\phase_2_momentum\momentum_rolling_validation_v1_folds.csv)
- [momentum_rolling_validation_v1_results.csv](D:\hh\codex\v4\phase_2_momentum\momentum_rolling_validation_v1_results.csv)
