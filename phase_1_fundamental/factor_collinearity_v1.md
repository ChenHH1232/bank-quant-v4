# Factor Collinearity Check V1

Scope:
- training window only: `2014-05-01` to `2019-05-01`
- sample only: `rebalance_stock_pool_flag = 1`
- only single-factor `A/B` candidates are included
- quarterly and annual targets are checked separately

## y_quarter_avg_daily_return_close
- factor count: `43`
- high-corr factors (`abs corr >= 0.8`): `36`
- high-VIF factors (`VIF >= 10`): `36`
- highest-correlation factors:
- `indicator__net_profit_margin` vs `indicator__net_profit_to_total_revenue` | corr=`1.0` | vif=`inf`
- `indicator__net_profit_to_total_revenue` vs `indicator__net_profit_margin` | corr=`1.0` | vif=`inf`
- `balance__total_liability` vs `balance__total_assets` | corr=`0.999889` | vif=`445106.152951`
- `balance__total_assets` vs `balance__total_liability` | corr=`0.999889` | vif=`495002.972537`
- `income__np_parent_company_owners` vs `income__net_profit` | corr=`0.999819` | vif=`400324.540523`
- top pairwise correlations:
- `indicator__net_profit_margin` vs `indicator__net_profit_to_total_revenue` | corr=`1.0`
- `balance__total_assets` vs `balance__total_liability` | corr=`0.999889`
- `income__net_profit` vs `income__np_parent_company_owners` | corr=`0.999819`
- `balance__total_owner_equities` vs `balance__equities_parent_company_owners` | corr=`0.999678`
- `income__net_profit` vs `indicator__adjusted_profit` | corr=`0.999587`

## y_year_avg_daily_return_close
- factor count: `4`
- high-corr factors (`abs corr >= 0.8`): `0`
- high-VIF factors (`VIF >= 10`): `0`
- highest-correlation factors:
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__total_deposit` | corr=`0.515041` | vif=`1.647183`
- `bank_indicator__total_deposit` vs `bank_indicator__capital_adequacy_ratio` | corr=`0.515041` | vif=`1.632948`
- `bank_indicator__deposit_loan_ratio` vs `bank_indicator__total_deposit` | corr=`0.180343` | vif=`1.006942`
- `bank_indicator__cost_to_income_ratio` vs `bank_indicator__capital_adequacy_ratio` | corr=`0.099223` | vif=`1.017615`
- top pairwise correlations:
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__total_deposit` | corr=`0.515041`
- `bank_indicator__deposit_loan_ratio` vs `bank_indicator__total_deposit` | corr=`0.180343`
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__cost_to_income_ratio` | corr=`0.099223`
- `bank_indicator__cost_to_income_ratio` vs `bank_indicator__deposit_loan_ratio` | corr=`-0.057603`
- `bank_indicator__capital_adequacy_ratio` vs `bank_indicator__deposit_loan_ratio` | corr=`-0.014795`

Outputs:
- [factor_collinearity_v1.csv](D:\hh\codex\v4\phase_1_fundamental\factor_collinearity_v1.csv)
- [factor_pairwise_corr_v1.csv](D:\hh\codex\v4\phase_1_fundamental\factor_pairwise_corr_v1.csv)