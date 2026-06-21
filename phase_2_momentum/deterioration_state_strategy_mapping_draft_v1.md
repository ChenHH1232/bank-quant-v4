# Deterioration State Strategy Mapping Draft V1

Objective:
- freeze a simple execution-facing mapping from annual fundamental deterioration state to dual-engine budget routing

## Annual Update Rule

State refresh timing:
- refresh once per year at the annual fundamental update date
- use the same annual refresh point as the fundamental engine
- compute the state score from the latest available annual cross-sectional score change snapshot

Recommended primary state score:
- `score_delta_median`

Recommended backup state score:
- `- deterioration_ratio`

## Train-Time Cut Rule

Primary rule:
- compute train-set state scores
- set:
- `weak_down_cut` = `33%` quantile
- `strong_up_cut` = `67%` quantile

Backup robustness rule:
- allow `30/70` as a nearby robustness check for `breadth_only`

## Runtime State Classification

Given the current annual state score:

- if score >= `strong_up_cut`, classify `strong_up`
- if score <= `weak_down_cut`, classify `weak_down`
- otherwise classify `neutral_flat`

## Portfolio Budget Mapping

Recommended frozen mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

## Interpretation By State

`strong_up`:
- bank fundamentals are broadly improving enough to justify keeping the momentum sleeve fully active

`neutral_flat`:
- keep momentum alive, but shrink it to a secondary sleeve

`weak_down`:
- observable bank fundamentals are deteriorating broadly enough that the momentum sleeve should be shut off

## Execution Notes

- this mapping keeps fundamentals and momentum logically separate
- only the engine budgets change
- raw stock scores are still computed independently inside each engine
- the state layer only decides how much capital each engine receives

## Suggested Next Acceptance Step

- keep fixed `60/40` as the clean benchmark
- compare it only against:
- `delta_median_only` with `33/67`
- `breadth_only` with `33/67`

That keeps the executable acceptance set narrow and disciplined.

## References

- [deterioration_state_proxy_formal_conclusion_v1.md](D:\hh\codex\v4\phase_2_momentum\deterioration_state_proxy_formal_conclusion_v1.md)
- [joinquant_v4_dual_engine_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_dual_engine_strategy_v1.py)
