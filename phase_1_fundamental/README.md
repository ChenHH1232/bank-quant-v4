# Phase 1: Fundamental

Goal:

- Collect and clean core bank fundamental data
- Run standalone statistical tests on fundamental factors first
- Do not mix momentum or mean-reversion features into this phase

Project time protocol:

- [TIME_PROTOCOL.md](/D:/hh/codex/v4/TIME_PROTOCOL.md)

Workflow:

1. Define required fields and source mapping
2. Download raw data
3. Align disclosure dates and reporting periods
4. Clean and standardize field formats
5. Build valid data segments for stock-quarter observations
6. Build factor candidates
7. Run rolling statistical tests

Current validity outputs:

- [valid_data_segment_definition.md](/D:/hh/codex/v4/phase_1_fundamental/valid_data_segment_definition.md)
- [quarterly_valid_data_segments.csv](/D:/hh/codex/v4/phase_1_fundamental/quarterly_valid_data_segments.csv)

Dynamic rebalance stock-pool template:

- [build_formal_daily_market_rebalance_input.py](/D:/hh/codex/v4/phase_1_fundamental/build_formal_daily_market_rebalance_input.py)
- [build_dynamic_rebalance_stock_pool.py](/D:/hh/codex/v4/phase_1_fundamental/build_dynamic_rebalance_stock_pool.py)
- [daily_market_rebalance_input.csv](/D:/hh/codex/v4/phase_1_fundamental/daily_market_rebalance_input.csv)
- [dynamic_rebalance_stock_pool.csv](/D:/hh/codex/v4/phase_1_fundamental/dynamic_rebalance_stock_pool.csv)

Current modeling panel outputs:

- [build_phase1_training_panel.py](/D:/hh/codex/v4/phase_1_fundamental/build_phase1_training_panel.py)
- [phase1_training_panel.csv](/D:/hh/codex/v4/phase_1_fundamental/phase1_training_panel.csv)
- [phase1_training_panel.md](/D:/hh/codex/v4/phase_1_fundamental/phase1_training_panel.md)
- [phase1_tradable_rebalance_samples.csv](/D:/hh/codex/v4/phase_1_fundamental/phase1_tradable_rebalance_samples.csv)
- [phase1_tradable_rebalance_samples.md](/D:/hh/codex/v4/phase_1_fundamental/phase1_tradable_rebalance_samples.md)

Single-factor test protocol:

- [single_factor_test_protocol_v1.md](/D:/hh/codex/v4/phase_1_fundamental/single_factor_test_protocol_v1.md)
- [build_single_factor_manifest.py](/D:/hh/codex/v4/phase_1_fundamental/build_single_factor_manifest.py)
- [build_single_factor_test_results.py](/D:/hh/codex/v4/phase_1_fundamental/build_single_factor_test_results.py)
- [build_factor_collinearity_check_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_factor_collinearity_check_v1.py)
- [build_factor_dedup_clusters_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_factor_dedup_clusters_v1.py)
- [build_factor_dedup_review_packet_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_factor_dedup_review_packet_v1.py)
- [factor_dedup_decision_v2.md](/D:/hh/codex/v4/phase_1_fundamental/factor_dedup_decision_v2.md)
- [factor_dedup_decision_v2.csv](/D:/hh/codex/v4/phase_1_fundamental/factor_dedup_decision_v2.csv)
- [build_factor_retention_v2.py](/D:/hh/codex/v4/phase_1_fundamental/build_factor_retention_v2.py)
- [final_core_factor_pool_v2.csv](/D:/hh/codex/v4/phase_1_fundamental/final_core_factor_pool_v2.csv)
- [final_core_factor_pool_v2.md](/D:/hh/codex/v4/phase_1_fundamental/final_core_factor_pool_v2.md)
- [build_single_factor_manifest_core_v2.py](/D:/hh/codex/v4/phase_1_fundamental/build_single_factor_manifest_core_v2.py)
- [build_single_factor_test_results_core_v2.py](/D:/hh/codex/v4/phase_1_fundamental/build_single_factor_test_results_core_v2.py)
- [final_core_factor_pool_v2_trimmed.csv](/D:/hh/codex/v4/phase_1_fundamental/final_core_factor_pool_v2_trimmed.csv)
- [final_core_factor_pool_v2_trimmed.md](/D:/hh/codex/v4/phase_1_fundamental/final_core_factor_pool_v2_trimmed.md)
- [build_multifactor_combo_core_v2.py](/D:/hh/codex/v4/phase_1_fundamental/build_multifactor_combo_core_v2.py)
- [build_multifactor_combo_backtest_core_v2.py](/D:/hh/codex/v4/phase_1_fundamental/build_multifactor_combo_backtest_core_v2.py)

Improvement-factor layer:

