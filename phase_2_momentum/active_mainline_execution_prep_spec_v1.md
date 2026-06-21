# Active Mainline Execution Prep Spec V1

Objective:
- freeze the exact implementation contract for the current active upgrade candidate before writing or revising executable backtest code
- reduce definition drift between research validation and later JoinQuant execution

## Candidate To Prepare

Execution-preparation candidate:
- `annual breadth entry + monthly mom6 q50 exit + slow fundamental, fast exit`

Reference baseline:
- fixed `60/40`

## Fixed Signal Rules

Annual entry rule:
- annual weak-state trigger = `breadth_only`
- annual score = `- deterioration_ratio`
- annual classification source remains the frozen precomputed annual state schedule

Monthly exit rule:
- monthly repair signal = bank cross-sectional `mom_6_1` positive ratio
- release threshold = train-set `q50`
- release action = only `weak_down -> neutral_flat`

No additional signal changes are allowed in the execution-preparation version.

## Fixed Budget Mapping

- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

This mapping is frozen for the execution-preparation version.

## Fixed Execution Interpretation

Default execution interpretation:
- `slow fundamental, fast exit`

Meaning:

- on fundamental rebalance dates:
- fundamental sleeve may buy, sell, and rebuild

- on non-fundamental dates:
- fundamental sleeve may sell down
- fundamental sleeve may not buy new fundamental positions
- restored tactical risk budget should first reactivate the momentum sleeve

## Fixed Comparison Scope

The execution-preparation round should compare only:

1. `fixed_60_40`
2. active candidate with `slow fundamental, fast exit`

Do not include:

- annual-only breadth route
- unconstrained candidate version
- delta-median branch
- layered filter-then-rank branch
- score-layer mixing branch

## Fixed Data/Calendar Assumptions

Fundamental layer:
- approved annual or quasi-quarterly pool schedule remains frozen

Momentum layer:
- monthly `mom_12_1` deployment-safe ranking remains frozen

State layer:
- annual state refresh remains tied to the annual fundamental refresh point
- monthly exit checks run only on monthly refresh dates

## Required Output For Execution Round

The next executable round should report at least:

- strategy return
- annualized return
- excess return
- max drawdown
- Sharpe ratio
- beta
- volatility
- yearly return split
- drawdown period

## Promotion Rule

The candidate should only be considered for promotion if the execution round shows one of two outcomes:

1. clear outperformance over fixed `60/40`
2. clearly better risk profile with only a small and acceptable return concession

If neither happens:
- fixed `60/40` remains the practical main line
- the candidate stays archived as a research-proven but not promoted branch

## Process Discipline

Before writing new executable code or editing old executable code, treat the following as locked:

- annual entry signal
- monthly exit signal
- budget mapping
- slow-fundamental execution boundary
- comparison baseline set

This preparation round should not reopen research exploration.

## References

- [active_mainline_final_validation_packet_v1.md](D:\hh\codex\v4\phase_2_momentum\active_mainline_final_validation_packet_v1.md)
- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
- [slow_fundamental_fast_exit_execution_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_validation_note_v1.md)
