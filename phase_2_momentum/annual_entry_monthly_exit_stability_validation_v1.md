# Annual Entry Monthly Exit Stability Validation V1

Conclusion:
- the `annual breadth entry + monthly mom6 q50 exit` candidate is not a fragile one-fold accident
- it improves the annual-only defensive route in both current folds
- but it still trails fixed `60/40` in both folds, so the baseline advantage remains stable

## Fold-Level Check

Compared strategies:
- fixed `60/40`
- annual breadth entry + monthly `mom6_positive_ratio_q50` exit

Fold summary:

- `fold_01`
- candidate cum return = `0.006247`
- fixed `60/40` cum return = `0.006713`

- `fold_02`
- candidate cum return = `0.000413`
- fixed `60/40` cum return = `0.001101`

## What This Means

This says two things:

- the candidate is consistently second-best, not randomly unstable
- but the fixed `60/40` baseline still beats it in both currently available validation folds

So the current gap is persistent:

- the candidate has not yet found a fold where it clearly overtakes the baseline

## State-Behavior Check

Candidate state behavior:

- weak-down monthly snapshots = `20`
- released to `neutral_flat` = `3`
- held in `weak_down` = `17`

Mean return by final state:

- `neutral_flat` = `0.000892`
- `weak_down` = `-0.000078`

## Interpretation

This confirms the economic story:

- months that escaped `weak_down` were materially better than the months that stayed defensive
- so the monthly release layer is genuinely detecting part of the recovery process

But it also exposes the remaining shortfall:

- release frequency is still too low
- the candidate spends too much time trapped in `weak_down`
- this is likely the main reason it still trails fixed `60/40`

## Validation Judgment

Current validation judgment should be:

1. keep fixed `60/40` as the active baseline
2. keep annual entry plus monthly exit as the active upgrade candidate
3. treat the remaining gap as a `release-efficiency` problem, not as proof that the whole two-layer framework is wrong

## References

- [weak_down_exit_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_rolling_validation_v1.md)
- [annual_entry_monthly_exit_vs_fixed6040_note_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_vs_fixed6040_note_v1.md)
