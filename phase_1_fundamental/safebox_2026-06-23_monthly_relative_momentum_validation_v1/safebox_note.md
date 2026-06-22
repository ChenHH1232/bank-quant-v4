# Safebox Note

Archive name:

- `safebox_2026-06-23_monthly_relative_momentum_validation_v1`

Purpose:

- preserve the full monthly relative momentum validation chain for pure-fundamental follow-up
- keep rolling branch-switch, rolling continuous tilt, rolling discrete tilt, JoinQuant executable candidate, and final summary in one recoverable snapshot

Contents:

- `monthly_relative_momentum_validation_summary_2026-06-23.md`
- `build_base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1.py`
- `base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1.md`
- `base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1_config_results.csv`
- `build_base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1.py`
- `base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1.md`
- `base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1_config_results.csv`
- `build_base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2.py`
- `base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2.md`
- `base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2_config_results.csv`
- `joinquant_v4_annual_backtest_strategy_base_core_6_monthly_relative_momentum_tilt_discrete_v1.py`

Decision snapshot:

- monthly branch switching did not beat simply keeping the stronger branch B candidate
- monthly continuous tilt looked directionally sensible but only offered weak rolling improvement
- monthly discrete tilt looked slightly better in rolling, but the JoinQuant executable candidate failed clearly
- final status: archive the whole monthly relative momentum style-timing path as research-complete but execution-rejected
