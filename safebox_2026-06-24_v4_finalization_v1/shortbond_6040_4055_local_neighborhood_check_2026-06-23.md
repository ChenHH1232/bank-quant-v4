# `shortbond_6040_4055` Local Neighborhood Check

Date: `2026-06-23`

## Objective

Do a minimal local robustness check around the live defensive-overlay candidate:

- `bank_core_3`
- defensive asset = `short_bond_etf_511260`
- live JoinQuant candidate label = `shortbond_6040_4055`

This note uses the existing rolling output and does not open a new broad parameter search.

## Source

- [fundamental_defensive_overlay_rolling_validation_v1_config_results.csv](D:/hh/codex/v4/phase_1_fundamental/fundamental_defensive_overlay_rolling_validation_v1_config_results.csv)
- [fundamental_defensive_overlay_project_summary_2026-06-22.md](D:/hh/codex/v4/phase_1_fundamental/fundamental_defensive_overlay_project_summary_2026-06-22.md)

## Neighborhood Definition

The available local grid around `6040_4055` is:

- `warning_threshold`: `40%` or `45%`
- `severe_threshold`: `55%` or `60%`
- `warning_equity_weight`: `60%` or `80%`
- `severe_equity_weight`: `20%` or `40%`

Target point:

- `warning_threshold = 40%`
- `severe_threshold = 55%`
- `warning_equity_weight = 60%`
- `severe_equity_weight = 40%`

## Aggregated Fold Result

Mean rolling cumulative return across the 5 annual folds:

| warning thr | severe thr | warning eq | severe eq | train mean | test mean | review mean | total mean |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| 40% | 55% | 60% | 20% | 0.010884 | 0.008578 | 0.003467 | 0.022929 |
| 40% | 60% | 60% | 20% | 0.010884 | 0.008578 | 0.003467 | 0.022929 |
| 45% | 55% | 60% | 20% | 0.010884 | 0.008578 | 0.003467 | 0.022929 |
| 45% | 60% | 60% | 20% | 0.010884 | 0.008578 | 0.003467 | 0.022929 |
| 40% | 55% | 60% | 40% | 0.010626 | 0.008578 | 0.003467 | 0.022671 |
| 40% | 60% | 60% | 40% | 0.010626 | 0.008578 | 0.003467 | 0.022671 |
| 45% | 55% | 60% | 40% | 0.010626 | 0.008578 | 0.003467 | 0.022671 |
| 45% | 60% | 60% | 40% | 0.010626 | 0.008578 | 0.003467 | 0.022671 |
| 40% | 55% | 80% | 20% | 0.008431 | 0.006139 | 0.002245 | 0.016815 |
| 40% | 60% | 80% | 20% | 0.008431 | 0.006139 | 0.002245 | 0.016815 |
| 45% | 55% | 80% | 20% | 0.008431 | 0.006139 | 0.002245 | 0.016815 |
| 45% | 60% | 80% | 20% | 0.008431 | 0.006139 | 0.002245 | 0.016815 |
| 40% | 55% | 80% | 40% | 0.008173 | 0.006139 | 0.002245 | 0.016557 |
| 40% | 60% | 80% | 40% | 0.008173 | 0.006139 | 0.002245 | 0.016557 |
| 45% | 55% | 80% | 40% | 0.008173 | 0.006139 | 0.002245 | 0.016557 |
| 45% | 60% | 80% | 40% | 0.008173 | 0.006139 | 0.002245 | 0.016557 |

## Read-Through

What clearly matters:

- `warning_equity_weight = 60%` is much better than `80%`
- the gap is large enough to show up consistently in `train`, `test`, and `review`

What matters only a little:

- within the `warning_eq = 60%` family, `severe_eq = 20%` is slightly above `40%`
- the difference is small: `0.022929` vs `0.022671`

What barely matters in this local grid:

- `warning_threshold = 40%` vs `45%`
- `severe_threshold = 55%` vs `60%`

In this dataset those threshold changes are effectively flat around the live candidate.

## Conclusion

`shortbond_6040_4055` does not look like an isolated spike in the local rolling panel.

The main signal from the neighborhood check is:

- the useful edge is concentrated in the `warning` layer
- keeping warning-stage equity at `60%` looks important
- the `55%` versus `60%` severe threshold is not the source of the edge
- the `20%` versus `40%` severe-equity branch is secondary

So if we want the smallest next JoinQuant follow-up, the most meaningful adjacent check is not more threshold twisting, but one tight comparison inside the `warning_eq = 60%` family:

- current live point: `6040_4055`
- closest meaningful neighbor: `6020_4055`

If that neighbor does not beat the live candidate in full backtest, we should treat the short-bond branch as sufficiently stable and stop micro-tuning it.
