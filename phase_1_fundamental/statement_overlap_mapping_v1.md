# Statement Overlap Mapping V1

Updated: 2026-06-17

Purpose:

- define the first-round overlap mapping between ordinary statements and financial-company statements
- attach explicit missingness checks before standardization
- avoid silent quarter conversion when prerequisite reports are missing

Scope in V1:

- `income.csv` vs `finance_income_statement_current_only.csv`
- `cash_flow.csv` vs `finance_cashflow_statement_current_only.csv`
- balance-sheet overlap is noted separately but not fully mapped in this first file

## 1. Core Rule

Before any standardization:

- check whether the source quarter exists
- check whether the prior cumulative quarter needed for differencing exists
- if the conversion prerequisite is missing, mark the standardized field as missing and log the reason

Do not:

- silently fill missing quarters with zero
- silently carry forward previous quarter values
- silently mix general and financial-company source values in one field

## 2. Income Statement Mapping

### 2.1 Primary Source

Use `finance_income_statement_current_only.csv` as the first-round primary source for bank income-flow fields.

Use `income.csv` as:

- a cross-check source
- a fallback source only when the financial-company table is fully missing for that bank-period

### 2.2 Standardized Overlap Fields

These fields should be treated as overlapping same-meaning candidates with likely cumulative-bank-report behavior:

- `operating_revenue`
- `interest_income`
- `interest_expense`
- `commission_income`
- `commission_expense`
- `asset_impairment_loss`
- `credit_impairment_loss`
- `investment_income`
- `operating_profit`
- `total_profit`
- `income_tax_expense`
- `net_profit`
- `np_parent_company_owners`
- `minority_profit`

### 2.3 First-Round Standardization Treatment

Use this treatment:

- preserve `raw_general_value`
- preserve `raw_financial_value`
- create `std_quarterly_value`
- create `std_source_used`
- create `std_period_basis`
- create `std_missing_reason`

Default transformation:

- choose `finance_income_statement_current_only` as `std_source_used`
- interpret it as `ytd_raw`
- convert to `converted_from_ytd` for Q2/Q3/Q4
- for Q1 keep the raw value directly

### 2.4 Known Cross-Check Behavior

Observed on Ping An Bank and the 10-bank random sample:

- `asset_impairment_loss` often matches exactly
- `operating_revenue`
- `operating_profit`
- `total_profit`
- `np_parent_company_owners`
- `interest_income`
- `commission_income`
often do not match exactly across the two source families

Interpretation:

- do not use equality as the requirement for keeping a field
- use source-priority plus period-basis rules instead

## 3. Cash-Flow Statement Mapping

### 3.1 Primary Source

Use `finance_cashflow_statement_current_only.csv` as the first-round primary source for bank cash-flow fields.

Use `cash_flow.csv` as:

- a cross-check source
- a fallback source only when the financial-company table is fully missing for that bank-period

### 3.2 Standardized Overlap Fields

First-round overlapping bank cash-flow fields:

- `net_deposit_increase`
- `net_borrowing_from_central_bank`
- `net_borrowing_from_finance_co`
- `interest_and_commission_cashin`
- `net_increase_in_placements`
- `net_buyback`
- `tax_levy_refund`
- `goods_and_services_cash_paid`
- `net_loan_and_advance_increase`
- `net_deposit_in_cb_and_ib`
- `original_compensation_paid`
- `policy_dividend_cash_paid`
- `staff_behalf_paid`
- `tax_payments`
- `subtotal_operate_cash_inflow`
- `subtotal_operate_cash_outflow`
- `net_operate_cash_flow`
- `invest_withdrawal_cash`
- `invest_proceeds`
- `fix_intan_other_asset_acqui_cash`
- `invest_cash_paid`
- `impawned_loan_net_increase`
- `subtotal_invest_cash_inflow`
- `subtotal_invest_cash_outflow`
- `net_invest_cash_flow`
- `cash_from_invest`
- `cash_from_bonds_issue`
- `cash_from_borrowing`
- `subtotal_finance_cash_inflow`
- `borrowing_repayment`
- `dividend_interest_payment`
- `subtotal_finance_cash_outflow`
- `net_finance_cash_flow`
- `exchange_rate_change_effect`
- `cash_equivalent_increase`
- `cash_equivalents_at_beginning`
- `cash_and_equivalents_at_end`

### 3.3 First-Round Standardization Treatment

Default transformation:

- choose `finance_cashflow_statement_current_only` as `std_source_used`
- interpret amount fields as `ytd_raw`
- convert Q2/Q3/Q4 to `converted_from_ytd`
- preserve Q1 directly

Special note:

- some fields may already behave like point movements instead of cumulative values
- until explicitly reclassified, keep them under the same audit framework and compare the converted series against the general `cash_flow` table

## 4. Balance-Sheet Overlap Handling

V1 policy:

- do not attempt aggressive field-by-field merging yet
- use `balance.csv` as the standardized main table
- keep `finance_balance_sheet_parent_current_only.csv` as parent-scope supplement

Overlapping fields such as:

- `total_assets`
- `total_liability`
- `lend_capital`
- `bought_sellback_assets`
- `cash_equivalents`

should be kept as:

- main consolidated-style value from `balance`
- optional `parent_*` auxiliary series from `finance_balance_sheet_parent_current_only`

## 5. Missingness Checks

### 5.1 Report-Existence Check

For each bank and standardized quarter:

- check whether the target source table has a row for that report period
- if missing, set:
  - `std_quarterly_value = missing`
  - `std_missing_reason = missing_target_report`

### 5.2 Prior-Quarter Conversion Check

For cumulative-to-quarter conversion:

- Q1 does not need a prior quarter
- Q2 requires Q1
- Q3 requires Q2
- Q4 requires Q3

If the prior quarter is missing:

- do not compute the difference
- set:
  - `std_quarterly_value = missing`
  - `std_missing_reason = missing_prior_cumulative_report`

### 5.3 New-Listing Check

If a bank was not yet listed or not yet expected to have public reports in the early window:

- allow missingness
- set:
  - `std_missing_reason = pre_listing_or_not_expected`

### 5.4 Structural-Scope Check

For fields that only exist in one source family:

- keep them as source-specific fields
- set:
  - `std_missing_reason = source_specific_field_not_available`
when trying to reference them from the other family

### 5.5 Tail-Window Check

For the current research window end `2026-05-01`:

- missing `2026q2`, `2026q3`, `2026q4` should be labeled:
  - `std_missing_reason = outside_current_available_window`

### 5.6 Annual Bank Indicator Gap

For `bank_indicator`:

- missing `2024`, `2025`, `2026` should be labeled:
  - `std_missing_reason = provider_unavailable_annual_bank_indicator`

## 6. Required Audit Outputs

For each standardized field conversion, log:

- `code`
- `report_period_end`
- `standard_field_name`
- `source_table`
- `source_field`
- `raw_value_used`
- `prior_cumulative_value_used`
- `transformation_rule`
- `conversion_success`
- `missing_reason`

## 7. V1 Implementation Order

1. implement report-presence and prior-quarter checks
2. implement quarterly conversion for primary income fields
3. implement quarterly conversion for primary cash-flow fields
4. write conversion audit logs
5. only then expand to the longer tail of source-specific banking fields
