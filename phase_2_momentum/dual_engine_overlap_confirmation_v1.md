# Dual Engine Overlap Confirmation V1

Objective:
- test whether the current dual-engine blend derives value from different stock selection or from different weighting on the same stock set
- inspect whether `dual confirmation` stocks are actually a distinct bucket under the current implementation

Protocol:
- research scope = pre-2021 only
- stock-level inspection uses the deployed `60/40` blend
- selection is defined by positive engine weight under the frozen `5%` engine cap

Selection-bucket summary:
- `both_selected` | stock_rows=`109` | ratio=`1.000000` | mean_forward_return=`0.000508`

Overlap summary:
- mean_jaccard_overlap=`1.000000`
- min_jaccard_overlap=`1.000000`
- max_jaccard_overlap=`1.000000`

Interpretation:
- under the current bank universe and cap structure, the two engines effectively select the same stock set on every tested snapshot
- therefore the current dual-engine edge does not come from low-overlap stock picking
- it comes from different weighting on a nearly identical stock universe
- this also means `dual confirmation` is not a distinct stock bucket yet; it is almost the full investable set

Current reading:
- this result strengthens the earlier attribution conclusion that current dual-engine gains are mainly a weighting and deployment effect
- if the project later wants true `selection-layer` interaction evidence, the engine construction would need a narrower stock-selection rule rather than full-universe positive weights

Output:
- [dual_engine_overlap_confirmation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\dual_engine_overlap_confirmation_v1_detail.csv)
