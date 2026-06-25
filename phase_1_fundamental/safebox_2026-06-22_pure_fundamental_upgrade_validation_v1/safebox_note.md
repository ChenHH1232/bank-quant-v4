# Pure Fundamental Upgrade Validation Safebox

Date: `2026-06-22`

Purpose:

- preserve the full validation chain used to upgrade the current pure-fundamental line
- keep the failed execution-layer variants and the successful factor-layer refinement in one recoverable snapshot

Included:

- `build_pure_fundamental_execution_rolling_validation_v1.py`
- `pure_fundamental_execution_rolling_validation_v1.md`
- `pure_fundamental_execution_rolling_validation_v1_config_results.csv`
- `pure_fundamental_execution_rolling_validation_v1_chosen.csv`
- `build_pure_fundamental_execution_staggered_rolling_validation_v1.py`
- `pure_fundamental_execution_staggered_rolling_validation_v1.md`
- `pure_fundamental_execution_staggered_rolling_validation_v1_config_results.csv`
- `pure_fundamental_execution_staggered_rolling_validation_v1_chosen.csv`
- `build_base_core_7_leave_one_out_rolling_validation_v1.py`
- `base_core_7_leave_one_out_rolling_validation_v1.md`
- `base_core_7_leave_one_out_rolling_validation_v1_config_results.csv`
- `build_base_core_6_minus_log_total_assets_v1.py`
- `base_core_6_minus_log_total_assets_v1.md`
- `base_core_6_minus_log_total_assets_v1_folds.csv`
- `base_core_6_minus_log_total_assets_v1_factor_selection.csv`
- `base_core_6_minus_log_total_assets_v1_results.csv`
- `joinquant_v4_annual_backtest_strategy_base_core_6_minus_log_total_assets_v1.py`

Decision snapshot:

- execution-layer changes did not produce a stable upgrade:
  - wider holding count did not beat the baseline
  - full delay entry did not beat the baseline
  - staggered entry slightly improved review means but still did not beat baseline on mean test
- leave-one-out rolling pointed to `derived__log_total_assets` as the most likely drag factor inside `base_core_7`
- promoting `base_core_6 = base_core_7 - derived__log_total_assets` improved both rolling research readout and the later JoinQuant comparison
- reported JoinQuant candidate result for `base_core_6`:
  - strategy return = `48.38%`
  - annualized return = `8.49%`
  - excess return = `23.80%`
  - sharpe = `0.233`
  - max drawdown = `22.29%`
- compared with the earlier pure-fundamental baseline, the main benefit came from higher return, alpha, sharpe, sortino, and information ratio, while max drawdown stayed roughly unchanged
- current conclusion: treat `base_core_6 minus log_total_assets` as the new leading pure-fundamental candidate branch
