# Final Core Factor Pool V2 Trimmed

Updated: 2026-06-18

This file is the trimmed result after:

- v1 single-factor screening
- collinearity and de-duplication review
- v2 bank-domain override decisions
- focused core-v2 retest

## Final Keep

- `indicator__roe`
- `indicator__inc_net_profit_to_shareholders_annual`
- `derived__log_total_assets`
- `bank_indicator__cost_to_income_ratio`
- `bank_indicator__deposit_loan_ratio`
- `bank_indicator__capital_adequacy_ratio`
- `derived__investment_income_to_operating_revenue`

These are the current best-supported core factors after both statistical and banking-logic review.

## Watch Keep

- `income__minority_profit`
- `indicator__eps`

These survived the focused retest, but they are not yet promoted into the strict core block.

## Downgraded To Watch

- `bank_indicator__Nonperforming_loan_rate`
- `bank_indicator__non_performing_loan_provision_coverage`
- `bank_indicator__core_level_capital_adequacy_ratio`
- `bank_indicator__non_interest_income_ratio`
- `bank_indicator__net_interest_margin`

These remain economically meaningful banking concepts, but in the current `2014-05-01` to `2021-05-01` test design they did not survive the focused validation pass.

## Dropped After Retest

- `derived__staff_cash_to_operating_revenue`

This derived Q01 candidate did not hold up in the focused retest and should not move forward as a current candidate.

## Practical Next Step

The next modeling layer should start from the seven final-keep fields, and only add `watch_keep` items if they improve robustness rather than complexity.
