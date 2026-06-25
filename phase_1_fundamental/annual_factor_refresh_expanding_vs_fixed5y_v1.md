# Annual Factor Refresh Expanding Vs Fixed5Y V1

Objective:
- compare the current pure-fundamental annual refresh baseline against an expanding-memory alternative
- keep the same `2Y` test and `1Y` review structure
- change only the training-window rule

Compared protocols:
- fixed baseline:
  - [annual_factor_refresh_5y2y1y_v1.md](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1.md)
  - each annual refresh uses only the latest `5` realized May-anchor cycles as training history
- expanding alternative:
  - [annual_factor_refresh_expanding_5y2y1y_v1.md](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_expanding_5y2y1y_v1.md)
  - first usable fold starts with `5` realized May-anchor cycles
  - later folds keep the same start date and extend the train window to `6 / 7 / 8 / 9` anchor years

Shared setup:
- factor universe size = `19`
- fold count = `5`
- annual refresh still happens only once per realized May rebalance date
- layer caps and keep rules are unchanged

Fold structure:
- fixed:
  - `annual_01` to `annual_05`
  - train anchor years always = `5`
- expanding:
  - `expanding_01` to `expanding_05`
  - train anchor years = `5 / 6 / 7 / 8 / 9`

Selection-count comparison:
- fixed kept counts by fold:
  - `10 / 10 / 4 / 5 / 7`
- expanding kept counts by fold:
  - `10 / 10 / 5 / 6 / 8`

Interpretation:
- the expanding-memory version keeps more factors in the later folds
- this means older history makes more factors pass the train-plus-test filter
- so long memory is clearly affecting factor retention, not just final combo scoring

Review-year comparison by scenario and combo:
- `base_core_7`:
  - fixed best = `combo__ic_weight_train`
  - fixed mean review ic = `0.095899`
  - fixed mean review spread = `0.00031330`
  - expanding best = `combo__equal_weight`
  - expanding mean review ic = `0.082085`
  - expanding mean review spread = `0.00030499`
- `base_plus_top2_9`:
  - fixed best = `combo__ic_weight_train`
  - fixed mean review ic = `0.086609`
  - fixed mean review spread = `0.00031724`
  - expanding best = `combo__ic_weight_train`
  - expanding mean review ic = `0.066244`
  - expanding mean review spread = `0.00022376`

Main reading:
- on this current pure-fundamental validation frame, expanding memory does **not** beat the fixed `5Y` baseline
- the fixed `5Y` version remains stronger on the main `ic_weight_train` combo in both scenarios
- the expanding version is not useless:
  - it slightly improves `base_core_7` equal-weight review ic and spread
  - it also increases retained-factor counts in later years
- but the current evidence says:
  - longer memory improves retention breadth
  - while fixed `5Y` still gives the stronger main scoring signal

Practical conclusion:
- keep fixed `5Y` as the primary pure-fundamental refresh baseline
- archive expanding memory as a valid comparison branch, not as the new default
- if we revisit this branch later, the most promising next angle is:
  - use expanding memory as a stability filter
  - rather than directly replacing the fixed `5Y` train window

Outputs:
- [annual_factor_refresh_5y2y1y_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_5y2y1y_v1_results.csv)
- [annual_factor_refresh_expanding_5y2y1y_v1_results.csv](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_expanding_5y2y1y_v1_results.csv)
- [annual_factor_refresh_expanding_vs_fixed5y_v1.md](D:\hh\codex\v4\phase_1_fundamental\annual_factor_refresh_expanding_vs_fixed5y_v1.md)
