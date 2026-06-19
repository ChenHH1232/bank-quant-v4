# Momentum Candidate Pool Draft V1

This draft freezes the current first-round momentum conclusions into a repeatable candidate rule for the next rolling-validation stage.

Scope:

- annual anchor = each year's realized first May trading day
- training / validation structure = `5y train + 2y validation`
- stock-pool rule = at each annual rebalance date, keep only stocks that are both top `80%` by prior-20-trading-day average traded amount and top `80%` by prior-20-trading-day average market cap
- evidence base = `momentum_single_factor_test_results_v2.csv`

## 1. Primary Momentum Candidate

- `mom_12_1`

Reason:

- current annual v2 status = `A`
- validation direction = `larger_better`
- validation rank IC = `0.283851`
- validation top-minus-bottom spread = `0.21953049`
- compared with plain `mom_12m`, the skip-one-month version is clearly stronger and avoids the recent-short-term contamination that likely hurts raw 12-month momentum

Operational rule:

- treat `mom_12_1` as the default lead momentum signal in the next rolling framework
- if only one momentum signal is allowed into a formal trial shell, use this one first

## 2. Secondary Rotation Candidates

- `mom_6_1`
- `mom_3m`

Reason:

- both reached current annual v2 status = `A`
- `mom_6_1` keeps the same “skip recent month” logic as `mom_12_1`, which makes it a useful supporting comparison candidate
- `mom_3m` passed under the relaxed annual small-sample rule, but its validation spread is weak and close to flat, so it should be treated as a lower-conviction rotation name rather than a resident signal

Operational rule:

- `mom_6_1` should be the first backup momentum signal behind `mom_12_1`
- `mom_3m` can stay in the research rotation sleeve, but should not outrank `mom_12_1` or `mom_6_1`

## 3. Supportive Non-Alpha Constraint

- `liq_money_1m`

Reason:

- current annual v2 status = `A`
- validation rank IC = `0.261793`
- validation spread = `0.2103603`
- in this branch it behaves like a strong tradability-aware support signal, but its more important role is still as a stock-pool and execution-quality constraint

Operational rule:

- keep `liq_money_1m` as a formal support variable in the rolling framework
- it can be tested both as:
  - a pure stock-pool constraint
  - a supportive ranking adjustment variable beside the primary momentum signal
- do not let it replace `mom_12_1` as the main momentum thesis

## 4. Current Excluded or Watch-Only Names

- `mom_12m`
- `mom_1m`
- `mom_6m`
- `liq_turnover_1m`

Reason:

- all four are `C` in the current annual v2 table
- `mom_12m` is especially important because it loses clearly against `mom_12_1`
- this supports the view that the current signal is not “raw momentum everywhere”, but a more selective medium-horizon momentum structure with a skip-recent-month adjustment

Operational rule:

- keep these names in the research watch layer
- do not place them into the first formal momentum execution shell unless later rolling evidence upgrades them

## 5. Frozen Draft Conclusion

The current momentum draft is:

- one primary candidate: `mom_12_1`
- one first backup candidate: `mom_6_1`
- one lower-conviction rotation candidate: `mom_3m`
- one supportive liquidity variable: `liq_money_1m`
- one watch-only raw long-horizon comparison name: `mom_12m`

This is strong enough to freeze as the momentum branch's first rolling-validation shortlist.
