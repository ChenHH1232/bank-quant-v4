# Multifactor Top2 Improvement Combo V1

- Baseline combo: `combo__ic_weight` | val_ic=`0.15537` | spread=`0.00017311`
- Top1 alone: `improve__annual_delta__bank_indicator__Nonperforming_loan_rate` | val_ic=`0.262569` | delta_ic=`0.107199`
- Top2 alone: `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | val_ic=`0.246092` | delta_ic=`0.090722`
- Together: `improve__annual_delta__bank_indicator__Nonperforming_loan_rate|improve__snapshot_delta__derived__investment_income_to_operating_revenue` | val_ic=`0.302698` | delta_ic=`0.147328` | delta_spread=`0.00079717`

Outputs:
- [multifactor_top2_improvement_combo_v1.csv](D:\hh\codex\v4\phase_1_fundamental\multifactor_top2_improvement_combo_v1.csv)