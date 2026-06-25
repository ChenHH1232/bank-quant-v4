# Pure Fundamental Execution Staggered Rolling Validation V1

Protocol:
- factor engine stays fixed at annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- this branch changes only execution-layer parameters
- stock selection uses fixed `top 8` ranked names from the same pure-fundamental score
- tested immediate allocation = `100% / 70% / 50%`
- tested second-tranche delay = `0 / 3 / 5` trading days
- capital not yet deployed during the stagger window stays in cash with `0` return

Baseline config: `pf_stagger__top_08__imm_100__delay_00`

Chosen fold results:
- `annual_01` | status=`chosen_best_available` | config=`pf_stagger__top_08__imm_070__delay_03` | hold_count=`8` | immediate_weight=`0.7` | delay_days=`3` | train_cum=`1.367974` | test_cum=`0.250282` | review_cum=`-0.027429` | review_mean_cash=`0.016456` | review_mean_invested_stock_count=`8.000000`
- `annual_02` | status=`chosen_overlay` | config=`pf_stagger__top_08__imm_050__delay_03` | hold_count=`8` | immediate_weight=`0.5` | delay_days=`3` | train_cum=`0.329165` | test_cum=`0.269128` | review_cum=`0.059828` | review_mean_cash=`0.023564` | review_mean_invested_stock_count=`8.000000`
- `annual_03` | status=`chosen_overlay` | config=`pf_stagger__top_08__imm_050__delay_05` | hold_count=`8` | immediate_weight=`0.5` | delay_days=`5` | train_cum=`0.753644` | test_cum=`0.077039` | review_cum=`-0.004885` | review_mean_cash=`0.048665` | review_mean_invested_stock_count=`8.000000`
- `annual_04` | status=`chosen_best_available` | config=`pf_stagger__top_08__imm_050__delay_05` | hold_count=`8` | immediate_weight=`0.5` | delay_days=`5` | train_cum=`0.518844` | test_cum=`0.254744` | review_cum=`0.198198` | review_mean_cash=`0.048665` | review_mean_invested_stock_count=`8.000000`
- `annual_05` | status=`chosen_overlay` | config=`pf_stagger__top_08__imm_050__delay_05` | hold_count=`8` | immediate_weight=`0.5` | delay_days=`5` | train_cum=`0.377399` | test_cum=`0.462169` | review_cum=`0.124406` | review_mean_cash=`0.047112` | review_mean_invested_stock_count=`8.000000`

Mean config ranking:
- `pf_stagger__top_08__imm_070__delay_05` | folds=`5` | mean_train_cum=`0.641667` | mean_test_cum=`0.256925` | mean_review_cum=`0.070264` | mean_review_cash=`0.027258`
- `pf_stagger__top_08__imm_050__delay_05` | folds=`5` | mean_train_cum=`0.634888` | mean_test_cum=`0.255141` | mean_review_cum=`0.071008` | mean_review_cash=`0.045157`
- `pf_stagger__top_08__imm_070__delay_03` | folds=`5` | mean_train_cum=`0.677463` | mean_test_cum=`0.250882` | mean_review_cum=`0.067004` | mean_review_cash=`0.016519`
- `pf_stagger__top_08__imm_050__delay_03` | folds=`5` | mean_train_cum=`0.694991` | mean_test_cum=`0.245183` | mean_review_cum=`0.065659` | mean_review_cash=`0.027258`

Baseline means:
- mean_train_cum=`0.650664`
- mean_test_cum=`0.259277`
- mean_review_cum=`0.069055`

Outputs:
- [pure_fundamental_execution_staggered_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\pure_fundamental_execution_staggered_rolling_validation_v1_config_results.csv)
- [pure_fundamental_execution_staggered_rolling_validation_v1_chosen.csv](D:\hh\codex\v4\phase_1_fundamental\pure_fundamental_execution_staggered_rolling_validation_v1_chosen.csv)
