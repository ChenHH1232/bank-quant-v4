# Pure Fundamental Execution Rolling Validation V1

Protocol:
- factor engine stays fixed at annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- this branch changes only execution-layer parameters
- stock selection uses direct score ranking instead of changing factor definitions
- tested hold counts = `8 / 10 / 12`
- tested entry delays = `0 / 5` trading days after each rebalance date
- capital not yet deployed during delay stays in cash with `0` return

Baseline config: `pf_exec__top_08__delay_00`

Chosen fold results:
- `annual_01` | status=`chosen_best_available` | config=`pf_exec__top_10__delay_00` | hold_count=`10` | entry_delay_days=`0` | train_cum=`1.299483` | test_cum=`0.200290` | review_cum=`-0.049364` | review_mean_cash=`0.001639` | review_mean_invested_stock_count=`10.000000`
- `annual_02` | status=`chosen_best_available` | config=`pf_exec__top_08__delay_05` | hold_count=`8` | entry_delay_days=`5` | train_cum=`0.242071` | test_cum=`0.230449` | review_cum=`0.082517` | review_mean_cash=`0.000000` | review_mean_invested_stock_count=`8.000000`
- `annual_03` | status=`chosen_best_available` | config=`pf_exec__top_10__delay_05` | hold_count=`10` | entry_delay_days=`5` | train_cum=`0.587199` | test_cum=`0.086908` | review_cum=`-0.014378` | review_mean_cash=`0.000000` | review_mean_invested_stock_count=`10.000000`
- `annual_04` | status=`chosen_best_available` | config=`pf_exec__top_08__delay_05` | hold_count=`8` | entry_delay_days=`5` | train_cum=`0.494518` | test_cum=`0.258588` | review_cum=`0.214116` | review_mean_cash=`0.000000` | review_mean_invested_stock_count=`8.000000`
- `annual_05` | status=`chosen_best_available` | config=`pf_exec__top_10__delay_05` | hold_count=`10` | entry_delay_days=`5` | train_cum=`0.289924` | test_cum=`0.475295` | review_cum=`0.069565` | review_mean_cash=`0.000000` | review_mean_invested_stock_count=`10.000000`

Mean config ranking:
- `pf_exec__top_08__delay_05` | folds=`5` | mean_train_cum=`0.615317` | mean_test_cum=`0.249923` | mean_review_cum=`0.072654` | mean_review_cash=`0.000427`
- `pf_exec__top_10__delay_05` | folds=`5` | mean_train_cum=`0.515059` | mean_test_cum=`0.217385` | mean_review_cum=`0.060721` | mean_review_cash=`0.000342`
- `pf_exec__top_10__delay_00` | folds=`5` | mean_train_cum=`0.547211` | mean_test_cum=`0.216128` | mean_review_cum=`0.062214` | mean_review_cash=`0.000328`
- `pf_exec__top_12__delay_05` | folds=`5` | mean_train_cum=`0.478249` | mean_test_cum=`0.203985` | mean_review_cum=`0.052707` | mean_review_cash=`0.000285`
- `pf_exec__top_12__delay_00` | folds=`5` | mean_train_cum=`0.511669` | mean_test_cum=`0.201382` | mean_review_cum=`0.056345` | mean_review_cash=`0.000273`

Baseline means:
- mean_train_cum=`0.650664`
- mean_test_cum=`0.259277`
- mean_review_cum=`0.069055`

Outputs:
- [pure_fundamental_execution_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\pure_fundamental_execution_rolling_validation_v1_config_results.csv)
- [pure_fundamental_execution_rolling_validation_v1_chosen.csv](D:\hh\codex\v4\phase_1_fundamental\pure_fundamental_execution_rolling_validation_v1_chosen.csv)
