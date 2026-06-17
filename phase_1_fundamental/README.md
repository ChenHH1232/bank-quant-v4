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
