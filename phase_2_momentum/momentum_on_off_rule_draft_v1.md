# Momentum On-Off Rule Draft V1

Positioning:
- this draft defines how momentum should be `enabled`, `down-weighted`, or `disabled` inside the bank-stock framework
- it is intended for the next `pre-2021 rolling` validation round
- it is not a promoted deployment rule yet

## Core Question

The practical question is no longer:

- whether momentum exists at all

That part is already broadly answered.

The real question is:

- should momentum stay always-on in a long-only bank portfolio
- or should it be conditionally turned off in weak or non-trending environments

Current evidence suggests:

- always-on momentum is too blunt
- `mom_6_1` is especially vulnerable outside strong trend-up states
- `mom_12_1` is more stable, but still should not automatically consume allocation in weak environments

## Fixed Design Principle

The next rule should preserve three constraints:

- fundamentals and momentum remain separate engines
- state only controls the `momentum budget`, not the underlying fundamental stock-selection logic
- the state definition must use only information observable at the decision date

So the switch is a `portfolio-allocation rule`, not a new mixed factor model.

## Three-State Framework

The clean first draft is:

1. `strong_up`
2. `neutral_flat`
3. `weak_down`

The intended behavior is:

- `strong_up`: momentum on
- `neutral_flat`: momentum reduced
- `weak_down`: momentum off

## Proposed Allocation Mapping

For the next rolling research pass, use this fixed mapping first:

- `strong_up`: `60%` fundamental + `40%` momentum
- `neutral_flat`: `80%` fundamental + `20%` momentum
- `weak_down`: `100%` fundamental + `0%` momentum

Interpretation:

- the goal is not to predict exact returns
- the goal is to stop forcing momentum capital into environments where its pre-2021 evidence is weak
- this also keeps the research close to the dual-engine framework we already validated

## Why This Mapping

This mapping follows the current evidence:

- pure or high-usage `mom_6_1` works mainly in trend-up years
- middle-state months should not be pushed toward aggressive momentum
- slower `mom_12_1` is safer than `mom_6_1`, but still not obviously worth a constant fixed budget in weak states
- the dual-engine `60/40` blend already showed first-pass portfolio-construction value

So the draft is intentionally conservative:

- only give the full momentum budget in clearly favorable states
- cut the budget in uncertain states
- shut momentum off in weak states instead of trying to rescue it with more complexity

## State Definition Guidance

The state variable should be chosen under a strict observability rule.

Allowed direction:

- cross-sectional or market-wide metrics known at the rebalance date
- examples: bank-pool momentum breadth, positive-ratio breadth, market-cap structure, liquidity structure, slow trend filters

Not allowed:

- any state input defined from next-period returns
- any forward dispersion term that is only known after the rebalance decision

This is the main lesson from the earlier `state_score_v2` research loop.

## First Research Candidate

The first candidate should not invent a brand-new complex state score immediately.

Instead, reuse the already-supported interpretation:

- if observable trend-state proxy is clearly high: classify as `strong_up`
- if clearly weak: classify as `weak_down`
- otherwise: classify as `neutral_flat`

That means the first validation round should focus on:

- whether `off / low / full` momentum budgeting helps
- not on over-optimizing the state formula itself

## Validation Protocol

The next validation should stay fully inside `pre-2021`.

Recommended protocol:

- keep the existing train/test rolling discipline
- estimate state thresholds only on the training segment
- apply the allocation rule unchanged on the test segment
- compare against:
- pure fundamental
- fixed `60/40` dual engine
- pure `mom_12_1` momentum line
- state-gated dual engine

Primary evaluation target:

- whether the state-gated dual engine improves return retention relative to pure fundamental
- while keeping drawdown materially better than an always-on momentum blend

## Current Expected Outcome

The most realistic expectation is:

- this rule will probably not become the top raw-return line
- but it may become the cleaner low-drawdown allocation version of the bank strategy stack

In other words:

- pure fundamental remains the main return-seeking line
- state-gated dual engine becomes a candidate for a more defensive allocation sleeve

## Immediate Next Step

The next concrete task should be:

- build `state-gated dual-engine rolling validation v1`

Its first purpose is simply to answer:

- does `momentum off in weak states` beat `always-on 60/40`

If yes, then we can justify a second pass on better observable state definitions.

## References

- [momentum_pre2021_state_review_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_pre2021_state_review_v1.md)
- [momentum_state_switch_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_candidate_v1.md)
- [momentum_state_switch_final_acceptance_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_state_switch_final_acceptance_v1.md)
- [fundamental_momentum_dual_engine_rolling_plan_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_plan_v1.md)
- [fundamental_momentum_dual_engine_rolling_test_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_dual_engine_rolling_test_v1.md)
