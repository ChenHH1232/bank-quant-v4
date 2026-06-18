# Time-Series CV Feasibility V1

Requested protocol:
- training window: `5` years
- test window: `2` years
- research must end before: `2021-05-01`

Observed usable pre-2021 rebalance sample:
- earliest rebalance date: `2014-05-05`
- latest rebalance date: `2020-11-02`
- rebalance date count: `23`

Feasibility check:
- if the first fold starts at `2014-05-05`, a full 5y+2y window would end at `2021-05-05`
- strict 5y-train / 2y-test pre-2021 CV feasible: `False`

Conclusion:
- full pre-2021 time-series CV is not feasible with the current panel because the usable rebalance history starts too late
- this means we cannot build multiple strict 5y-train / 2y-test folds without either
  using post-2021 data for research, or relaxing the window definition

Output:
- [time_series_cv_feasibility_v1.csv](D:\hh\codex\v4\phase_1_fundamental\time_series_cv_feasibility_v1.csv)