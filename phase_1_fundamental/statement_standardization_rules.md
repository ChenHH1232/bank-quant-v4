# Statement Standardization Rules

Updated: 2026-06-17

Purpose:

- define a stable standardization plan for bank financial statements
- resolve overlap between the general three-statement interfaces and the dedicated financial-company interfaces
- separate `raw source retention` from `model-ready standardized fields`

## 1. What We Confirmed

Using Ping An Bank plus a random 10-bank sample from the 42-bank universe, we confirmed:

- ordinary `income` and `finance.FINANCE_INCOME_STATEMENT` share many fields but often differ in value
- ordinary `cash_flow` and `finance.FINANCE_CASHFLOW_STATEMENT` share many fields but often differ in value
- ordinary `balance` and `finance.FINANCE_BALANCE_SHEET_PARENT` share many fields but often differ in value
- the pattern is not a Ping An-only exception

Working interpretation:

- income and cash-flow overlap is mainly a `single-quarter vs year-to-date cumulative` problem
- balance-sheet overlap is mainly a `consolidated vs parent-company scope` problem

## 2. Standardization Principles

Rules:

- never overwrite raw source files
- preserve source-specific columns in a raw layer
- create standardized tables in a separate cleaned layer
- every standardized field must have:
  - a source priority
  - a period interpretation
  - a statement-scope interpretation
  - a missing-data fallback

## 3. Standardized Table Families

We will maintain three logical layers for statements:

### 3.1 Raw Layer

Keep all original downloaded files:

- `balance.csv`
- `income.csv`
- `cash_flow.csv`
- `indicator.csv`
- `bank_indicator.csv`
- `finance_income_statement_current_only.csv`
- `finance_cashflow_statement_current_only.csv`
- `finance_balance_sheet_parent_current_only.csv`

### 3.2 Standardized Quarterly Layer

Create model-ready quarterly tables:

- `std_balance_quarterly`
- `std_income_quarterly`
- `std_cash_flow_quarterly`
- `std_indicator_quarterly`
- `std_bank_indicator_annual`

### 3.3 Mapping / Audit Layer

Keep traceability tables:

- field mapping catalog
- source-priority table
- quarter-conversion audit table
- statement-scope audit table

## 4. Period Standardization Rules

This section applies to:

- `income`
- `cash_flow`
- `indicator`
- `finance_income_statement_current_only`
- `finance_cashflow_statement_current_only`

### 4.1 Raw Period Labels

For every raw row keep:

- security code
- report period end date
- disclosure date
- source table name
- raw field value

### 4.2 Period Interpretation

Default working assumption:

- Q1 values are already first-quarter values
- Q2, Q3, Q4 values in bank financial statements are often year-to-date cumulative values

### 4.3 Standard Quarterly Conversion

For fields identified as cumulative:

- `Q1_std = Q1_raw`
- `Q2_std = Q2_raw - Q1_raw`
- `Q3_std = Q3_raw - Q2_raw`
- `Q4_std = Q4_raw - Q3_raw`

For fields identified as already single-quarter:

- `Qx_std = Qx_raw`

### 4.4 First-Round Classification

Treat these financial-company statement fields as cumulative unless evidence later proves otherwise:

- operating revenue / income flow fields
- interest income / interest expense
- commission income / commission expense
- operating profit
- total profit
- net profit
- net cash-flow subtotals
- most operating / investing / financing cash-flow amount fields

Treat these as candidates for direct carry-through without quarter-differencing:

- disclosure metadata
- report type markers
- static identifiers

## 5. Statement Scope Standardization Rules

This section applies mainly to:

- `balance`
- `finance_balance_sheet_parent_current_only`

### 5.1 Main Scope Decision

Use this priority for the first production panel:

- primary balance-sheet scope: consolidated / general `balance`
- supplemental balance-sheet scope: parent-company `finance_balance_sheet_parent_current_only`

Reason:

- the general `balance` table is more complete across the 42-bank universe
- the finance balance table explicitly carries a parent-company-style scope
- we should not force-merge those two scopes into one numeric series

### 5.2 Standardized Handling

For overlapping balance-sheet fields:

- keep the general `balance` value as the main standardized value
- keep the finance-parent value as a parallel auxiliary field only when useful
- do not replace general `balance.total_assets` with finance-parent `total_assets`
- do not replace general `balance.total_liability` with finance-parent `total_liability`

### 5.3 Parent-Scope Retention

Keep parent-company-only fields in a separate namespace:

- `parent_*`
- or an equivalent explicit source-scope prefix in later cleaned tables

## 6. Source Priority Rules

### 6.1 Income Statement

First-round priority:

- primary source: `finance_income_statement_current_only`
- secondary source: `income`

Reason:

- the dedicated financial-company income statement is more native to bank reporting structure
- it carries more banking-specific flow fields

### 6.2 Cash-Flow Statement

First-round priority:

- primary source: `finance_cashflow_statement_current_only`
- secondary source: `cash_flow`

Reason:

- the dedicated financial-company cash-flow table is more expressive for banks
- it includes more banking-specific operating cash-flow components

### 6.3 Balance Sheet

First-round priority:

- primary source: `balance`
- supplemental source: `finance_balance_sheet_parent_current_only`

### 6.4 Financial Indicators

Priority:

- primary source: `indicator`
- supplemental source: `bank_indicator`

Interpretation:

- `indicator` is part of the quarterly standardized backbone
- `bank_indicator` is a lower-frequency annual bank-specialized layer

## 7. Known Missingness Rules

### 7.1 Quarterly Statement Tail

Current observed rule:

- all 42 banks are missing `2026q2`, `2026q3`, `2026q4` in the ordinary quarterly statement layer

Interpretation:

- this is expected under the current window end date `2026-05-01`
- do not treat it as a data-quality failure

### 7.2 Bank Annual Indicator Gap

Current observed rule:

- all 42 banks are missing `bank_indicator` for `2024`, `2025`, `2026`

Interpretation:

- treat `bank_indicator` as usable through the last available year only
- do not forward-fill these years blindly into the model panel

Fallback direction when needed:

- use quarterly `indicator`
- use standardized financial-company statement fields
- derive substitute ratios directly from standardized balance / income / cash-flow layers

## 8. First-Round Output Design

For every standardized numeric field, store:

- `code`
- `report_period_end`
- `pub_date`
- `standard_field_name`
- `standard_value`
- `source_table`
- `source_field`
- `period_basis`
- `statement_scope`
- `transformation_rule`

Recommended values:

- `period_basis`:
  - `point_in_time`
  - `single_quarter`
  - `ytd_raw`
  - `converted_from_ytd`
- `statement_scope`:
  - `general`
  - `financial_company`
  - `parent`
  - `annual_bank_indicator`

## 9. Immediate Next Steps

1. build a field mapping catalog for overlapping statement fields
2. classify overlapping fields into:
   - same meaning, same scope
   - same meaning, different period basis
   - same meaning, different statement scope
   - source-specific only
3. implement cumulative-to-single-quarter conversion for income and cash-flow families
4. build the first cleaned quarterly panel on top of those rules
