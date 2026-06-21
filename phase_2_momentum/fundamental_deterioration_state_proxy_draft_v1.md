# Fundamental Deterioration State Proxy Draft V1

Positioning:
- this draft proposes a stronger observable state layer for the bank dual-engine framework
- the focus is no longer only price-state or liquidity-state
- the new direction is to measure whether bank fundamentals are broadly getting worse

## Core Idea

The key hypothesis is:

- if a large share of bank stocks are showing worsening fundamental composite scores
- and the deterioration is broad rather than isolated
- then the market environment may be structurally weak for bank-equity risk-taking

This could help explain weak states more economically than a pure price-breadth proxy.

## Why This Matters

Current evidence says:

- fixed `60/40` beats both state-gated bank-only fallback and state-gated bond-switch fallback
- so the main bottleneck is probably not the fallback destination
- the bottleneck is more likely `state recognition quality`

A deterioration-based state proxy may improve that because it asks:

- are bank fundamentals still healthy and broadening
- or are they weakening across the universe

## Base Measurement Object

The natural base object is:

- the current bank `fundamental composite score`

For the current main line, this should start from:

- `base_plus_top2_9`
- with the same production candidate combo backbone we already use in rolling research

The state layer should not change the stock-picking engine itself.

It should only observe:

- how those scores are changing across the cross-section

## First Candidate Features

The first feature set should stay simple and fully observable.

### Breadth Features

- `deterioration_ratio_1`
- definition: share of stocks whose current composite score is below the previous annual refresh score

- `deterioration_ratio_2`
- definition: share of stocks whose current composite score change is below `0`

- `severe_deterioration_ratio`
- definition: share of stocks whose score drop is below the cross-sectional median drop threshold or a fixed negative threshold

Interpretation:

- these tell us how widespread the weakening is

### Magnitude Features

- `score_delta_mean`
- definition: cross-sectional mean of current-minus-reference composite score

- `score_delta_median`
- definition: cross-sectional median of current-minus-reference composite score

- `score_delta_bottom_quartile_mean`
- definition: average score change among the worst `25%` deteriorating stocks

Interpretation:

- these tell us how deep the deterioration is

### Dispersion Features

- `score_delta_std`
- definition: cross-sectional standard deviation of score changes

- `score_delta_top_bottom_spread`
- definition: top quartile minus bottom quartile of score changes

Interpretation:

- these tell us whether weakness is broad and synchronized or just concentrated in a few names

## Reference Point Choice

This is the most important implementation decision.

The safest first-pass choice is:

- compare current score against the most recent annual or quasi-quarterly fundamental refresh baseline already known at that date

That means:

- for a given month after the May refresh, use the refreshed annual composite score as the anchor
- then observe whether later monthly conditions imply deterioration relative to that anchor

This keeps the state layer:

- observable
- economically interpretable
- aligned with the bank fundamental engine

## Preferred First-Pass Proxy

The cleanest first-pass combined proxy should likely use:

- `deterioration_ratio_1`
- `score_delta_mean`
- `score_delta_bottom_quartile_mean`

Why this trio:

- one breadth measure
- one central tendency measure
- one tail-damage measure

That is usually enough for a first rolling test without making the state score too fragile.

## State Classification Logic

The first-pass classification can stay parallel to the earlier framework:

- `strong_up`
- `neutral_flat`
- `weak_down`

But now the interpretation becomes:

- `strong_up`: limited deterioration, or broad improvement
- `neutral_flat`: mixed or shallow deterioration
- `weak_down`: broad and deep deterioration

The practical mapping can still remain:

- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => fallback variant under test

## Observable Discipline

This proxy must obey strict timing discipline:

- only use score information available at the rebalance date
- do not use next-period realized returns
- do not use future-refreshed fundamental values as the reference anchor

So any score comparison must be:

- current observable score
- versus last already-known baseline score

not:

- current score versus a future annual recomputation

## First Validation Plan

The next implementation should build:

- one local panel with date-level deterioration features

Then test three competing state proxies under the same pre-2021 rolling protocol:

1. current momentum-state observable proxy
2. fundamental deterioration proxy
3. combined proxy

The question is:

- does deterioration-based state recognition beat price-breadth-only state recognition

## Practical Priority

The first coding step should be:

- build a dated panel of fundamental composite score changes by stock

Then aggregate those stock-level changes into:

- breadth
- mean
- median
- bottom-tail deterioration

Only after that should we decide how to z-score and combine them.

## Current Judgment

This is currently the most promising next observable-state direction because:

- it stays inside the bank strategy logic
- it uses information we already compute
- it is more economically grounded than pure market-structure proxies
- it directly addresses your concern that weak states may show up first as broad fundamental weakening

## References

- [pre2021_rolling_validation_v1.md](D:\hh\codex\v4\phase_1_fundamental\pre2021_rolling_validation_v1.md)
- [state_gated_dual_engine_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\state_gated_dual_engine_validation_note_v1.md)
- [defensive_bond_switch_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\defensive_bond_switch_validation_note_v1.md)
