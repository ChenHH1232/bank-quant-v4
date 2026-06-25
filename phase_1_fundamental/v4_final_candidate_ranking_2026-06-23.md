# V4 Final Candidate Ranking 2026-06-23

Date: `2026-06-23`

This note freezes the current ranking after the latest JoinQuant execution checks for:

- pure `balanced`
- pure `core_level_shadow`
- `balanced + shortbond overlay`
- `core_level_shadow + shortbond overlay`

## Current Ranking

### 1. `core_level_shadow + shortbond overlay`

Current best overall branch.

Key points:

- strategy return = `53.17%`
- annualized return = `9.20%`
- excess return = `27.79%`
- alpha = `0.054`
- sharpe = `0.313`
- information ratio = `0.791`
- max drawdown = `21.68%`
- excess max drawdown = `7.15%`
- volatility = `0.166`

Interpretation:

- this branch is no longer just a defensive variant
- it improves return, excess return, Sharpe, IR, and absolute drawdown at the same time
- it also preserves the strongest relative-path profile in the current candidate set

### 2. `balanced + shortbond overlay`

Strong upgraded branch, but clearly second to the core-level overlay version.

Key points:

- strategy return = `51.41%`
- annualized return = `8.94%`
- excess return = `26.32%`
- alpha = `0.051`
- sharpe = `0.290`
- information ratio = `0.731`
- max drawdown = `21.83%`
- excess max drawdown = `11.66%`

Interpretation:

- this branch beats pure `balanced` on return, excess return, Sharpe, IR, and absolute drawdown
- but it is weaker than `core_level_shadow + shortbond overlay`, especially on relative-path risk

### 3. Pure `core_level_shadow`

Still a strong pure-fundamental branch, but now dominated by its overlay-enhanced version.

Key points:

- annualized return = `8.43%`
- excess return = `23.46%`
- excess max drawdown = `6.89%`
- information ratio = `0.647`

Interpretation:

- this remains the best pure-fundamental branch on relative-path stability
- but the shortbond overlay version now lifts both return and risk-adjusted performance further

### 4. Pure `balanced`

Still the cleanest plain baseline, but no longer the leading execution version.

Key points:

- annualized return = `8.49%`
- excess return = `23.80%`
- sharpe = `0.233`
- max drawdown = `22.29%`
- excess max drawdown = `11.47%`

Interpretation:

- pure `balanced` remains useful as the simplest no-overlay benchmark
- but both overlay branches now outperform it in full JoinQuant execution

## Decision Impact On V4

Two major questions are now resolved:

- fixed momentum sleeve versions should not enter the formal main line
- shortbond overlay should no longer be treated as only an optional side study

Current evidence points clearly to:

- under this project's A-share bank sample and execution framework, momentum does not provide enough stable incremental alpha to enter the formal main line
- under the same project scope, shortbond overlay improves the leading pure-fundamental branches enough to become part of the formal candidate stack

## Formal Versions To Keep

Recommended formal versions:

- `core_level_shadow + shortbond overlay`
  - current first-ranked execution candidate
- `balanced + shortbond overlay`
  - second-ranked execution candidate
- pure `core_level_shadow`
  - plain no-overlay relative-path benchmark
- pure `balanced`
  - plain no-overlay simplicity benchmark

## Momentum Branch Disposition

Momentum dual-engine versions should remain outside the formal V4 default stack.

Why:

- pre-2021 rolling showed incremental promise
- but under this project's A-share bank sample, `mom_12_1` definition, and separate-sleeve execution framework, full-cycle JoinQuant execution shows the dominant effect is lower beta and lower volatility
- that came with weaker return, weaker excess return, and weaker alpha than the leading pure-fundamental and shortbond-overlay branches

Practical conclusion:

- momentum is not part of the default formal V4 combination set
- if retained at all, it should be retained only as a historical research reference, not a live front-line candidate

## Final Framing

The V4 architecture now separates into three jobs:

- pure fundamental
  - defines the stock-selection core
- shortbond overlay
  - handles absolute-risk control and can improve the best execution branches
- rejected momentum stack
  - no longer enters the formal default candidate hierarchy
