# Factor Collinearity Check V1

Scope:
- training window only: `2014-05-01` to `2019-05-01`
- sample only: `rebalance_stock_pool_flag = 1`
- only single-factor `A/B` candidates are included
- quarterly and annual targets are checked separately

## y_quarter_avg_daily_return_close
- factor count: `43`
- high-corr factors (`abs corr >= 0.8`): `34`
- high-VIF factors (`VIF >= 10`): `32`
- highest-correlation factors:
- `indicator__net_profit_margin` vs `indicator__net_profit_to_total_revenue` | corr=`1.0` | vif=`inf`
- `indicator__net_profit_to_total_revenue` vs `indicator__net_profit_margin` | corr=`1.0` | vif=`inf`
- `balance__total_liability` vs `balance__total_assets` | corr=`0.999857` | vif=`inf`
- `balance__total_assets` vs `balance__total_liability` | corr=`0.999857` | vif=`inf`
- `cash_flow__invest_cash_paid` vs `cash_flow__subtotal_invest_cash_outflow` | corr=`0.999719` | vif=`1656.763985`
- top pairwise correlations:
- `indicator__net_profit_margin` vs `indicator__net_profit_to_total_revenue` | corr=`1.0`
- `balance__total_assets` vs `balance__total_liability` | corr=`0.999857`
- `cash_flow__invest_cash_paid` vs `cash_flow__subtotal_invest_cash_outflow` | corr=`0.999719`
- `balance__total_owner_equities` vs `balance__equities_parent_company_owners` | corr=`0.999713`
- `income__operating_profit` vs `income__total_profit` | corr=`0.999668`

## y_year_avg_daily_return_close
- factor count: `4`
- high-corr factors (`abs corr >= 0.8`): `0`
- high-VIF factors (`VIF >= 10`): `0`
- highest-correlation factors:
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__total_deposit` | corr=`0.571407` | vif=`1.824154`
- `bank_indicator__total_deposit` vs `bank_indicator__capital_adequacy_ratio` | corr=`0.571407` | vif=`1.834282`
- `bank_indicator__cost_to_income_ratio` vs `bank_indicator__capital_adequacy_ratio` | corr=`0.11061` | vif=`1.034788`
- `bank_indicator__deposit_loan_ratio` vs `bank_indicator__capital_adequacy_ratio` | corr=`0.059318` | vif=`1.038459`
- top pairwise correlations:
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__total_deposit` | corr=`0.571407`
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__cost_to_income_ratio` | corr=`-0.11061`
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__deposit_loan_ratio` | corr=`-0.059318`
- `bank_indicator__cost_to_income_ratio` vs `bank_indicator__deposit_loan_ratio` | corr=`-0.04633`
- `bank_indicator__deposit_loan_ratio` vs `bank_indicator__total_deposit` | corr=`0.032687`

Outputs:
- [factor_collinearity_v1.csv](D:\hh\codex\v4\phase_1_fundamental\factor_collinearity_v1.csv)
- [factor_pairwise_corr_v1.csv](D:\hh\codex\v4\phase_1_fundamental\factor_pairwise_corr_v1.csv)