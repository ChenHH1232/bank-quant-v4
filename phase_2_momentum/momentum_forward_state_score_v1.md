# Momentum Forward State Score V1

Scope:
- sample window: `2014-01-01` to `2020-12-31`
- objective: combine the best simple forward state proxies into one composite score for `mom_6_1` favorability

Score construction:
- `cross_mcap_median` with sign `1`
- `cross_mom6_positive_ratio` with sign `1`
- `cross_target_dispersion` with sign `1`
- `cross_money_median` with sign `-1`

Composite score results:
- corr to next-period pool mean return: `0.207763`
- corr to next-period `mom_6_1` IC: `0.420968`
- corr to next-period `mom_12_1` IC: `0.216621`
- top-third score months avg forward return: `0.027131`
- bottom-third score months avg forward return: `-0.002100`
- top-third score months avg `mom_6_1` IC: `0.290998`
- bottom-third score months avg `mom_6_1` IC: `-0.174415`
- top-third score months avg `mom_12_1` IC: `0.164145`
- bottom-third score months avg `mom_12_1` IC: `-0.113544`

Interpretation:
- a useful state score should raise `mom_6_1` more than it raises `mom_12_1`
- if top-third months clearly improve `mom_6_1` IC versus bottom-third months, the score is a usable first-generation forward state proxy
- this is still a research-layer score, not yet a production switching rule

Output:
- [momentum_forward_state_score_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_score_v1.csv)
