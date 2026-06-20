# Momentum Forward State Score V2

Scope:
- sample window: `2014-01-01` to `2020-12-31`
- objective: build a more `mom_6_1`-specific forward state score than V1
- selection logic: keep only components that looked helpful in rolling switch testing and avoid pushing too much weight onto broad momentum breadth

Score construction:
- `cross_mcap_median` with sign `1`
- `cross_target_dispersion` with sign `1`
- `cross_mom6_top_bottom_spread` with sign `1`
- `cross_money_median` with sign `-1`

Composite score results:
- corr to next-period pool mean return: `0.217110`
- corr to next-period `mom_6_1` IC: `0.334931`
- corr to next-period `mom_12_1` IC: `0.161464`
- `mom_6_1` minus `mom_12_1` IC correlation gap: `0.173467`
- top-third score months avg forward return: `0.019596`
- bottom-third score months avg forward return: `-0.005561`
- top-third score months avg `mom_6_1` IC: `0.250972`
- bottom-third score months avg `mom_6_1` IC: `-0.088532`
- top-third score months avg `mom_12_1` IC: `0.101820`
- bottom-third score months avg `mom_12_1` IC: `-0.058851`

Interpretation:
- compared with V1, this version is intended to sharpen the high-state month definition rather than broaden it
- `cross_mom6_top_bottom_spread` is kept because it better reflects cross-sectional medium-term momentum separation
- this score still remains a research-layer score until the rolling switch test confirms promotion value

Output:
- [momentum_forward_state_score_v2.csv](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_score_v2.csv)
