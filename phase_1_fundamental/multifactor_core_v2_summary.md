# Multifactor Core V2 Summary

Core factors used:
- `indicator__roe` | target=`y_quarter_avg_daily_return_close` | direction=`larger_better`
- `indicator__inc_net_profit_to_shareholders_annual` | target=`y_quarter_avg_daily_return_close` | direction=`smaller_better`
- `derived__log_total_assets` | target=`y_quarter_avg_daily_return_close` | direction=`larger_better`
- `bank_indicator__cost_to_income_ratio` | target=`y_year_avg_daily_return_close` | direction=`larger_better`
- `bank_indicator__deposit_loan_ratio` | target=`y_year_avg_daily_return_close` | direction=`smaller_better`
- `bank_indicator__capital_adequacy_ratio` | target=`y_year_avg_daily_return_close` | direction=`larger_better`
- `derived__investment_income_to_operating_revenue` | target=`y_quarter_avg_daily_return_close` | direction=`larger_better`

- Quarterly factor count: `4`
- Annual factor count: `3`

Combo evaluation:
- `combo__equal_weight` `train` | ic=`0.138344` | ic_ir=`0.427438` | top-bottom=`0.0008874`
- `combo__equal_weight` `validation` | ic=`0.213124` | ic_ir=`1.194791` | top-bottom=`0.00074522`
- `combo__ic_weight` `train` | ic=`0.113321` | ic_ir=`0.336315` | top-bottom=`0.00082964`
- `combo__ic_weight` `validation` | ic=`0.20061` | ic_ir=`1.025021` | top-bottom=`0.0009128`
- `combo__quarterly_plus_annual` `train` | ic=`0.190393` | ic_ir=`0.552026` | top-bottom=`0.0009931`
- `combo__quarterly_plus_annual` `validation` | ic=`0.229192` | ic_ir=`1.180207` | top-bottom=`0.00089657`

Outputs:
- [multifactor_core_v2_panel.csv](D:\hh\codex\v4\phase_1_fundamental\multifactor_core_v2_panel.csv)