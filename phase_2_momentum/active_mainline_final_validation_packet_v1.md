# Active Mainline Final Validation Packet V1

Conclusion:
- the active mainline remains `fixed 60/40`
- the strongest upgrade candidate is now frozen as:
- `annual breadth entry + monthly mom6 q50 exit + slow fundamental, fast exit`
- this candidate is mature enough to archive as a formal execution-preparation candidate
- but it has not yet earned promotion over the active baseline

## Mainline Decision

Active executable baseline:
- fixed `60/40`

Active upgrade candidate:
- annual `breadth_only` weak-state entry
- monthly `mom6_positive_ratio_q50` release from `weak_down` to `neutral_flat`
- preferred execution interpretation = `slow fundamental, fast exit`

## Final Ranking

Current best baseline:
- fixed `60/40`
- cum return = `0.007940`

Current best upgrade candidate:
- annual entry monthly exit with `slow fundamental, fast exit`
- cum return = `0.007116`

Weaker candidate reading:
- annual entry monthly exit unconstrained
- cum return = `0.006799`

Earlier weaker route:
- annual breadth-only route
- cum return = `0.005463`

## JoinQuant Execution Confirmation

Frozen executable window:
- `2021-05-31` to `2026-05-31`

Executable baseline confirmation:
- variant = `fixed_60_40`
- strategy return = `35.54%`
- annualized return = `6.48%`
- excess return = `13.08%`
- max drawdown = `13.74%`
- beta = `0.780`
- volatility = `0.138`

Executable candidate confirmation:
- variant = `annual_entry_monthly_exit_slow_fundamental`
- strategy return = `33.93%`
- annualized return = `6.22%`
- excess return = `11.74%`
- max drawdown = `12.95%`
- beta = `0.695`
- volatility = `0.124`

Executable reading:
- the candidate still trails the fixed `60/40` baseline on return
- but it does deliver a slightly tighter risk profile
- so the executable result matches the earlier rolling judgment:
- keep `fixed_60_40` as the practical main line
- archive the candidate as the formal lower-beta alternative branch

## Stability Judgment

The upgrade candidate is not a one-fold accident.

Fold behavior:

- `fold_01`
- candidate = `0.006247`
- fixed `60/40` = `0.006713`

- `fold_02`
- candidate = `0.000413`
- fixed `60/40` = `0.001101`

This means:

- the candidate is consistently second-best
- the baseline is consistently first-best

## Structural Judgment

What has now been proven:

- annual deterioration-based weak-state entry is economically meaningful
- monthly exit from `weak_down` adds real value
- the best current release signal is `mom_6_1` repair breadth with `q50`
- the `slow fundamental, fast exit` execution boundary improves the candidate further

What has not been proven:

- that the candidate can yet surpass the simpler fixed `60/40` route

## Bottleneck Diagnosis

The remaining gap is now narrow and specific:

- the candidate still restores too little effective exposure after defensive phases
- the remaining weakness is better described as a `release-efficiency` shortfall
- it is no longer mainly a `weak-state entry` problem

## Execution-Preparation Decision

Current decision:

1. the candidate is strong enough to preserve as the official next-step execution-preparation candidate
2. the baseline should still remain the default executable line
3. no broader branch should displace this candidate unless it first beats it under the same rolling discipline

So the correct practical reading is:

- this branch is ready for execution-preparation status
- and now also has executable confirmation
- but not yet for baseline replacement status

## What Not To Do Next

Do not:

- reopen annual state-proxy search
- reopen broad combined-structure search
- reopen score-layer mixing
- keep tuning many unrelated branches in parallel

## Recommended Next Step

Use this packet as the freeze point and then choose only one of the following:

- archive the candidate and keep fixed `60/40` as the practical main line
- or use the executable candidate only as a lower-beta allocation alternative, not as the promoted default

## References

- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
- [annual_entry_monthly_exit_stability_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_stability_validation_v1.md)
- [slow_fundamental_fast_exit_execution_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_validation_note_v1.md)
- [annual_entry_monthly_exit_vs_fixed6040_note_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_vs_fixed6040_note_v1.md)
- [joinquant_v4_active_mainline_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_active_mainline_strategy_v1.py)
