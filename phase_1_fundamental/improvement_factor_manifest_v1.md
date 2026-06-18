# Improvement Factor Manifest V1

- Total improvement candidates: `22`
- Quarterly-style improvement candidates: `14`
- Annual bank-indicator improvement candidates: `8`

Improvement rules:
- `snapshot_delta`: current value minus previous available rebalance snapshot for the same stock
- `season_yoy_delta`: current value minus prior-year same-season snapshot for the same stock
- `annual_delta`: current annual bank-indicator value minus previous source-year value for the same stock

Output:
- [improvement_factor_manifest_v1.csv](D:\hh\codex\v4\phase_1_fundamental\improvement_factor_manifest_v1.csv)