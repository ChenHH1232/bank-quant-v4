# Factor Dedup Decision V2

Updated: 2026-06-18

## Purpose

This document upgrades the `v1` factor de-duplication packet by combining:

- statistical redundancy evidence from the single-factor and collinearity passes
- domain judgment specific to listed Chinese banks

The goal is to avoid keeping multiple variables that are statistically strong only because they proxy for bank size, accounting scale, or balance-sheet mechanics rather than durable cross-bank quality differences.

## Core Principle

At this stage, the main risk is not missing one statistically significant factor.

The main risk is:

- repeatedly feeding the model with size variables
- over-rewarding large banks because many absolute-value fields all encode the same scale effect
- mistaking accounting-flow activity for investment skill or operating quality

Therefore, `v2` decisions are made by combining:

- cluster-level correlation structure
- single-factor evidence
- bank-industry interpretability

## Cluster Decisions

### Q01 Scale Cluster

`v1` keep:

- `cash_flow__staff_behalf_paid`

`v2` decision:

- keep `balance__total_assets`
- use `log(total_assets)` in actual modeling
- do **not** keep raw `cash_flow__staff_behalf_paid` as the cluster representative

Reason:

- staff cash payments are influenced not only by scale, but also by staffing model, branch density, compensation policy, digitization level, and bonus timing
- for a bank cross-section, `total_assets` is a cleaner and more stable size proxy
- most other absolute-value members in this cluster are just alternative ways of saying "this bank is large"

Recommended delete from this cluster:

- `balance__total_liability`
- `balance__total_owner_equities`
- `balance__equities_parent_company_owners`
- `income__operating_revenue`
- `income__net_profit`
- `income__np_parent_company_owners`
- `income__interest_income`
- `income__interest_expense`
- `income__operating_profit`
- `income__total_profit`
- `indicator__adjusted_profit`
- `indicator__operating_profit`
- and other raw large-scale absolute fields inside the same cluster

Deferred / derived candidate:

- `cash_flow__staff_behalf_paid / income__operating_revenue`
- `cash_flow__staff_behalf_paid / average_total_assets`

Interpretation:

- these are labor-cost intensity candidates
- they are better than the raw absolute staff-cash value

### Q02 Investment Cash-Flow Cluster

`v2` decision:

- delete the whole cluster

Delete:

- `cash_flow__invest_withdrawal_cash`
- `cash_flow__invest_cash_paid`
- `cash_flow__subtotal_invest_cash_inflow`
- `cash_flow__subtotal_invest_cash_outflow`

Reason:

- these describe investment cash-flow activity volume
- they do not directly measure investment skill or investment return
- for banks, they are strongly driven by bond maturity, roll-over, trading rhythm, and balance-sheet management

### Q03 Profit-Growth Cluster

`v1` keep:

- `indicator__inc_net_profit_annual`

`v2` decision:

- keep `indicator__inc_net_profit_to_shareholders_annual`

Delete:

- `indicator__inc_net_profit_annual`
- `indicator__inc_operation_profit_annual`

Reason:

- for listed-bank equity selection, the shareholder-relevant profit measure is more directly aligned with stockholder outcomes
- parent-company attributable net-profit growth is cleaner than total net-profit growth when minority interests may exist

Future enhancement candidate:

- 3-year CAGR of attributable profit
- attributable-profit growth volatility

### Q04 Profitability Cluster

`v2` decision:

- keep `indicator__roe`
- delete `indicator__inc_return`
- delete `indicator__roa` from the core set

Reason:

- ROE is the best first-line equity-holder profitability metric
- `inc_return` is nearly a duplicate ROE-style return measure
- ROA has information, but if the model also keeps capital-adequacy controls, then ROE plus capital ratios is a better bank-equity combination than keeping all three in the same cluster

Condition:

- this decision assumes the model retains bank capital metrics such as capital adequacy and core tier-1 adequacy in the broader factor set

### Q05 Operating Cash-Flow Cluster

`v2` decision:

- delete the whole cluster

Delete:

- `cash_flow__net_operate_cash_flow`
- `indicator__ocf_to_revenue`

Reason:

- for banks, operating cash flow does not play the same interpretive role it does for industrial firms
- it is heavily affected by deposit inflows, loan growth, interbank positions, central-bank funding, and financial-asset classification
- it is not a clean measure of earnings quality in a bank cross-section

### Q06 Investment-Income Cluster

`v2` decision:

- do not keep raw `income__investment_income` as a core factor
- do not keep `indicator__value_change_profit` as a core factor
- retain this cluster only after re-construction into a ratio-based investment-return concept

Current raw fields:

- `income__investment_income`
- `indicator__value_change_profit`

Preferred derived factor:

- `investment_income / average_investment_assets`

Fallback derived factor if full investment-asset denominator is unavailable:

- `investment_income / income__operating_revenue`

Interpretation:

- the preferred metric is an investment return proxy
- the fallback metric is only an investment-income contribution proxy, not a true return measure

Reason:

- raw investment income is still heavily scale-driven
- fair-value change profit is not identical to realized investment income
- both are sensitive to bond-market cycle and realization timing, so they are not ideal core quality factors in raw absolute-value form

### Q07 Net-Margin Cluster

`v2` decision:

- delete the whole cluster

Delete:

- `indicator__net_profit_margin`
- `indicator__net_profit_to_total_revenue`

Reason:

- for banks, net-margin comparisons are confounded by policy role, business mix, credit cost, non-interest income mix, and accounting treatment of investment/fair-value items
- these fields add limited clean information once the model already contains bank-specific metrics such as:
  - net interest margin
  - ROE
  - ROA
  - cost-to-income ratio
  - NPL ratio
  - provision coverage
  - non-interest income ratio

## V2 Keep / Drop / Rebuild Summary

### Keep As Core Representatives

- `balance__total_assets`
  - use transformed form: `log(total_assets)`
- `indicator__inc_net_profit_to_shareholders_annual`
- `indicator__roe`

### Delete Entire Cluster

- `Q02`
- `Q05`
- `Q07`

### Rebuild Before Keeping

- `Q06`
  - preferred: `investment_income / average_investment_assets`
  - fallback: `investment_income / operating_revenue`

### Convert To Derived Efficiency Candidates

- `cash_flow__staff_behalf_paid / operating_revenue`
- `cash_flow__staff_behalf_paid / average_total_assets`

## Modeling Implication

Compared with the `v1` mechanical cluster keep-list, `v2` is more conservative and more bank-specific.

The intended outcome is:

- fewer duplicated size proxies
- less accidental "buy the largest bank repeatedly"
- clearer distinction between:
  - scale
  - shareholder profitability
  - annual profit improvement
  - bank-specific prudential quality

## Next Action

The next implementation step should be:

1. create a formal `v2` retained-factor shortlist
2. mark deleted cluster members explicitly
3. add derived-factor backlog items for:
   - log total assets
   - staff-cost intensity
   - investment-return ratio
