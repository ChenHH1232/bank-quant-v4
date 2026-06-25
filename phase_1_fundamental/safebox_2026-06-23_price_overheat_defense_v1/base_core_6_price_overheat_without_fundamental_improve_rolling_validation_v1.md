# Base Core 6 Price Overheat Without Fundamental Improve Rolling Validation V1

Protocol:
- factor engine = annual pure-fundamental `base_core_6`
- combo fixed at `combo__ic_weight_train`
- stock selection fixed at `top bucket` from the five-group cross-section
- a stock becomes eligible for overheat capping only if its fundamentals did not improve enough at entry
- fundamental improvement is counted across the six resident `base_core_6` fields versus the previous rebalance snapshot
- minimum available improvement signals required = `3`
- only eligible stocks are capped after price overheat; other holdings keep their original weight
- released weight stays in cash with `0` return
- tested price-overheat trigger growth = `15% / 20%`
- tested post-trigger stock cap = `15% / 10%`
- tested poor-improvement threshold = `improve_count <= 1 / 2`

Baseline means:
- train/test/review cum = `0.870620` / `0.365221` / `0.058546`

Candidate ranking:
- `price_hot_no_fund_improve__trigger_20__cap_010__maximp_1` | folds=`5` | mean_train_cum=`0.997475` | mean_test_cum=`0.368580` | mean_review_cum=`0.061228` | delta_test_vs_baseline=`0.003359` | delta_review_vs_baseline=`0.002681` | mean_review_cash=`0.011877` | mean_review_trim_events=`0.400000` | mean_review_weight_sum=`0.973333`
- `price_hot_no_fund_improve__trigger_20__cap_010__maximp_2` | folds=`5` | mean_train_cum=`0.930846` | mean_test_cum=`0.367273` | mean_review_cum=`0.059491` | delta_test_vs_baseline=`0.002052` | delta_review_vs_baseline=`0.000945` | mean_review_cash=`0.035947` | mean_review_trim_events=`0.700000` | mean_review_weight_sum=`0.936667`
- `price_hot_no_fund_improve__trigger_20__cap_015__maximp_1` | folds=`5` | mean_train_cum=`0.961632` | mean_test_cum=`0.366499` | mean_review_cum=`0.059218` | delta_test_vs_baseline=`0.001278` | delta_review_vs_baseline=`0.000672` | mean_review_cash=`0.003789` | mean_review_trim_events=`0.400000` | mean_review_weight_sum=`0.993333`
- `price_hot_no_fund_improve__trigger_20__cap_015__maximp_2` | folds=`5` | mean_train_cum=`0.900027` | mean_test_cum=`0.364874` | mean_review_cum=`0.057913` | delta_test_vs_baseline=`-0.000347` | delta_review_vs_baseline=`-0.000633` | mean_review_cash=`0.019472` | mean_review_trim_events=`0.700000` | mean_review_weight_sum=`0.971667`
- `price_hot_no_fund_improve__trigger_15__cap_015__maximp_1` | folds=`5` | mean_train_cum=`0.911976` | mean_test_cum=`0.359806` | mean_review_cum=`0.059853` | delta_test_vs_baseline=`-0.005416` | delta_review_vs_baseline=`0.001306` | mean_review_cash=`0.008494` | mean_review_trim_events=`0.966667` | mean_review_weight_sum=`0.981667`
- `price_hot_no_fund_improve__trigger_15__cap_010__maximp_1` | folds=`5` | mean_train_cum=`0.924884` | mean_test_cum=`0.355502` | mean_review_cum=`0.064200` | delta_test_vs_baseline=`-0.009719` | delta_review_vs_baseline=`0.005654` | mean_review_cash=`0.029773` | mean_review_trim_events=`0.966667` | mean_review_weight_sum=`0.933333`
- `price_hot_no_fund_improve__trigger_15__cap_015__maximp_2` | folds=`5` | mean_train_cum=`0.846940` | mean_test_cum=`0.345270` | mean_review_cum=`0.055798` | delta_test_vs_baseline=`-0.019951` | delta_review_vs_baseline=`-0.002748` | mean_review_cash=`0.027112` | mean_review_trim_events=`1.266667` | mean_review_weight_sum=`0.960000`
- `price_hot_no_fund_improve__trigger_15__cap_010__maximp_2` | folds=`5` | mean_train_cum=`0.844815` | mean_test_cum=`0.332708` | mean_review_cum=`0.057898` | delta_test_vs_baseline=`-0.032513` | delta_review_vs_baseline=`-0.000648` | mean_review_cash=`0.059436` | mean_review_trim_events=`1.266667` | mean_review_weight_sum=`0.896667`

Outputs:
- [base_core_6_price_overheat_without_fundamental_improve_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\base_core_6_price_overheat_without_fundamental_improve_rolling_validation_v1_config_results.csv)
