# Multifactor Incremental Improvement V1

Baseline reference:
- combo: `combo__quarterly_plus_annual`
- validation ic: `0.229192`
- validation top-bottom: `0.00089657`

- Improvement candidates tested: `6`
- Positive delta candidates: `5`

Top candidates by validation delta:
- `improve__annual_delta__bank_indicator__capital_adequacy_ratio` | best_combo=`combo__ic_weight` | delta_ic=`0.076748` | delta_spread=`0.00026371`
- `improve__snapshot_delta__derived__investment_income_to_operating_revenue` | best_combo=`combo__ic_weight` | delta_ic=`0.03847` | delta_spread=`3.19e-06`
- `improve__snapshot_delta__income__minority_profit` | best_combo=`combo__ic_weight` | delta_ic=`0.009428` | delta_spread=`5.527e-05`
- `improve__snapshot_delta__derived__log_total_assets` | best_combo=`combo__quarterly_plus_annual` | delta_ic=`-0.007916` | delta_spread=`5.333e-05`
- `improve__snapshot_delta__indicator__inc_net_profit_to_shareholders_annual` | best_combo=`combo__ic_weight` | delta_ic=`-0.00841` | delta_spread=`2.347e-05`
- `improve__annual_delta__bank_indicator__core_level_capital_adequacy_ratio` | best_combo=`combo__ic_weight` | delta_ic=`-0.016071` | delta_spread=`-9.468e-05`

Outputs:
- [multifactor_incremental_improvement_v1.csv](D:\hh\codex\v4\phase_1_fundamental\multifactor_incremental_improvement_v1.csv)