# Annual Entry Monthly Exit Vs Fixed 60/40 Note V1

Conclusion:
- the `annual breadth entry + monthly mom6 q50 exit` branch is the strongest current observable state-routing upgrade candidate
- but it still does not beat the fixed `60/40` dual-engine baseline in pre-2021 rolling validation
- so the current role of this branch is `formal candidate`, not `promoted baseline`

## What Was Compared

Baseline:
- fixed `60/40`

Annual-only defensive route:
- annual `breadth_only`

Two-layer candidate:
- annual `breadth_only` weak-state entry
- monthly `mom6_positive_ratio_q50` release from `weak_down` to `neutral_flat`

Shared budget mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

## Result

Current ranking:

1. fixed `60/40` cum return = `0.007821`
2. annual breadth entry + monthly `mom6_positive_ratio_q50` exit = `0.006799`
3. annual breadth entry + monthly `mom6_positive_ratio_q67` exit = `0.006663`
4. annual breadth-only route = `0.005463`

## Interpretation

This means:

- the annual deterioration layer by itself was too slow to recover
- adding a monthly release layer clearly helped
- the best current repair signal is still `mom_6_1` breadth, with a `q50` release threshold

But the baseline still wins:

- fixed `60/40` remains the stronger overall route on current pre-2021 rolling evidence

So the right reading is:

- the two-layer state machine is a valid and meaningful improvement over annual-only state routing
- but it has not yet earned promotion over the simpler fixed blend

## Why The Candidate Still Matters

This branch remains important because it has now established something structural:

- faster release from `weak_down` is the real missing piece in the observable state-routing problem

That means future refinement should stay narrow:

- keep annual entry fixed
- keep release destination fixed at `neutral_flat`
- only improve the release signal if needed

## Current Decision

Current decision should be:

1. keep fixed `60/40` as the active executable baseline
2. keep `annual breadth entry + monthly mom6 q50 exit` as the active research upgrade candidate
3. do not reopen broader annual state-proxy search or unrelated combined-structure branches before this candidate is fully settled

## References

- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
- [weak_down_exit_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_rolling_validation_v1.md)
- [weak_down_exit_signal_refinement_v1.md](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_signal_refinement_v1.md)
