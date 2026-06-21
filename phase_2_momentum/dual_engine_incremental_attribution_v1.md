# Dual Engine Incremental Attribution V1

Objective:
- measure what the deployed `60/40` dual-engine blend adds relative to pure fundamental
- keep the comparison at the same pre-2021 rolling out-of-sample snapshots

Protocol:
- reference = `fundamental_only`
- tested blend = `blend_60_40`
- comparison unit = each out-of-sample rebalance snapshot

Incremental summary:
- `fundamental_only` cum return = `0.002768`
- `blend_60_40` cum return = `0.004325`
- cumulative increment = `0.001557`
- mean per-snapshot return increment = `0.000194`
- positive increment snapshots = `6`
- negative increment snapshots = `2`
- mean invested-weight increment = `0.237623`
- mean cash-weight change = `-0.237623`

Interpretation:
- the main first-order improvement from adding momentum is higher effective capital deployment
- the dual-engine blend reduces residual cash created by the conservative cap structure
- this higher deployment translates into a positive average return increment on most snapshots

Fold attribution:
- `fold_01` | fundamental=`0.000960` | blend_60_40=`0.001528` | increment=`0.000568` | positive_snapshots=`3/4`
- `fold_02` | fundamental=`0.001806` | blend_60_40=`0.002792` | increment=`0.000987` | positive_snapshots=`3/4`

Best incremental snapshots:
- `2019-09-02` `fold_01` | delta_return=`0.000745` | delta_invested=`0.255455`
- `2019-09-02` `fold_02` | delta_return=`0.000745` | delta_invested=`0.255455`
- `2020-05-06` `fold_02` | delta_return=`0.000348` | delta_invested=`0.190000`

Weakest incremental snapshots:
- `2019-11-01` `fold_01` | delta_return=`-0.000260` | delta_invested=`0.232308`
- `2019-11-01` `fold_02` | delta_return=`-0.000260` | delta_invested=`0.232308`
- `2019-05-06` `fold_01` | delta_return=`0.000000` | delta_invested=`0.255455`

Current reading:
- this first-pass attribution does not yet separate alpha improvement from diversification improvement
- but it already shows that the dual-engine blend improves the practical portfolio profile beyond pure fundamental on the same snapshots
- the next attribution layer should study holding overlap and dual-confirmation effects

Output:
- [dual_engine_incremental_attribution_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\dual_engine_incremental_attribution_v1_detail.csv)
