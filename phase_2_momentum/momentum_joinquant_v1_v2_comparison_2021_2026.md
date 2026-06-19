# JoinQuant Monthly Momentum V1 vs V2 Comparison

Scope:
- backtest window: `2021-05-31` to `2026-05-29`
- benchmark: `512800.XSHG`
- execution frequency: monthly, each month first actual trading day
- portfolio construction: equal-weight top bucket inside the filtered bank pool

Strategy definitions:
- `v1` = [joinquant_v4_monthly_momentum_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_monthly_momentum_strategy_v1.py)
  - annual offline factor plan
  - raw factor scoring only
  - no cross-sectional neutralization
- `v2` = [joinquant_v4_monthly_momentum_strategy_v2.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_monthly_momentum_strategy_v2.py)
  - same annual offline factor plan
  - same monthly execution
  - add cross-sectional neutralization on `log(avg_money_20d_pre_rebalance)` and `log(avg_market_cap_20d_pre_rebalance)`

Data sources used for this comparison:
- `v1` equity curve: `C:\Users\Administrator\Downloads\result_1 (4).csv`
- `v2` equity curve: `C:\Users\Administrator\Downloads\result_1 (5).csv`
- `v2` runtime log sample: [runtime_log_sample](C:\Users\Administrator\Desktop\临时文件.txt)

## Runtime Check

`v2` runtime log confirms three points:
- monthly rebalancing executed normally
- positions were actually built from `2021-05-31`
- neutralized selection was active, not falling back to raw scoring in the first observed months

Example log evidence from `2021-05-31`:
- `selected_factor=mom_12_1_neu`
- `selection_mode='offline_annual_factor_plan_neutralized'`
- `used_raw_fallback=0`
- `candidate_count=19`
- `selected_count=4`

So this experiment is a valid `v1` vs `v2` strategy comparison, not a failed run.

## Total Return Comparison

Full-period result:

| strategy | strategy return | benchmark return | excess return |
| --- | ---: | ---: | ---: |
| `v1` raw | `33.84%` | `19.86%` | `11.66%` |
| `v2` neutralized | `29.28%` | `19.86%` | `7.86%` |

Direct reading:
- `v2` underperformed `v1` by `4.56pct` in total strategy return
- `v2` underperformed `v1` by `3.80pct` in excess return

Extreme excess observations:

| strategy | min excess | min excess date | max excess | max excess date |
| --- | ---: | --- | ---: | --- |
| `v1` | `-10.43%` | `2021-07-28` | `31.77%` | `2024-04-18` |
| `v2` | `-12.30%` | `2021-12-30` | `24.32%` | `2024-04-08` |

## Monthly Up/Down Market Read

Method:
- JoinQuant export columns are cumulative return percentages, not monthly return series
- monthly statistics below are computed by first converting cumulative return into net value, then taking month-end to month-end return
- complete month count used here: `60`

Up-market months:

| strategy | months | avg benchmark month | avg strategy month | avg monthly excess | up capture | excess win rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `v1` | `28` | `4.1585%` | `4.2523%` | `0.0938%` | `1.0225` | `46.43%` |
| `v2` | `28` | `4.1585%` | `3.9973%` | `-0.1612%` | `0.9612` | `50.00%` |

Down-market months:

| strategy | months | avg benchmark month | avg strategy month | avg monthly excess | down capture | excess win rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `v1` | `31` | `-2.9516%` | `-2.5535%` | `0.3981%` | `0.8651` | `54.84%` |
| `v2` | `31` | `-2.9516%` | `-2.4160%` | `0.5356%` | `0.8186` | `61.29%` |

Interpretation:
- `v1` is slightly better in rising months and still keeps some downside control
- `v2` improves downside behavior a bit
- but `v2` gives up the more important upside participation that we currently want from the momentum line

## Decision

Current judgment:
- `v1` should remain the monthly momentum execution baseline
- `v2` should be recorded as a negative validation result for the current objective

Reason:
- our current research target is not just `more stable`
- it is specifically `can the momentum line clearly outperform the benchmark in rising environments`
- on that criterion, `v2` did not improve and in fact weakened the offensive profile

## What This Means For The Mainline

The present evidence supports:
- keep `v1` as the active JoinQuant monthly momentum baseline
- keep `v2` only as an archived branch of evidence showing that direct liquidity-and-size neutralization did not help this deployment version
- continue next tests from the `v1` direction, especially around factor mix and refresh logic, rather than promoting `v2`

Likely next research directions:
- test a more `6-1`-centered annual factor plan
- test whether `12-1` is acting as a hidden slow-style filter rather than pure bank momentum
- keep monthly execution, but leave factor refresh annual unless a later experiment shows clear benefit
