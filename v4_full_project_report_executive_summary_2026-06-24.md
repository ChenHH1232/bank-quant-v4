# V4 Executive Summary 2026-06-24

Date: `2026-06-24`

## 1. One-Sentence Conclusion

V4 should now be understood as a pure-fundamental bank-stock strategy family with independently managed risk control, where shortbond overlay has been promoted into the formal top-ranked execution stack and momentum / mean-reversion have been removed from the default main line.

## 2. What V4 Originally Tried To Do

The project did not begin as a narrow pure-fundamental strategy.

It began from a broader research thesis:

- fundamentals should provide the strategic stock-selection base
- momentum might add incremental alpha or improve the path
- mean reversion might improve entry timing
- defensive overlays might help control large drawdowns

So the early V4 mindset was closer to:

`fundamental core + momentum enhancement + tactical adjustment + optional defense`

By the end of the project, that structure no longer matched the evidence.

## 3. What Changed During Research

Three major evidence updates changed the project direction.

### 3.1 Pure Fundamental Became Stronger Than Expected

The pure-fundamental branch improved meaningfully after repeated rolling validation and JoinQuant execution checks.

The biggest structural improvement came from reducing the base factor set from `base_core_7` to `base_core_6`.

This was important because the improvement did not come from adding complexity.
It came from removing one drag factor and simplifying the stock-selection core.

That simplification produced two strong pure-fundamental branches:

- `balanced`
- `core_level_shadow`

These two became the stable center of gravity for the project.

### 3.2 Momentum Did Not Survive Execution-Level Validation

Momentum looked promising in parts of local rolling, especially in older out-of-sample windows.

But once the research standard was tightened, the decision rule became:

- local rolling can nominate a candidate
- JoinQuant executable results decide whether the candidate is accepted

Under that rule, fixed momentum sleeves did not survive.

When `40%` momentum was combined with either of the two leading fundamental branches, the structure was consistent:

- beta fell
- volatility fell
- absolute drawdown often improved somewhat
- but annualized return fell
- excess return fell
- alpha fell
- Sharpe fell

That means momentum behaved more like equity-risk dilution than like a true return enhancer.

So momentum was not rejected as a universal theory.
It was rejected in a narrower and more precise sense:

> under this project's A-share bank sample, `mom_12_1` definition, and independent sleeve execution framework, momentum did not show stable incremental value strong enough to enter the formal main line

### 3.3 Defensive Overlay Improved Enough To Become Formal

At first, shortbond overlay was treated as a defensive side branch.

Later JoinQuant checks changed that interpretation.

The two overlay-enhanced branches outperformed their plain pure-fundamental parents strongly enough that overlay could no longer be treated as merely optional:

- `balanced + shortbond overlay`
- `core_level_shadow + shortbond overlay`

Most importantly, the `core_level_shadow + shortbond overlay` branch improved:

- total return
- annualized return
- excess return
- alpha
- Sharpe
- information ratio
- drawdown behavior

That made it the formal first-ranked version rather than a defensive footnote.

## 4. Final Research Conclusions By Branch

### 4.1 Pure Fundamental Branch

Status: `accepted`

Core conclusion:

- pure fundamental is the real alpha engine of V4
- reducing from `base_core_7` to `base_core_6` improved the strategy
- the best pure-fundamental styles are now `balanced` and `core_level_shadow`

Interpretation:

- `balanced` is the cleaner, more direct default fundamental baseline
- `core_level_shadow` is the more risk-aware relative-path version

### 4.2 Momentum Branch

Status: `rejected from formal main line`

Core conclusion:

- momentum was useful as a research challenger
- momentum did not prove stable additive alpha in final executable validation
- fixed `40%` momentum sleeve should not enter the formal V4 production hierarchy

Interpretation:

- momentum can remain archived research
- it should not be part of the default deployed logic

### 4.3 Mean-Reversion / Overheat / Tactical Price Defense Branch

Status: `not promoted`

Core conclusion:

- these branches generated ideas and helped stress-test the main line
- but they did not produce sufficiently robust or execution-worthy improvement

Interpretation:

- useful as research diagnostics
- not suitable as formal V4 default components

### 4.4 Shortbond Defensive Overlay Branch

Status: `promoted`

Core conclusion:

- shortbond overlay is not just downside cosmetics
- in the final validated set, it materially upgrades the best fundamental branches

Interpretation:

- risk control should be handled independently
- overlay is now part of the top formal candidate stack

## 5. Methodology Corrections That Matter

V4 did not only improve because of new ideas.
It also improved because the research discipline became stricter.

The most important methodology corrections were:

- stop accepting local rolling results as sufficient evidence
- use JoinQuant executable results as the final acceptance layer
- distinguish stock-selection alpha from risk dilution effects
- separate relative-risk management from absolute-risk management
- stop adding new factors just because backtests looked better

This was a major maturity step for the project.

The working hierarchy is now:

1. local rolling finds candidates
2. JoinQuant validates executable reality
3. only then can a branch enter the formal ranking

## 6. Final Formal Ranking

The final current ranking is:

1. `core_level_shadow_shortbond_overlay`
2. `balanced_shortbond_overlay`
3. `pure core_level_shadow`
4. `pure balanced`

This ranking matters because it changes the interpretation of the whole project.

The final hierarchy is no longer:

- pure fundamental first
- defense optional

It is now:

- overlay-enhanced pure-fundamental branches first
- plain pure-fundamental branches second
- momentum and mean reversion archived outside the formal default stack

## 7. What This Means Operationally

The cleanest practical reading is:

- fundamental selection is the strategy engine
- shortbond overlay is the preferred risk-control layer
- momentum is not needed for the current formal version
- mean reversion is not needed for the current formal version

This also means V4 should no longer chase theoretical completeness.

The project does not need to prove that every classic quant component has a place.
It only needs to keep the components that survived the current evidence standard.

## 8. Recommended Talking Point For External Review

If this project is handed to another analyst or model, the most accurate short framing is:

> V4 started as a broader multi-idea bank strategy, but the accumulated rolling and JoinQuant evidence compressed it into a simpler and stronger structure: pure-fundamental stock selection is the effective alpha core, shortbond overlay is the preferred independent risk-control layer, and momentum / mean-reversion do not currently deserve a place in the formal main line.

## 9. Bottom Line

The deepest result of V4 is not just that one branch beat another.

It is that the project moved from a broad theory-driven structure to an evidence-driven structure:

- less theoretical completeness
- more empirical discipline
- less component stacking
- more separation between alpha generation and risk control

That is why the final V4 framework is stronger than the one it started with.
