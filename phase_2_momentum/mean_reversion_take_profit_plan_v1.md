# Mean Reversion Take-Profit Plan V1

This note defines the first draft for using mean-reversion logic as a take-profit or trim signal inside the bank strategy stack.

## Why This Direction Makes Sense

Current research already supports one side of the symmetry:
- short-term oversold names can show rebound tendency

The natural symmetric question is:
- can short-term overheated names show pullback tendency

If that holds, then mean reversion may help on the sell side through:
- take-profit
- partial trim
- pause on adding exposure

This is a better first interpretation than treating it as a pure reverse-alpha short signal, because the current bank framework is still long-only and execution-oriented.

## Core Hypothesis

The first sell-side hypothesis should be:

- when a holding becomes too hot in the short run, future short-window return can weaken
- therefore a short-horizon overheat signal may improve exit timing or trimming decisions

This should be tested as:
- sell discipline

not as:
- proof that the stock should be structurally excluded from the annual or momentum-approved pool

## Candidate Overheat Fields

The current local panel already supports a first-pass overheat branch.

Primary fields:
- `rev_5d`
  - buy-side interpretation: very low is good for rebound entry
  - sell-side interpretation: very high may indicate near-term overheat

- `abnormal_volume_ratio`
  - if recent volume spikes together with short-term rise, the move may be crowded

- `close_to_ma20`
  - if price is too far above the 20-day mean, there may be mean-reversion pressure

Secondary contextual fields:
- `intramonth_drawdown_20d`
  - can help distinguish smooth trend from unstable burst

- `volatility_20d`
  - can help identify noisy overheat versus cleaner trend persistence

## First Frozen Overheat Proxy

The first V1 overheat proxy should stay simple and symmetric with the current buy-side logic.

Recommended V1 proxy:
- `overheat_score_v1 = 0.6 * rev_5d + 0.2 * abnormal_volume_ratio + 0.2 * close_to_ma20`

Interpretation:
- higher is hotter
- hotter names are more likely to deserve partial trimming

Why this form:
- `rev_5d` stays the main anchor
- `abnormal_volume_ratio` captures crowded burst behavior
- `close_to_ma20` captures extension away from the short mean

## First Use Case

The first use case should be narrow:

- only apply this rule inside the approved long-only basket
- do not change the approved stock list itself
- use it only to decide whether to:
  - keep full size
  - trim part of the position
  - postpone adding new size

This keeps the rule aligned with the existing annual and momentum structure.

## Recommended V1 Action Rule

The first practical rule should be conservative:

- if a holding enters the top overheat bucket inside the approved basket:
  - trim part of the position, not all of it

Suggested first action:
- trim `30%` to `50%` of the position
- re-add only when the overheat condition fades or a separate re-entry rule triggers

Why not full exit first:
- in a strong upward phase, some hot names may remain strong
- full exit is more likely to overreact than partial trim

## Minimal Validation Plan

The first validation should compare:

1. baseline hold
- no take-profit overlay

2. partial take-profit overlay
- trim part of a holding when `overheat_score_v1` exceeds a high threshold inside the approved basket

Key things to evaluate:
- short-horizon forward return after overheat signal
- whether trimming reduces local drawdown
- whether trimming damages upside too much in strong trend years

## Success Standard

This branch is useful only if it improves at least one of:

- local drawdown after overheated states
- realized path smoothness
- risk-adjusted return of the approved basket

without causing too much damage to:
- upside capture in strong trend phases

## Current Recommendation

The current best next step is:

- treat `超涨回吐` as a candidate take-profit layer
- keep it partial and conservative
- validate it as a trim rule, not as a full sell-or-reject rule
