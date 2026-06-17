# Single-Factor Manifest V1

Scope:
- built from `phase1_training_panel.csv`
- includes only modeled factor columns
- excludes helper columns, pool flags, identifiers, and target columns

Window:
- training: `2014-05-01` to `2019-05-01`
- validation: `2019-05-01` to `2021-05-01`

- Total candidate factors: `74`

Family counts:
- `balance`: `14`
- `bank_indicator`: `11`
- `cash_flow`: `20`
- `income`: `12`
- `indicator`: `17`

Output:
- [single_factor_manifest_v1.csv](D:\hh\codex\v4\phase_1_fundamental\single_factor_manifest_v1.csv)