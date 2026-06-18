# JoinQuant V4 Annual Attribution V1

## Scope

- Backtest window in the current log: 2021-05-31 to 2025-11-03
- Strategy line: `primary`
- Rebalance cadence: May, September, November
- Source log: desktop temporary log file `临时文件.txt`
- Detail table: `joinquant_v4_annual_attribution_v1.csv`

## Overall Takeaways

- The JoinQuant strategy is now running normally. The first two years are no longer empty because the bank indicator layer has been replaced with embedded annual static data.
- Annual plan switching is working. The log shows an orderly progression from `annual_01` through `annual_05`.
- The style path is clear: the early stage leans toward high-quality city banks and retail banks, then shifts toward large state-owned banks from `annual_03`, and later adds a controlled improvement layer back in `annual_04` and `annual_05`.
- The strategy is target-value equal weight in logic, but actual fills are slightly perturbed by the A-share board-lot rule of 100 shares.

## Plan Timeline

| Plan | Rebalance dates in log | Main factor structure | Holding style snapshot |
| --- | --- | --- | --- |
| `annual_01` | 2021-05-31, 2021-09-01, 2021-11-01, 2022-05-05 | 4 bank indicators + `eps` + `roe` + 2 improvement factors | Stable focus on `002142`, `600036`, `601009`, `600926`, `601658`, `601838`, `600908` |
| `annual_02` | 2022-09-01, 2022-11-01, 2023-05-04 | `annual_01` base plus `derived__log_total_assets`, improvement layer changes to annual delta of capital adequacy ratio | Keeps the core winners, then starts to admit `601825` and `601528` |
| `annual_03` | 2023-09-01, 2023-11-01, 2024-05-06 | `capital_adequacy_ratio` + `deposit_loan_ratio` + `log_total_assets` | Clear shift toward large banks: `601398`, `601288`, `601939`, `601988`, `600036` |
| `annual_04` | 2024-09-02, 2024-11-01, 2025-05-06 | `capital_adequacy_ratio` + `log_total_assets` + 2 improvement factors | Large-bank core remains, while `601328`, `601187`, `600016`, `601169` rotate in |
| `annual_05` | 2025-09-01, 2025-11-03 | 3 bank indicators + `log_total_assets` + 2 improvement factors | Large-bank core remains strong, with `601825`, `601658`, `601077` around the edge |

## Plan Notes

### `annual_01`

- First rebalance top names on 2021-05-31:
  - `002142.XSHE`, `600036.XSHG`, `601009.XSHG`, `600926.XSHG`, `601658.XSHG`, `601838.XSHG`, `600908.XSHG`
- This plan was highly stable across 2021-05, 2021-09 and 2021-11.
- On 2022-05-05, `002839.XSHE` replaced `601658.XSHG`, which is the first visible material holding change.

### `annual_02`

- Added `derived__log_total_assets`, so size became part of the core scoring layer.
- 2022-09 and 2022-11 were still dominated by the same seven names from the prior phase.
- By 2023-05-04, `601825.XSHG` and `601528.XSHG` entered the long book, signaling expansion beyond the original early winners.

### `annual_03`

- This is the cleanest style regime in the whole sample.
- With only 3 factors active, the strategy became strongly biased toward large banks with better capital metrics and lower deposit-loan pressure.
- The resulting long book was extremely stable:
  - `601398.XSHG`, `601288.XSHG`, `601939.XSHG`, `600036.XSHG`, `601988.XSHG`, `601825.XSHG`, `601658.XSHG`, `601077.XSHG`

### `annual_04`

- Improvement factors returned, but the large-bank tilt remained.
- The first rebalance on 2024-09-02 brought in:
  - `601328.XSHG`, `601187.XSHG`, `600016.XSHG`
- By 2025-05-06, the edge names shifted again and `601169.XSHG` replaced `600016.XSHG`.

### `annual_05`

- Bank-indicator coverage was simplified to 3 static bank variables plus size and 2 improvement factors.
- The core book remained:
  - `600036.XSHG`, `601398.XSHG`, `601288.XSHG`, `601939.XSHG`, `601988.XSHG`
- Edge rotation switched between `002142.XSHE` and `601658.XSHG`, while `601825.XSHG` and `601077.XSHG` stayed in the group.

## Important Implementation Note

- The 2022-05-05 rebalance still uses `plan=annual_01`, because the current implementation determines the active plan using the previous trading day factor date `2022-04-29`, not the actual rebalance date `2022-05-05`.
- This is an implementation choice, not a runtime error.
- If we want the new annual plan to take effect on the May rebalance itself, we should later decide whether to switch the plan boundary from `factor_date` to actual rebalance date.

## Next Suggested Use

- Use `joinquant_v4_annual_attribution_v1.csv` as the base table for annual attribution review.
- When we run the next formal comparison, directly add:
  - `primary` vs `benchmark`
  - with-improvement vs without-improvement
  - year-by-year return and drawdown split