- [build_improvement_factor_manifest_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_improvement_factor_manifest_v1.py)
- [improvement_factor_manifest_v1.csv](/D:/hh/codex/v4/phase_1_fundamental/improvement_factor_manifest_v1.csv)
- [improvement_factor_manifest_v1.md](/D:/hh/codex/v4/phase_1_fundamental/improvement_factor_manifest_v1.md)
- [build_improvement_factor_test_results_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_improvement_factor_test_results_v1.py)
- [improvement_factor_panel_v1.csv](/D:/hh/codex/v4/phase_1_fundamental/improvement_factor_panel_v1.csv)
- [improvement_factor_test_results_v1.csv](/D:/hh/codex/v4/phase_1_fundamental/improvement_factor_test_results_v1.csv)
- [improvement_factor_test_results_v1.md](/D:/hh/codex/v4/phase_1_fundamental/improvement_factor_test_results_v1.md)
- [build_multifactor_incremental_improvement_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_multifactor_incremental_improvement_v1.py)
- [multifactor_incremental_improvement_v1.csv](/D:/hh/codex/v4/phase_1_fundamental/multifactor_incremental_improvement_v1.csv)
- [multifactor_incremental_improvement_v1.md](/D:/hh/codex/v4/phase_1_fundamental/multifactor_incremental_improvement_v1.md)
- [build_multifactor_top2_improvement_combo_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_multifactor_top2_improvement_combo_v1.py)
- [multifactor_top2_improvement_combo_v1.csv](/D:/hh/codex/v4/phase_1_fundamental/multifactor_top2_improvement_combo_v1.csv)
- [multifactor_top2_improvement_combo_v1.md](/D:/hh/codex/v4/phase_1_fundamental/multifactor_top2_improvement_combo_v1.md)
- [final_core_factor_pool_v3.csv](/D:/hh/codex/v4/phase_1_fundamental/final_core_factor_pool_v3.csv)
- [final_core_factor_pool_v3.md](/D:/hh/codex/v4/phase_1_fundamental/final_core_factor_pool_v3.md)
- [build_time_series_cv_feasibility_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_time_series_cv_feasibility_v1.py)
- [time_series_cv_feasibility_v1.csv](/D:/hh/codex/v4/phase_1_fundamental/time_series_cv_feasibility_v1.csv)
- [time_series_cv_feasibility_v1.md](/D:/hh/codex/v4/phase_1_fundamental/time_series_cv_feasibility_v1.md)
- [build_pre2021_rolling_validation_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_pre2021_rolling_validation_v1.py)
- [pre2021_rolling_validation_v1_folds.csv](/D:/hh/codex/v4/phase_1_fundamental/pre2021_rolling_validation_v1_folds.csv)
- [pre2021_rolling_validation_v1_results.csv](/D:/hh/codex/v4/phase_1_fundamental/pre2021_rolling_validation_v1_results.csv)
- [pre2021_rolling_validation_v1.md](/D:/hh/codex/v4/phase_1_fundamental/pre2021_rolling_validation_v1.md)
- [build_formal_walk_forward_validation_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_formal_walk_forward_validation_v1.py)
- [formal_walk_forward_validation_v1_folds.csv](/D:/hh/codex/v4/phase_1_fundamental/formal_walk_forward_validation_v1_folds.csv)
- [formal_walk_forward_validation_v1_results.csv](/D:/hh/codex/v4/phase_1_fundamental/formal_walk_forward_validation_v1_results.csv)
- [formal_walk_forward_validation_v1.md](/D:/hh/codex/v4/phase_1_fundamental/formal_walk_forward_validation_v1.md)
- [build_annual_factor_refresh_5y2y1y_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_annual_factor_refresh_5y2y1y_v1.py)
- [annual_factor_refresh_5y2y1y_v1_folds.csv](/D:/hh/codex/v4/phase_1_fundamental/annual_factor_refresh_5y2y1y_v1_folds.csv)
- [annual_factor_refresh_5y2y1y_v1_factor_selection.csv](/D:/hh/codex/v4/phase_1_fundamental/annual_factor_refresh_5y2y1y_v1_factor_selection.csv)
- [annual_factor_refresh_5y2y1y_v1_results.csv](/D:/hh/codex/v4/phase_1_fundamental/annual_factor_refresh_5y2y1y_v1_results.csv)
- [annual_factor_refresh_5y2y1y_v1.md](/D:/hh/codex/v4/phase_1_fundamental/annual_factor_refresh_5y2y1y_v1.md)
- [build_annual_factor_refresh_selection_summary_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_annual_factor_refresh_selection_summary_v1.py)
- [annual_factor_refresh_selection_summary_v1.md](/D:/hh/codex/v4/phase_1_fundamental/annual_factor_refresh_selection_summary_v1.md)
- [build_annual_review_backtest_detail_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_annual_review_backtest_detail_v1.py)
- [annual_review_backtest_detail_v1_groups.csv](/D:/hh/codex/v4/phase_1_fundamental/annual_review_backtest_detail_v1_groups.csv)
- [annual_review_backtest_detail_v1.md](/D:/hh/codex/v4/phase_1_fundamental/annual_review_backtest_detail_v1.md)
- [build_controlled_improvement_pool_v1.py](/D:/hh/codex/v4/phase_1_fundamental/build_controlled_improvement_pool_v1.py)
- [controlled_improvement_pool_v1.csv](/D:/hh/codex/v4/phase_1_fundamental/controlled_improvement_pool_v1.csv)
- [controlled_improvement_pool_v1.md](/D:/hh/codex/v4/phase_1_fundamental/controlled_improvement_pool_v1.md)
- [build_2013_bank_indicator_backfill_plan.py](/D:/hh/codex/v4/phase_1_fundamental/build_2013_bank_indicator_backfill_plan.py)
- [bank_indicator_2013_backfill_banks.csv](/D:/hh/codex/v4/phase_1_fundamental/bank_indicator_2013_backfill_banks.csv)
- [bank_indicator_2013_backfill_fields.csv](/D:/hh/codex/v4/phase_1_fundamental/bank_indicator_2013_backfill_fields.csv)
- [run_2013_bank_indicator_backfill_download.ps1](/D:/hh/codex/v4/phase_1_fundamental/run_2013_bank_indicator_backfill_download.ps1)
- [bank_indicator_2013_backfill_plan.md](/D:/hh/codex/v4/phase_1_fundamental/bank_indicator_2013_backfill_plan.md)
- [download_joinquant_2013_bank_indicator_backfill.py](/D:/hh/codex/v4/phase_1_fundamental/download_joinquant_2013_bank_indicator_backfill.py)
