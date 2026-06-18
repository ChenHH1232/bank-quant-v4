# Retained Factor Shortlist V2

Summary:
- keep_core: `14`
- keep_regular: `55`
- drop: `5`

Core manual v2 overrides:
- keep `log(balance__total_assets)` as the size representative
- keep `indicator__inc_net_profit_to_shareholders_annual`
- keep `indicator__roe`
- delete clusters `Q02`, `Q05`, `Q07`
- rebuild cluster `Q06` before reuse

Derived backlog capability:
- `cash_flow__staff_behalf_paid / income__operating_revenue` | status=`ready_now` | labor-cost intensity candidate
- `cash_flow__staff_behalf_paid / average_total_assets` | status=`ready_with_construction_rule` | requires lag/average total-assets construction from panel history
- `income__investment_income / average_investment_assets` | status=`blocked_need_new_denominator` | investment asset denominator not present in current panel header; needs new source/definition
- `income__investment_income / income__operating_revenue` | status=`ready_now` | fallback contribution ratio if denominator unavailable

Outputs:
- [retained_factor_shortlist_v2.csv](D:\hh\codex\v4\phase_1_fundamental\retained_factor_shortlist_v2.csv)
- [derived_factor_backlog_v2.csv](D:\hh\codex\v4\phase_1_fundamental\derived_factor_backlog_v2.csv)