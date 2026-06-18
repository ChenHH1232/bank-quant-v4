# Final Core Factor Pool V3

Updated: 2026-06-18

This file refreshes the core-factor decision after:

- adding `2013` annual `bank_indicator` backfill from JoinQuant
- fixing early-quarter rebalance-date construction
- rebuilding the full training panel from `2014-05-05` onward
- rerunning single-factor, improvement-factor, and multifactor incremental tests

## Base Core

- `indicator__roe`
- `indicator__eps`
- `derived__log_total_assets`
- `bank_indicator__Nonperforming_loan_rate`
- `bank_indicator__non_performing_loan_provision_coverage`
- `bank_indicator__deposit_loan_ratio`
- `bank_indicator__capital_adequacy_ratio`

This is the refreshed seven-factor base block.

Compared with `v2`, the biggest change is that the prudential asset-quality block moved to the center:

- `Nonperforming_loan_rate`
- `non_performing_loan_provision_coverage`

Both became much stronger after the early sample was restored.

At the same time, the prior base picks:

- `indicator__inc_net_profit_to_shareholders_annual`
- `bank_indicator__cost_to_income_ratio`
- `derived__investment_income_to_operating_revenue`

no longer justify unconditional core status in the refreshed sample.

## Enhancement Layer

- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue`

These are not part of the static base block. They are the current best two-factor enhancement layer.

The refreshed `top2` result is:

- baseline `combo__ic_weight`: validation IC `0.15537`
- plus NPL annual-improvement only: validation IC `0.262569`
- plus investment-income-ratio snapshot improvement only: validation IC `0.246092`
- both together: validation IC `0.302698`

So the current main candidate is best interpreted as:

- `7` base core factors
- `2` improvement enhancers

## Watch Layer

- `bank_indicator__non_interest_income_ratio`
- `bank_indicator__net_interest_margin`
- `indicator__inc_net_profit_to_shareholders_annual`
- `bank_indicator__cost_to_income_ratio`
- `bank_indicator__core_level_capital_adequacy_ratio`
- `derived__investment_income_to_operating_revenue`

These remain useful reserve candidates, but they should not be treated as automatic core members at this stage.

## Drop Layer

- `derived__staff_cash_to_operating_revenue`
- `income__minority_profit`

These should stay out of the current production candidate path unless a later rolling test clearly overturns the present evidence.

## Practical Next Step

The next modeling step should use:

1. the `7`-factor base core as the refreshed baseline
2. the `2` improvement enhancers as the first official augmented model
3. rolling pre-2021 validation on top of this `7+2` candidate rather than on the older `v2` base block
