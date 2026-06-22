# Fundamental Defensive Overlay YOY Pool Linear V2 Threshold Freeze Summary

Purpose:
- freeze a single deterioration threshold for the `v2` pure-fundamental defensive overlay
- decision must use `train/test` only
- `review` is intentionally excluded from the freeze decision

Source:
- [fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2_config_results.csv)
- [fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2.md](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2.md)

Protocol:
- base execution line = annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- defensive signal = ratio of deteriorated stocks inside the filtered candidate pool
- tested thresholds = `40% / 50% / 60%`
- defensive asset = `511010`
- freeze comparison aggregates all `5` annual folds using only `train/test`

Unified train/test comparison:

| Threshold | Folds | Train mean cum | Test mean cum | Train mean excess vs baseline | Test mean excess vs baseline | Train wins vs baseline | Test wins vs baseline | Train mean treasury weight | Test mean treasury weight |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `40%` | `5` | `0.069848` | `0.027800` | `0.066656` | `0.024099` | `5/5` | `5/5` | `0.461139` | `0.466004` |
| `50%` | `5` | `0.061429` | `0.028494` | `0.058237` | `0.024794` | `5/5` | `5/5` | `0.418366` | `0.402554` |
| `60%` | `5` | `0.026792` | `0.014160` | `0.023599` | `0.010460` | `4/5` | `4/5` | `0.200953` | `0.145581` |

Readout:
- `60%` is clearly weaker than `40%` and `50%` on both train and test.
- `40%` and `50%` both beat the pure-fundamental baseline in all `5/5` train folds and all `5/5` test folds.
- `50%` has the best mean `test` cumulative return and the best mean `test` excess versus baseline.
- `50%` also uses less treasury on average than `40%`, so it gets slightly better test performance with a more restrained defensive posture.
- `40%` has the best mean `train` result, but that extra strength does not carry into a better mean `test` result.

Freeze decision:
- freeze threshold = `50%`

Why `50%` is the better freeze:
- it is the best `test` performer on the only comparison window we are allowed to use for freezing
- it matches `40%` on fold-level test win rate (`5/5`) while taking less average defensive weight
- it avoids the more aggressive `40%` setting, which looks somewhat stronger in-sample than out-of-sample
- it is materially stronger than `60%`, so it keeps enough sensitivity to deterioration breadth

Implementation guidance:
- if we now write the defensive code back into the `v4` pure-fundamental JoinQuant strategy, the first frozen candidate should be:
- signal = filtered candidate-pool deterioration ratio
- trigger threshold = `50%`
- mapping = `treasury_weight = deterioration_ratio` once threshold is crossed
- defensive asset = `511010`
- do not yet add persistence bonus or exit-on-improve logic; those should remain separate post-freeze tests
