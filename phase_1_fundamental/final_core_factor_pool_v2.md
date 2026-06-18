# Final Core Factor Pool V2

Updated: 2026-06-18

Purpose:

- compress the `v2` retained list into a practical core pool for the next modeling stage
- avoid mechanically carrying every `keep_core` field into the final multi-factor candidate set
- prioritize bank-specific interpretability over raw field count

## Core Keep

- `derived__log_total_assets`
- `indicator__roe`
- `indicator__inc_net_profit_to_shareholders_annual`
- `bank_indicator__Nonperforming_loan_rate`
- `bank_indicator__non_performing_loan_provision_coverage`
- `bank_indicator__capital_adequacy_ratio`
- `bank_indicator__core_level_capital_adequacy_ratio`
- `bank_indicator__cost_to_income_ratio`
- `bank_indicator__deposit_loan_ratio`
- `bank_indicator__net_interest_margin`
- `bank_indicator__non_interest_income_ratio`

## Secondary Candidates

- `derived__staff_cash_to_operating_revenue`
- `derived__investment_income_to_operating_revenue`

These are allowed into the next round of testing, but are not automatically part of the core bank-quality block.

## Watch Only

- `income__minority_profit`
- `indicator__eps`

These remain interesting statistically, but they are not yet promoted into the core bank factor set.

## Explicitly Not In Core Pool

The following are intentionally excluded from the current core pool even if they appeared in earlier `keep_core` or statistical passes:

- `bank_indicator__total_deposit`
- `bank_indicator__total_loan`
- `bank_indicator__weighted_risky_asset`

Reason:

- they are still too close to scale or scale-adjacent balance-sheet magnitude
- the current `v2` goal is to avoid silently reintroducing size through multiple channels

## Next Action

1. test the two immediately available derived factors
2. decide whether `watch_only` fields deserve promotion
3. separately research how to source a clean denominator for:
   - `investment_income / average_investment_assets`
