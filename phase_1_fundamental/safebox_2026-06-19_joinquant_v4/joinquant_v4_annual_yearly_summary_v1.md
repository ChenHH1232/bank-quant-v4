# JoinQuant V4 Annual Yearly Summary V1

## Scope

- Summary base: `joinquant_v4_annual_attribution_v1.csv`
- Coverage: 2021 to 2025
- Strategy line: `primary`
- Purpose: compress 15 rebalances into a one-page annual review sheet

## Yearly Snapshot

| Year | Rebalances in log | Effective plan view | Style label | Core holdings |
| --- | --- | --- | --- | --- |
| 2021 | 2021-05, 2021-09, 2021-11 | `annual_01` | 优质城商行/零售行主导 | `002142`, `600036`, `601009`, `600926`, `601658`, `601838`, `600908` |
| 2022 | 2022-05, 2022-09, 2022-11 | `annual_01 -> annual_02` | 延续 early winners，年内加入规模因子 | `600036`, `002142`, `601009`, `600926`, `601838`, `600908`, `601658` |
| 2023 | 2023-05, 2023-09, 2023-11 | `annual_02 -> annual_03` | 从优质中型银行切向大行 | `601398`, `601288`, `601939`, `600036`, `601988`, `601825`, `601658`, `601077` |
| 2024 | 2024-05, 2024-09, 2024-11 | `annual_03 -> annual_04` | 大行核心延续，秋季叠加改善层 | `601398`, `601288`, `601939`, `601988`, `600036`, `601328`, `600016` |
| 2025 | 2025-05, 2025-09, 2025-11 | `annual_04 -> annual_05` | 大行主线延续，边缘持仓轮换 | `600036`, `601398`, `601288`, `601939`, `601988`, `601825`, `601077` |

## Year Notes

### 2021

- 全年都处于 `annual_01`，8 个因子完整参与评分。
- 组合几乎不换，核心就是：
  - `002142.XSHE`
  - `600036.XSHG`
  - `601009.XSHG`
  - `600926.XSHG`
  - `601658.XSHG`
  - `601838.XSHG`
  - `600908.XSHG`
- 这一年最像“优质城商行/零售行精选组合”。

### 2022

- 2022-05 仍然沿用 `annual_01`，到 2022-09 才切换到 `annual_02`。
- `annual_02` 把 `derived__log_total_assets` 纳入核心层，所以规模开始进入打分体系。
- 年内主组合仍比较稳定，但 `002839.XSHE` 在 5 月短暂进入，说明早期风格开始出现边缘松动。

### 2023

- 2023-05 仍是 `annual_02`，但 `601825.XSHG`、`601528.XSHG` 已进入组合。
- 2023-09 切到 `annual_03` 后，风格发生全样本最明显的跃迁：
  - `601398.XSHG`
  - `601288.XSHG`
  - `601939.XSHG`
  - `601988.XSHG`
  - `600036.XSHG`
- 可以把 2023 下半年理解为“资本充足率 + 存贷比 + 规模”驱动下的大行年。

### 2024

- 2024-05 仍然落在 `annual_03`。
- 2024-09 开始切到 `annual_04`，改善层重新回到主线。
- 大行核心没有动摇，但新增了：
  - `601328.XSHG`
  - `601187.XSHG`
  - `600016.XSHG`
- 这一年更像“高资本大行核心 + 改善层补位”的结构。

### 2025

- 2025-05 仍使用 `annual_04`，2025-09 起转入 `annual_05`。
- `annual_05` 继续保留大行核心，同时边缘位置在 `002142.XSHE` 与 `601658.XSHG` 之间轮换。
- 年底收敛出来的稳定内核是：
  - `600036.XSHG`
  - `601398.XSHG`
  - `601288.XSHG`
  - `601939.XSHG`
  - `601988.XSHG`
  - `601825.XSHG`
  - `601077.XSHG`

## What This Sheet Is Good For

- Fast annual review without rereading all rebalance logs
- Comparing style drift before and after each annual plan switch
- Preparing the next step of `primary` vs `benchmark` annual comparison

## Important Note

- The May rebalance in 2022, 2024 and 2025 still reflects the prior annual plan because the implementation determines the active plan using `factor_date`, not the actual rebalance date.
- So this yearly sheet describes what actually ran in JoinQuant, not what we might want theoretically after a future boundary adjustment.
