# Momentum Monthly Rolling Validation V2

Protocol:
- monthly rebalance = each month first actual trading day
- fold structure = `60m train + 24m validation + 12m review`
- stock pool = prior-20-trading-day average traded amount top 60% intersect prior-20-trading-day average market-cap top 60%
- factor library keeps `mom_3_1`, `mom_6_1`, `mom_12_1`, and two 6-1-centered composites
- each fold reselects the active factor only from its own validation window

- fold count: `38`

Selection frequency:
- `mom_6_1`: `19` folds
- `mom_12_1`: `17` folds
- `mom_3_1`: `2` folds

Average selected-factor review results:
- mean_review_ic=`0.010038`
- mean_review_spread=`-0.00387767`
- mean_review_positive_ic_ratio=`0.492026`

Per-factor review summary after validation selection:
- `mom_6_1` | folds=`19` | mean_validation_ic=`0.052381` | mean_review_ic=`0.010624` | mean_review_spread=`-0.00245087`
- `mom_12_1` | folds=`17` | mean_validation_ic=`0.108677` | mean_review_ic=`0.031602` | mean_review_spread=`-0.00186834`
- `mom_3_1` | folds=`2` | mean_validation_ic=`0.024491` | mean_review_ic=`-0.178809` | mean_review_spread=`-0.03451162`

Latest folds preview:
- `mom_mfold_034` | validation=`2022-10-10` to `2024-09-02` | review=`2024-10-08` to `2025-09-01` | selected=`mom_12_1` | review_ic=`0.012555` | review_spread=`0.00361094`
- `mom_mfold_035` | validation=`2022-11-01` to `2024-10-08` | review=`2024-11-01` to `2025-10-09` | selected=`mom_12_1` | review_ic=`-0.018315` | review_spread=`0.0004123`
- `mom_mfold_036` | validation=`2022-12-01` to `2024-11-01` | review=`2024-12-02` to `2025-11-03` | selected=`mom_12_1` | review_ic=`-0.05233` | review_spread=`-0.00187923`
- `mom_mfold_037` | validation=`2023-01-03` to `2024-12-02` | review=`2025-01-02` to `2025-12-01` | selected=`mom_12_1` | review_ic=`-0.057353` | review_spread=`-0.00465064`
- `mom_mfold_038` | validation=`2023-02-01` to `2025-01-02` | review=`2025-02-05` to `2026-01-05` | selected=`mom_12_1` | review_ic=`-0.068337` | review_spread=`-0.00619244`

Outputs:
- [momentum_monthly_rolling_validation_v2_folds.csv](D:\hh\codex\v4\phase_2_momentum\momentum_monthly_rolling_validation_v2_folds.csv)
- [momentum_monthly_rolling_validation_v2_results.csv](D:\hh\codex\v4\phase_2_momentum\momentum_monthly_rolling_validation_v2_results.csv)
