# Momentum Monthly Neutralized Rolling Validation V3

Protocol:
- monthly rebalance = each month first actual trading day
- fold structure = `60m train + 24m validation + 12m review`
- stock pool = prior-20-trading-day average traded amount top 60% intersect prior-20-trading-day average market-cap top 60%
- neutralization = each rebalance date cross-sectionally regress momentum on `log(avg_money_20d_pre_rebalance)` and `log(avg_market_cap_20d_pre_rebalance)`
- factor library keeps neutralized `mom_3_1`, `mom_6_1`, `mom_12_1`, and two 6-1-centered composites
- each fold reselects the active factor only from its own validation window

- fold count: `38`

Selection frequency:
- `mom_12_1_neu`: `19` folds
- `combo_631_balanced_neu`: `9` folds
- `mom_6_1_neu`: `8` folds
- `combo_631_midheavy_neu`: `2` folds

Average selected-factor review results:
- mean_review_ic=`0.025804`
- mean_review_spread=`0.00024649`
- mean_review_positive_ic_ratio=`0.540271`

Per-factor review summary after validation selection:
- `mom_12_1_neu` | folds=`19` | mean_validation_ic=`0.073989` | mean_review_ic=`0.037398` | mean_review_spread=`0.00247678`
- `combo_631_balanced_neu` | folds=`9` | mean_validation_ic=`0.075799` | mean_review_ic=`0.029897` | mean_review_spread=`-0.00216248`
- `mom_6_1_neu` | folds=`8` | mean_validation_ic=`0.04145` | mean_review_ic=`0.007921` | mean_review_spread=`-0.00021964`
- `combo_631_midheavy_neu` | folds=`2` | mean_validation_ic=`0.066637` | mean_review_ic=`-0.03122` | mean_review_spread=`-0.00823632`

Latest folds preview:
- `mom_mneu_fold_034` | validation=`2022-10-10` to `2024-09-02` | review=`2024-10-08` to `2025-09-01` | selected=`mom_12_1_neu` | review_ic=`0.007596` | review_spread=`0.00474317`
- `mom_mneu_fold_035` | validation=`2022-11-01` to `2024-10-08` | review=`2024-11-01` to `2025-10-09` | selected=`mom_12_1_neu` | review_ic=`-0.028129` | review_spread=`0.00048176`
- `mom_mneu_fold_036` | validation=`2022-12-01` to `2024-11-01` | review=`2024-12-02` to `2025-11-03` | selected=`mom_12_1_neu` | review_ic=`-0.043646` | review_spread=`0.00021086`
- `mom_mneu_fold_037` | validation=`2023-01-03` to `2024-12-02` | review=`2025-01-02` to `2025-12-01` | selected=`mom_12_1_neu` | review_ic=`-0.056656` | review_spread=`-0.00330866`
- `mom_mneu_fold_038` | validation=`2023-02-01` to `2025-01-02` | review=`2025-02-05` to `2026-01-05` | selected=`mom_12_1_neu` | review_ic=`-0.062755` | review_spread=`-0.0021639`

Outputs:
- [momentum_monthly_neutralized_rolling_validation_v3_folds.csv](D:\hh\codex\v4\phase_2_momentum\momentum_monthly_neutralized_rolling_validation_v3_folds.csv)
- [momentum_monthly_neutralized_rolling_validation_v3_results.csv](D:\hh\codex\v4\phase_2_momentum\momentum_monthly_neutralized_rolling_validation_v3_results.csv)
