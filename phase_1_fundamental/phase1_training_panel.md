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

- Rows: `998`
- Rebalance dates: `38`
- In-pool rows: `726`
- Quarter-y ready rows: `958`
- Year-y ready rows: `856`

Largest remaining field-missing counts:
- `income__minority_profit`: `35`
- `cash_flow__invest_withdrawal_cash`: `21`
- `cash_flow__exchange_rate_change_effect`: `15`
- `cash_flow__net_loan_and_advance_increase`: `15`
- `cash_flow__invest_proceeds`: `14`
- `cash_flow__tax_payments`: `13`
- `indicator__expense_to_total_revenue`: `12`
- `cash_flow__fix_intan_other_asset_acqui_cash`: `3`
- `cash_flow__interest_and_commission_cashin`: `2`
- `cash_flow__net_finance_cash_flow`: `2`
- `cash_flow__subtotal_finance_cash_outflow`: `2`

Output:
- [phase1_training_panel.csv](D:\hh\codex\v4\phase_1_fundamental\phase1_training_panel.csv)