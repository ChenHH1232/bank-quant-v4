# Mean Reversion V1 Strategy Spec

This spec defines the first executable mean-reversion strategy candidate under the current research discipline.

## Strategy Goal

Validate whether the confirmed short-horizon bank mean-reversion signal can work as a standalone tactical layer before integrating it into the broader bank allocation system.

## Signal Freeze

Primary signal:
- `rev5_abnvol = -0.7 * rev_5d + 0.3 * abnormal_volume_ratio`

Backup signal:
- `rev_5d`

Signal interpretation:
- lower score is better
- the preferred names are recent short-term losers with abnormal volume support, because they show the strongest rebound evidence in current research

## Universe And Filters

Base universe:
- listed A-share bank stocks only

Hard filters:
- exclude non-tradable names
- exclude recently listed names that do not have enough lookback window
- exclude names with insufficient recent price history

Trading gate:
- keep the same liquidity and market-cap control logic already used in the bank research stack
- this gate is a control layer, not the alpha source

## Portfolio Construction

Standalone V1:
- rank all eligible names by `rev5_abnvol`
- select the best `N` names with the lowest scores
- equal weight among selected holdings

Recommended first `N`:
- start from `5`
- if turnover is too concentrated, test `7`

Why equal weight first:
- the current goal is to validate signal quality, not optimize sizing
- equal weight makes attribution cleaner

## Execution Rhythm

Recommended V1 default:
- signal observation: daily
- rebalance check: daily
- trade only when the ranking meaningfully changes or a holding exits the eligible set

Fallback version:
- signal observation: daily
- rebalance execution: weekly

Why not monthly:
- current evidence points to short-horizon repair
- monthly execution is likely to react too slowly for a `rev_5d`-driven signal

## Research Discipline

Do not do in V1:
- do not retune coefficients on the frozen post-2021 acceptance window
- do not mix fundamentals, momentum, and reversion into one composite score immediately
- do not treat the standalone tactical result as proof that it should replace the annual backbone

Use instead:
- train and test conclusions to set the first executable rule
- post-2021 window only as acceptance and behavior observation unless a new validation protocol is defined in advance

## Promotion Path

If standalone V1 behaves acceptably:
- next step is not to replace momentum or fundamentals
- next step is to test mean reversion as an entry and rotation overlay within the higher-level approved pool

The preferred promotion order is:
1. standalone tactical validation
2. overlay on momentum-approved pool
3. overlay on annual backbone if attribution remains clear

## Immediate Build Order

Next implementation sequence:
1. build a standalone local backtest using this frozen spec
2. compare `daily execution` against `weekly execution`
3. summarize turnover, drawdown, and regime behavior
4. only then decide whether a JoinQuant executable version should be written
