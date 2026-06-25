# Base Core 6 Robustness And Top06 Review V1

Scope:
- follow-up archive after the `2026-06-22` pure-fundamental upgrade safebox
- focus = robustness perturbation for `base_core_6`
- focus = JoinQuant confirmation check for the `top_06` execution candidate

Files included:
- `build_base_core_6_robustness_validation_v1.py`
- `base_core_6_robustness_validation_v1.md`
- `base_core_6_robustness_validation_v1_config_results.csv`
- `joinquant_v4_annual_backtest_strategy_base_core_6_minus_log_total_assets_top06_v1.py`

Research summary:
- mother shell remains `base_core_6 = base_core_7 - derived__log_total_assets`
- robustness matrix perturbed:
  - train window = `3 / 5 / 7` years
  - test window = `1 / 2` years
  - review window = `1` year
  - combo = `equal_weight / ic_weight_train / quarterly_plus_annual`
  - hold count = `6 / 8 / 10 / 12`
- local robustness output suggested that `top_06` often beat the old `top_08` baseline inside the research replay
- strongest practical candidate from the local matrix was:
  - `window_5y_2y_1y__combo__ic_weight_train__top_06`

Important local robustness reference:
- baseline `window_5y_2y_1y__combo__ic_weight_train__top_08`
  - mean_test_cum = `0.269435`
  - mean_review_cum = `0.065544`
- candidate `window_5y_2y_1y__combo__ic_weight_train__top_06`
  - mean_test_cum = `0.321874`
  - mean_review_cum = `0.070514`

JoinQuant confirmation result for `top_06` candidate:
- strategy return = `44.51%`
- annualized return = `7.90%`
- excess return = `20.56%`
- alpha = `0.041`
- beta = `1.070`
- sharpe = `0.196`
- max drawdown = `24.92%`
- information ratio = `0.472`
- max drawdown window = `2021/06/04,2022/10/31`

Decision:
- `base_core_6` remains valid as the current pure-fundamental mother shell
- `top_06` did not confirm as the new production execution setting in JoinQuant
- current preferred pure-fundamental candidate remains:
  - `base_core_6 + top_08`

Interpretation:
- the local robustness matrix was useful for idea generation
- but the `top_06` edge did not survive full JoinQuant confirmation
- likely reasons include:
  - local replay vs JoinQuant execution differences
  - higher concentration sensitivity after reducing holdings from `8` to `6`
