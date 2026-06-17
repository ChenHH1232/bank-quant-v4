# Phase 1 Training Panel

Definition:
- one row per `rebalance_date x code`
- already joined with:
  - disclosed-data validity
  - dynamic rebalance stock-pool flags
  - whitelisted fundamental fields
  - forward y labels based on close-to-close daily return averages

Y definition:
- `y_quarter_avg_daily_return_close`: mean daily close-to-close return from after current rebalance date to next rebalance date
- `y_year_avg_daily_return_close`: mean daily close-to-close return from after current rebalance date to the rebalance date four quarters later
- annual bank indicators are still aligned from the latest published annual snapshot available on the rebalance date

- Rows: `525`
- Rebalance dates: `25`
- In-pool rows: `390`
- Quarter-y ready rows: `486`
- Year-y ready rows: `429`

Largest remaining field-missing counts:
- `income__minority_profit`: `23`
- `cash_flow__invest_withdrawal_cash`: `12`
- `cash_flow__net_loan_and_advance_increase`: `9`
- `cash_flow__invest_proceeds`: `8`
- `cash_flow__tax_payments`: `7`
- `cash_flow__exchange_rate_change_effect`: `4`
- `cash_flow__fix_intan_other_asset_acqui_cash`: `3`
- `cash_flow__interest_and_commission_cashin`: `2`

Output:
- [phase1_training_panel.csv](D:\hh\codex\v4\phase_1_fundamental\phase1_training_panel.csv)