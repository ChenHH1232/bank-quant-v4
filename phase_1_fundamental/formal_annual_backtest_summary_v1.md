# Formal Annual Backtest Summary V1

This summary freezes the formal annual backtest comparison onto the annual rule draft's primary and benchmark lines.

- benchmark line: `base_core_7 + combo__ic_weight_train`
- primary line: `base_plus_top2_9 + combo__ic_weight_train`
- fold count: `5`
- mean benchmark review IC: `0.095899`
- mean primary review IC: `0.086609`
- mean benchmark top-bottom spread: `0.0003133`
- mean primary top-bottom spread: `0.000317242`
- primary wins on review IC: `1/5`
- primary wins on top-bottom spread: `2/5`

Annual fold comparison:
- `annual_01` | review=`2021-05-06` to `2022-05-05`
  benchmark_ic=`0.052788` | primary_ic=`-0.006809` | delta_ic=`-0.059597`
  benchmark_spread=`0.00023013` | primary_spread=`0.0002035` | delta_spread=`-2.663e-05`
  base_count=`6` | improvement_count=`2` | primary_selected_count=`8`
  base_factors=`bank_indicator__Nonperforming_loan_rate|bank_indicator__capital_adequacy_ratio|bank_indicator__deposit_loan_ratio|bank_indicator__non_performing_loan_provision_coverage|indicator__eps|indicator__roe`
  improvement_factors=`improve__annual_delta__bank_indicator__Nonperforming_loan_rate|improve__snapshot_delta__derived__investment_income_to_operating_revenue`
- `annual_02` | review=`2022-05-05` to `2023-05-04`
  benchmark_ic=`-0.13306` | primary_ic=`-0.138357` | delta_ic=`-0.005297`
  benchmark_spread=`-0.00035782` | primary_spread=`-0.00058243` | delta_spread=`-0.00022461`
  base_count=`7` | improvement_count=`2` | primary_selected_count=`9`
  base_factors=`bank_indicator__Nonperforming_loan_rate|bank_indicator__capital_adequacy_ratio|bank_indicator__deposit_loan_ratio|bank_indicator__non_performing_loan_provision_coverage|derived__log_total_assets|indicator__eps|indicator__roe`
  improvement_factors=`improve__annual_delta__bank_indicator__capital_adequacy_ratio|improve__snapshot_delta__derived__investment_income_to_operating_revenue`
- `annual_03` | review=`2023-05-04` to `2024-05-03`
  benchmark_ic=`0.189403` | primary_ic=`0.189403` | delta_ic=`0.0`
  benchmark_spread=`0.00053031` | primary_spread=`0.00053031` | delta_spread=`0.0`
  base_count=`3` | improvement_count=`0` | primary_selected_count=`3`
  base_factors=`bank_indicator__capital_adequacy_ratio|bank_indicator__deposit_loan_ratio|derived__log_total_assets`
  improvement_factors=`none`
- `annual_04` | review=`2024-05-06` to `2025-05-05`
  benchmark_ic=`0.220769` | primary_ic=`0.247038` | delta_ic=`0.026269`
  benchmark_spread=`7.368e-05` | primary_spread=`0.00026468` | delta_spread=`0.000191`
  base_count=`2` | improvement_count=`2` | primary_selected_count=`4`
  base_factors=`bank_indicator__capital_adequacy_ratio|derived__log_total_assets`
  improvement_factors=`improve__annual_delta__bank_indicator__Nonperforming_loan_rate|improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual`
- `annual_05` | review=`2025-05-06` to `2026-05-05`
  benchmark_ic=`0.149597` | primary_ic=`0.141769` | delta_ic=`-0.007828`
  benchmark_spread=`0.0010902` | primary_spread=`0.00117015` | delta_spread=`7.995e-05`
  base_count=`4` | improvement_count=`2` | primary_selected_count=`6`
  base_factors=`bank_indicator__capital_adequacy_ratio|bank_indicator__deposit_loan_ratio|bank_indicator__non_performing_loan_provision_coverage|derived__log_total_assets`
  improvement_factors=`improve__season_yoy_delta__derived__staff_cash_to_operating_revenue|improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual`

Interpretation:
- the primary 7+2 shell is kept as the formal main line because it preserves room for yearly improvement supplementation
- the base-only benchmark remains necessary because average review IC is still slightly stronger on the benchmark line in the current sample
- annual comparison should therefore focus on whether the primary line wins often enough on spread and future extensions, not only on the full-period mean IC

Outputs:
- [formal_annual_backtest_summary_v1.csv](D:\hh\codex\v4\phase_1_fundamental\formal_annual_backtest_summary_v1.csv)