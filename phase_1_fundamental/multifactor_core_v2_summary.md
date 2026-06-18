# Multifactor Core V2 Summary

Core factors used:
- `indicator__roe` | target=`y_quarter_avg_daily_return_close` | direction=`larger_better`
- `indicator__inc_net_profit_to_shareholders_annual` | target=`y_quarter_avg_daily_return_close` | direction=`larger_better`
- `derived__log_total_assets` | target=`y_quarter_avg_daily_return_close` | direction=`larger_better`
- `bank_indicator__cost_to_income_ratio` | target=`y_year_avg_daily_return_close` | direction=`smaller_better`
- `bank_indicator__deposit_loan_ratio` | target=`y_year_avg_daily_return_close` | direction=`smaller_better`
- `bank_indicator__capital_adequacy_ratio` | target=`y_year_avg_daily_return_close` | direction=`larger_better`
- `derived__investment_income_to_operating_revenue` | target=`y_quarter_avg_daily_return_close` | direction=`larger_better`

- Quarterly factor count: `4`
- Annual factor count: `3`

Combo evaluation:
- `combo__equal_weight` `train` | ic=`0.137453` | ic_ir=`0.435347` | top-bottom=`-1.31e-06`
- `combo__equal_weight` `validation` | ic=`0.082859` | ic_ir=`0.496093` | top-bottom=`-4.576e-05`
- `combo__ic_weight` `train` | ic=`0.147669` | ic_ir=`0.495707` | top-bottom=`-6.208e-05`
- `combo__ic_weight` `validation` | ic=`0.15537` | ic_ir=`2.151858` | top-bottom=`0.00017311`
- `combo__quarterly_plus_annual` `train` | ic=`0.141355` | ic_ir=`0.417967` | top-bottom=`0.0001675`
- `combo__quarterly_plus_annual` `validation` | ic=`0.077992` | ic_ir=`0.420001` | top-bottom=`4.619e-05`

Outputs:
- [multifactor_core_v2_panel.csv](D:\hh\codex\v4\phase_1_fundamental\multifactor_core_v2_panel.csv)