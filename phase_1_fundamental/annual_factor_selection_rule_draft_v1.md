# Annual Factor Selection Rule Draft V1

This draft freezes the current annual factor-refresh conclusions into a repeatable rule set for formal yearly backtests.

Scope:

- annual anchor = each year's realized May rebalance trading day
- rolling window = `5y train + 2y test + 1y review`
- factor pool = `final_core_factor_pool_v3.csv` plus `controlled_improvement_pool_v1.csv`
- selection refresh frequency = once per year
- review-year holding rule = freeze the selected factor set for the full next review year

Current evidence base:

- annual folds: `5`
- controlled factor universe size: `19`
- best base-only combo in annual review = `base_core_7 + combo__ic_weight_train`
- best 7+2 combo in annual review = `base_plus_top2_9 + combo__ic_weight_train`

Important freeze rules:

- `7+2` is a capacity ceiling, not a fill target
- if a factor does not pass the annual thresholds, do not backfill it just to reach `7` or `2`
- improvement layer can be `0`, `1`, or `2` factors in a given year
- annual factor selection must only use information available before that year's realized May rebalance date

## 1. Core Resident Layer

These are the factors that should be treated as the annual framework's default base backbone.

### A. Hard resident anchor

- `bank_indicator__capital_adequacy_ratio`

Reason:

- kept in `5/5` annual folds
- strongest evidence of cross-year stability
- should be treated as the first factor locked into the annual base set

### B. High-stability resident base layer

- `bank_indicator__core_level_capital_adequacy_ratio`
- `bank_indicator__deposit_loan_ratio`
- `derived__log_total_assets`

Reason:

- each kept in `4/5` annual folds
- they form the most stable second-tier base around the hard anchor
- they should enter the default annual candidate shortlist before lower-frequency base factors

Operational rule:

- these three factors are not forced into the yearly set
- but when they pass the annual threshold screen, they should have resident priority over lower-frequency rotation factors

### C. Medium-stability base support

- `bank_indicator__non_performing_loan_provision_coverage`

Reason:

- kept in `3/5` annual folds
- less stable than the resident base layer, but still materially more stable than the short-cycle rotation names

Operational rule:

- treat this as the first backup base factor after the resident set
- when annual thresholds are passed, it should usually be included before the lower-frequency rotation group

## 2. Annual Rotation Layer

These factors are not stable enough to be treated as annual residents, but they remain valid candidates for yearly refresh.

### A. Base rotation candidates

- `bank_indicator__Nonperforming_loan_rate`
- `indicator__eps`
- `indicator__roe`
- `bank_indicator__net_interest_margin`
- `bank_indicator__non_interest_income_ratio`

Interpretation:

- `bank_indicator__Nonperforming_loan_rate`, `indicator__eps`, and `indicator__roe` were each kept in `2/5` folds
- `bank_indicator__net_interest_margin` and `bank_indicator__non_interest_income_ratio` were each kept in `1/5` fold
- this group should not be made permanent
- it should be used as a rotation sleeve that fills the remaining base capacity only when the annual evidence is strong enough

Base fill order for formal backtests:

1. lock the hard resident anchor
2. add passing factors from the high-stability resident base layer
3. add `bank_indicator__non_performing_loan_provision_coverage` if it passes
4. rank the remaining base rotation candidates by annual `priority_score`
5. add them in descending order until the base layer reaches its current passing limit, capped at `7`

Practical implication:

- some review years may hold only `4` or `5` base factors
- this is acceptable and should be preserved in formal backtests
- annual_03 is the proof case that the framework should prefer quality over forced count

## 3. Improvement Supplement Layer

The improvement layer is now part of the framework, but only as a controlled yearly supplement.

### A. Controlled improvement pool

- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue`
- `improve__annual_delta__bank_indicator__capital_adequacy_ratio`
- `improve__season_yoy_delta__derived__staff_cash_to_operating_revenue`
- `improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual`
- `improve__snapshot_delta__indicator__eps`

### B. Current annual selection evidence

- annual_01: `Nonperforming_loan_rate annual delta` and `investment_income_to_operating_revenue snapshot delta`
- annual_02: `capital_adequacy_ratio annual delta` and `investment_income_to_operating_revenue snapshot delta`
- annual_03: no improvement factor passed into the final kept set
- annual_04: `Nonperforming_loan_rate annual delta` and `inc_net_profit_to_shareholders_annual snapshot delta`
- annual_05: `staff_cash_to_operating_revenue season_yoy delta` and `inc_net_profit_to_shareholders_annual snapshot delta`

Interpretation:

- improvement factors do have yearly value
- but the winners rotate substantially across years
- this supports a controlled annual re-screen, not a fixed permanent improvement pair

### C. Formal yearly supplement rule

1. evaluate only the controlled improvement pool
2. apply the same annual threshold screen used by the main refresh framework
3. rank passing improvement factors by annual `priority_score`
4. keep at most the top `2`
5. if no improvement factor passes, keep the improvement sleeve empty for that year

Priority interpretation:

- no improvement factor is permanent today
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue`
- `improve__annual_delta__bank_indicator__Nonperforming_loan_rate`
- `improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual`

These three have the best repeat evidence so far because they were each selected in `2/5` folds. They should be treated as first-watch names inside the controlled improvement pool, but not as forced annual inclusions.

## 4. Formal Backtest Execution Rule

Primary yearly strategy line:

- strategy shell = `base_plus_top2_9`
- actual selected count = `base 4-7` plus `improvement 0-2`
- yearly factor set = determined once at the realized May rebalance date, then frozen for the next review year
- primary combo = `combo__ic_weight_train`

Benchmark line:

- run `base_core_7 + combo__ic_weight_train` in parallel as the no-improvement benchmark

Reason:

- the annual evidence shows the best average review IC still belongs to the base-only line
- but the `7+2` shell remains the current main research direction because it preserves room for controlled yearly improvement supplementation
- keeping both lines in formal backtests will let us judge whether improvement factors add stable value or only episodic value

## 5. Frozen Annual Selection Template

Use the following decision order each year:

1. identify that year's realized May rebalance trading day
2. build the `5y train + 2y test + 1y review` fold ending at that date
3. run threshold screening on the full controlled factor universe
4. lock `bank_indicator__capital_adequacy_ratio` if it passes
5. add passing resident base factors in stability order
6. add the medium-stability support factor if it passes
7. use annual `priority_score` to fill remaining base slots up to `7`
8. use annual `priority_score` to fill improvement slots up to `2`
9. freeze the resulting factor set for the next review year
10. run both the primary `7+2` line and the base-only benchmark line

## 6. Draft Conclusion

The current annual rule draft is:

- one hard resident anchor: `bank_indicator__capital_adequacy_ratio`
- one resident base cluster: `core_level_capital_adequacy_ratio`, `deposit_loan_ratio`, `log_total_assets`
- one medium-stability support factor: `non_performing_loan_provision_coverage`
- one annual rotation sleeve for lower-frequency base factors
- one controlled yearly improvement sleeve with max `2` factors and no forced fill requirement

This is stable enough to freeze for the next formal backtest round without pretending the factor set is fully static across years.
