# Fundamental Momentum Layered Research Rule V1

Objective:
- freeze the research order for the `fundamental filter + momentum selector` branch
- keep the structure interpretable
- prevent weighting experiments from being mixed in before the equal-weight joint structure is properly judged

## Core Structural View

Current economic interpretation:

- fundamentals should decide `who is allowed into the candidate set`
- momentum should decide `which names are selected now`
- fundamentals are more stable and more suitable for long-horizon capital allocation
- momentum changes faster and is more suitable for entry ordering than for dominant weight assignment

So the preferred base structure is:

- full bank universe `U_t`
- fundamental candidate pool `F_t`
- final holding set `H_t`

Meaning:

- `U_t` -> quarterly fundamental filter -> `F_t`
- `F_t` -> monthly momentum ranking -> `H_t`

## Frozen First-Pass Research Structure

Quarterly layer:
- update fundamental composite score
- choose fundamental `Top 16` or `Top 20` as candidate pool

Monthly layer:
- compute momentum inside the candidate pool only
- first-pass momentum backbone = `mom_12_1`
- select momentum `Top 6`
- equal-weight final holdings

This is the frozen base version:

- `48 banks -> fundamental Top 16/20 -> momentum Top 6 -> equal weight`

## Required Equal-Weight Control Group Set

Before any weight-tilt experiment, the branch should be judged using these equal-weight strategy groups:

1. fundamental `Top 6` standalone strategy
2. momentum `Top 6` standalone strategy
3. fundamental filter plus momentum `Top 6` joint strategy

Expanded practical control set:

- quarterly fundamental `Top 16` equal-weight
- quarterly fundamental `Top 20` equal-weight
- direct momentum `Top 6`
- quarterly fundamental `Top 16` then momentum `Top 6`
- quarterly fundamental `Top 20` then momentum `Top 6`

These are the groups needed to answer:

- does the joint strategy beat pure fundamentals
- does the joint strategy beat pure momentum
- is the fundamental gate helpful or just restrictive

## Weighting Discipline

Do not begin with score-weighted final holdings.

First requirement:
- the equal-weight joint structure must first show clear value

Only after that may the branch move to:
- mild tilt
- not full score-proportional allocation

## Preferred Future Mild-Tilt Direction

If and only if the equal-weight joint structure proves worthwhile, the first weighting upgrade should be:

- `70%` equal-weight
- `30%` tilted by fundamental strength

Conceptually:

- momentum still decides selection
- fundamentals add a mild capital-allocation overlay

This is preferred over momentum-driven weight tilt because:

- fundamental scores are more stable
- momentum is better treated as a selector than as a dominant weight controller
- direct momentum weighting risks turning the strategy into a faster, more fragile, more chase-prone structure

## Current Process Rule

The branch should follow this order strictly:

1. judge the equal-weight layered structure
2. only if it proves useful, test mild fundamental tilt
3. do not test momentum-driven weight tilt before the above step is cleared

## Current Judgment

At the current stage:

- the layered structure is still a research branch
- it has not earned promotion over the stronger active state-routing candidate
- it should stay archived as a structured alternative until stronger evidence appears

## References

- [quarterly_fundamental_monthly_momentum_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\quarterly_fundamental_monthly_momentum_validation_note_v1.md)
- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
