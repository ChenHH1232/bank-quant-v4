# Execution-Faithful Validation V1

Goal:
- build a local truth packet for selected rebalance dates before comparing with JoinQuant
- use this packet to find where local rolling and JoinQuant begin to diverge

Scope frozen in this first pass:
- scenario: `base_core_7`
- combo: `combo__ic_weight_train`
- target years: `2021, 2022, 2024, 2025`

Local outputs:
- [execution_faithful_validation_v1_local_summary.csv](D:\hh\codex\v4\phase_1_fundamental\execution_faithful_validation_v1_local_summary.csv)
- [execution_faithful_validation_v1_local_detail.csv](D:\hh\codex\v4\phase_1_fundamental\execution_faithful_validation_v1_local_detail.csv)

Fields prepared for date-by-date reconciliation:
- local pool membership
- raw factor values
- standardized `z__*` values
- direction-adjusted `adj__*` values
- normalized factor weights and score contribution
- final score
- descending score rank
- bucket assignment
- top-bucket inclusion
- equal target weight inside top bucket
- next-period realized return in the local panel

JoinQuant side should export the same rebalance dates and the same fields in the same order.

Selected dates:
- `2021-05-06` | fold=`annual_01` | factor_count=`6` | pool_count=`26` | top_count=`5` | target_weight_each=`0.2`
- `2022-05-05` | fold=`annual_01` | factor_count=`6` | pool_count=`27` | top_count=`6` | target_weight_each=`0.1666666667`
- `2024-05-06` | fold=`annual_04` | factor_count=`2` | pool_count=`29` | top_count=`6` | target_weight_each=`0.1666666667`
- `2025-05-06` | fold=`annual_05` | factor_count=`4` | pool_count=`31` | top_count=`6` | target_weight_each=`0.1666666667`

Recommended reconciliation order:
1. pool membership
2. raw factor values
3. `z__*` standardization
4. `adj__*` sign handling
5. final score and rank
6. bucket / top-bucket selection
7. target weight
8. next-period return mapping