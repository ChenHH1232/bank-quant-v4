# Fundamental Momentum Dual-Engine Rolling Plan V1

This document freezes the first research plan for testing a dual-engine portfolio construction layer that combines the archived fundamental line and the archived momentum line at the weight-allocation level.

## Objective

The purpose is not to merge fundamental and momentum factors into one raw score.

The purpose is:

- fundamental engine generates its own target weights
- momentum engine generates its own target weights
- portfolio layer combines the two weight vectors under fixed risk caps

This keeps the two research branches interpretable and avoids mixing their signals too early.

## Research Scope

Research scope is strictly limited to:

- pre-2021 rolling train/test only
- no use of the frozen `2021-05-31` onward JoinQuant out-of-sample window

This branch must remain fully inside train/test research until a fixed combination rule is chosen.

## Engine Inputs

### Fundamental Engine

Use the archived `7+2` candidate as the current fundamental reference line:

- `7` static core factors
- `2` improvement enhancers

Reference:
- [final_core_factor_pool_v3.md](D:\hh\codex\v4\phase_1_fundamental\final_core_factor_pool_v3.md)

### Momentum Engine

Use only archived momentum lines that are deployment-safe or research-safe:

- base deployment-safe momentum reference = `mom_12_1`
- optional research comparison line = `mom_6_1`

Do not use the original `state_score_v2` switch rule inside this dual-engine test, because that branch currently has an observability issue.

Reference:
- [momentum_stage_summary_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_stage_summary_v1.md)
- [momentum_state_switch_final_acceptance_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_final_acceptance_v1.md)

## First-Pass Construction Rule

### Step 1. Independent Cross-Sectional Scores

At each rebalance date:

- fundamental engine ranks the stock pool and converts rank into target weights
- momentum engine ranks the same stock pool and converts rank into target weights

Both engines should be normalized separately so that:

- each engine weight vector sums to `100%`
- each engine is interpretable on its own

### Step 2. Engine-Level Blend

Construct blended weight:

- `final_weight_raw = alpha * fundamental_weight + (1 - alpha) * momentum_weight`

First-pass fixed blend candidates:

- `alpha = 0.8`  -> `80% fundamental + 20% momentum`
- `alpha = 0.7`  -> `70% fundamental + 30% momentum`
- `alpha = 0.6`  -> `60% fundamental + 40% momentum`

These should be treated as fixed research candidates, not continuously optimized weights.

### Step 3. Weight Caps

Single-engine caps:

- max stock weight from fundamental engine = `5%`
- max stock weight from momentum engine = `5%`

Combined portfolio cap:

- final single-stock cap after blending = `8%`

If blended raw weight exceeds `8%`:

- clip at `8%`
- redistribute the overflow proportionally across the remaining eligible names

Total portfolio weight:

- normalize final weights back to `100%`

## Rebalance Rhythm

For the first test pass:

- use the same rebalance rhythm on both engines
- preferred first-pass rhythm = annual fundamental refresh plus monthly portfolio execution

This means:

- fundamental engine weights change only on annual refresh dates
- momentum engine weights can refresh monthly
- combined portfolio is updated monthly using the latest allowed engine outputs

## Rolling Validation Structure

Preferred first-pass protocol:

- `5y train + 2y test`

Use the same rolling discipline already established elsewhere:

- each fold selects only from information available inside its train window
- test window is held fixed
- no fold may use later information from outside its own train segment

If data coverage limits a strict `5y + 2y` implementation on a specific panel:

- document the feasible variant explicitly
- do not silently shorten the window without recording it

## Baselines To Compare

Each dual-engine blend must be compared against:

1. pure fundamental baseline
2. pure momentum baseline
3. fixed-weight dual-engine blends

Minimum baseline set:

- fundamental only
- momentum only
- `80/20`
- `70/30`
- `60/40`

## Evaluation Metrics

Primary metrics:

- test-period total return
- annualized return
- max drawdown
- sharpe-like risk-adjusted metric if available

Secondary diagnostics:

- turnover
- concentration
- overlap between the two engines
- contribution share from each engine

Interpretation priority:

- prefer stability over one-off peak return
- a dual-engine blend only earns promotion if it improves robustness versus both single-engine baselines

## What To Avoid

- do not merge fundamental and momentum factors into one score at this stage
- do not tune blend ratios on the frozen post-2021 out-of-sample window
- do not let the momentum state-switch branch leak into this test before the observability issue is resolved
- do not treat a higher average return alone as enough if drawdown or concentration deteriorates sharply

## Deliverables

The first implementation pass should produce:

1. one rolling test script
2. one fold-level result csv
3. one summary md
4. one short conclusion note stating whether dual-engine blending is worth continuing
