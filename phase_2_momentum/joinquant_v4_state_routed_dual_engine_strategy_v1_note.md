# JoinQuant V4 State Routed Dual Engine Strategy V1 Note

Main file:
- [joinquant_v4_state_routed_dual_engine_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_state_routed_dual_engine_strategy_v1.py)

## How To Compare

Only compare these three variants by changing one line in `initialize`:

- `g.strategy_variant = "fixed_60_40"`
- `g.strategy_variant = "delta_median_only"`
- `g.strategy_variant = "breadth_only"`

Everything else stays unchanged.

## Frozen State Mapping

Shared mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

## Frozen Annual Proxy Interpretation

Primary candidate:
- `delta_median_only`
- train cuts = `q33 / q67`
- pre-2021 frozen cut values:
- low cut = `-0.029567`
- high cut = `0.013898`

Backup candidate:
- `breadth_only`
- score = `- deterioration_ratio`
- train cuts = `q33 / q67`
- pre-2021 frozen cut values:
- low cut = `-0.688375`
- high cut = `-0.471637`

## Annual State Schedule Written Into Code

`delta_median_only`:
- `2021-05-31` => `weak_down`
- `2022-05-05` => `strong_up`
- `2023-05-04` => `neutral_flat`
- `2024-05-06` => `neutral_flat`
- `2025-05-06` => `neutral_flat`
- `2026-05-06` => `neutral_flat` using carry-forward because the current local offline panel ends before a fresh `2026-05` annual proxy refresh

`breadth_only`:
- `2021-05-31` => `neutral_flat`
- `2022-05-05` => `strong_up`
- `2023-05-04` => `neutral_flat`
- `2024-05-06` => `strong_up`
- `2025-05-06` => `strong_up`
- `2026-05-06` => `strong_up` using carry-forward because the current local offline panel ends before a fresh `2026-05` annual proxy refresh

`fixed_60_40`:
- all annual dates stay fixed at `60/40`

## Execution Design

- fundamental stock pool still follows the approved annual or quasi-quarterly plan
- momentum stock picking still uses monthly `mom_12_1`
- only the budget layer changes by state
- the state layer updates yearly and is carried across the intra-year `09-01` and `11-01` pool refreshes
