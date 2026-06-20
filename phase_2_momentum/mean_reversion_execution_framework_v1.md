# Mean Reversion Execution Framework V1

This document converts the current mean-reversion research findings into a first executable framework that can later be implemented in JoinQuant or local backtests without changing the research口径.

## Role In The Full System

Current role definition:
- fundamentals remain the annual backbone
- momentum remains the medium-horizon style and trend layer
- mean reversion is not a third annual-updated backbone
- mean reversion should be treated as a short-horizon tactical execution layer

Practical interpretation:
- fundamentals answer `what can we hold this year`
- momentum answers `which names deserve relative overweight in this phase`
- mean reversion answers `when to add, trim, or rotate inside the approved pool`

## Current Evidence Base

Already confirmed:
- `rev_5d` is the first effective short-horizon bank mean-reversion signal
- direction is `smaller_better`
- `rev_10d` and `rev_20d` do not behave like robust pure reversion in the current research window
- `rev5_abnvol = -0.7 * rev_5d + 0.3 * abnormal_volume_ratio` is the strongest current composite
- anchored validation shows `rev5_abnvol` is slightly but consistently better than raw `rev_5d`

Current safe conclusion:
- the research supports a short-horizon selloff-repair signal
- the research does not yet support a slow monthly or annual mean-reversion backbone

## Recommended Operating Rhythm

Recommended first executable rhythm:
- factor library update rhythm: annual, aligned with the existing yearly research refresh process
- parameter refresh rhythm: annual
- signal calculation rhythm: monthly refresh of candidate set plus daily monitoring of trigger signal
- execution rhythm: daily

Why this is the best first fit:
- the factor research itself can still be reviewed and frozen annually like the other branches
- but the signal acts on short-lived dislocations, so monthly-only execution is likely too slow
- daily execution is more consistent with the confirmed `rev_5d` horizon

Fallback rhythm if daily execution is too noisy:
- keep the same annual update framework
- downgrade execution from daily to weekly
- use this only as a stability fallback, not as the default research interpretation

## Recommended First Version

V1 execution proposal:
- stock universe: bank universe only
- structural pool: inherit the existing bank investable universe construction
- liquidity and market-cap control: continue using the existing liquidity and market-cap restriction logic as a trading gate
- alpha signal: rank by `rev5_abnvol`
- fallback signal: use raw `rev_5d` if `abnormal_volume_ratio` is missing
- holding logic: select the strongest rebound candidates among recent short-term losers

Recommended first ranking logic:
- first filter names that pass tradability, listing-age, liquidity, and size gates
- then compute `rev5_abnvol`
- lower score means stronger reversion candidate
- buy the best-ranked names inside the eligible bank pool

## Relationship With Fundamentals And Momentum

The cleanest first integration is layered, not blended:

Layer 1:
- fundamentals decide the yearly approved bank set

Layer 2:
- momentum decides medium-horizon preference inside that set

Layer 3:
- mean reversion decides short-horizon entry and rotation timing

What should not be done in V1:
- do not blend annual fundamental score, monthly momentum score, and daily reversion score into one single composite immediately
- do not reinterpret mean reversion as a long-horizon stock-picking backbone
- do not retune the mean-reversion rule directly on the frozen post-2021 out-of-sample window

## Recommended V1 Implementation Paths

There are two valid implementation paths.

Path A: standalone mean-reversion strategy
- purpose: isolate the tactical signal and validate its pure contribution
- rebalance logic: short-horizon tactical switching inside the bank universe
- benefit: easiest to interpret
- cost: does not yet leverage the approved annual backbone

Path B: execution overlay on top of annual or momentum-approved pool
- purpose: use mean reversion only as an entry and rotation overlay
- rebalance logic: only trade names inside the higher-level approved pool
- benefit: best fit with the current multi-layer architecture
- cost: attribution becomes less clean

Recommended order:
- first do Path A locally to verify the tactical layer cleanly
- then promote to Path B once the execution behavior is understandable

## V1 Parameter Freeze Suggestion

For the next step, freeze the first executable spec as:
- main signal: `rev5_abnvol`
- backup signal: `rev_5d`
- execution frequency candidate 1: daily
- execution frequency candidate 2: weekly if daily turnover is too high
- refresh cadence for selected signal family: annual
- validation discipline: keep using train and test evidence first, treat `2021-05-31` onward as acceptance-only unless a separate protocol is defined

## What To Build Next

Immediate next deliverables:
- a short design note comparing `monthly update + daily execution` versus `monthly update + weekly execution`
- a first local executable backtest spec for standalone mean reversion
- a JoinQuant-ready tactical strategy skeleton if the standalone local logic looks stable

Suggested order:
1. freeze the execution framework in this document
2. define the exact V1 signal and trading rule
3. run the first standalone tactical backtest
4. only after that decide whether to overlay it onto the annual backbone

## Current Recommendation

The current best working assumption is:
- mean reversion should be `annual research refresh + short-horizon execution`
- the first live candidate should be `rev5_abnvol`
- execution should start from `daily` rather than `monthly`
- integration with fundamentals and momentum should happen as an overlay later, not in the first test
