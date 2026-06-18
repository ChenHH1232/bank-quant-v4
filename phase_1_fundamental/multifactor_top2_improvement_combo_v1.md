# Multifactor Top2 Improvement Combo V1

- Baseline combo: `combo__quarterly_plus_annual` | val_ic=`0.229192` | spread=`0.00089657`
- Top1 alone: `improve__annual_delta__bank_indicator__capital_adequacy_ratio` | val_ic=`0.30594` | delta_ic=`0.076748`
- Top2 alone: `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | val_ic=`0.267662` | delta_ic=`0.03847`
- Together: `improve__annual_delta__bank_indicator__capital_adequacy_ratio|improve__snapshot_delta__derived__investment_income_to_operating_revenue` | val_ic=`0.308259` | delta_ic=`0.079067` | delta_spread=`7.163e-05`

Outputs:
- [multifactor_top2_improvement_combo_v1.csv](D:\hh\codex\v4\phase_1_fundamental\multifactor_top2_improvement_combo_v1.csv)