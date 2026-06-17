# Model Field Whitelist V1

Updated: 2026-06-17

Basis:

- built from the full 42-bank standardized output
- uses missingness analysis from `field_missingness_analysis.csv`
- respects the current statement-standardization rules already fixed in Phase 1

## 1. Screening Rule

Primary quarterly whitelist rule:

- prefer fields with full-sample missing ratio `<= 10%`
- keep only fields with stable interpretation under the current source-priority rules
- exclude fields whose current usefulness is weakened mainly by source-scope ambiguity

Secondary annual / special-layer rule:

- allow some fields above 10% missingness only when the gap is known to be systematic and explainable
- current example:
  - `bank_indicator` missingness is heavily driven by provider-wide absence in `2024`, `2025`, `2026`

## 2. Primary Quarterly Whitelist

### 2.1 Income

Recommended for the first model panel:

- `operating_revenue`
- `interest_income`
- `interest_expense`
- `commission_income`
- `commission_expense`
- `investment_income`
- `operating_profit`
- `total_profit`
- `income_tax_expense`
- `net_profit`
- `np_parent_company_owners`

Keep but mark as slightly weaker:

- `minority_profit`

Defer for now:

- `credit_impairment_loss`
- `asset_impairment_loss`

Reason:

- they currently have much higher missingness than the core income-flow block

### 2.2 Cash Flow

Recommended for the first model panel:

- `cash_and_equivalents_at_end`
- `cash_equivalent_increase`
- `cash_equivalents_at_beginning`
- `invest_cash_paid`
- `net_invest_cash_flow`
- `net_operate_cash_flow`
- `staff_behalf_paid`
- `subtotal_invest_cash_inflow`
- `subtotal_invest_cash_outflow`
- `subtotal_operate_cash_inflow`
- `subtotal_operate_cash_outflow`
- `net_finance_cash_flow`
- `interest_and_commission_cashin`
- `invest_withdrawal_cash`
- `subtotal_finance_cash_outflow`
- `fix_intan_other_asset_acqui_cash`
- `net_loan_and_advance_increase`
- `tax_payments`
- `invest_proceeds`
- `exchange_rate_change_effect`

Keep as optional extension candidates:

- `net_deposit_increase`
- `cash_from_borrowing`
- `cash_from_bonds_issue`
- `borrowing_repayment`
- `dividend_interest_payment`

### 2.3 Indicator

Recommended for the first model panel:

- `eps`
- `adjusted_profit`
- `operating_profit`
- `value_change_profit`
- `roe`
- `inc_return`
- `roa`
- `net_profit_margin`
- `expense_to_total_revenue`
- `operation_profit_to_total_revenue`
- `net_profit_to_total_revenue`
- `ocf_to_revenue`
- `inc_total_revenue_annual`
- `inc_revenue_annual`
- `inc_operation_profit_annual`
- `inc_net_profit_annual`
- `inc_net_profit_to_shareholders_annual`

Keep as optional extension candidates:

- `ga_expense_to_total_revenue`
- `ocf_to_operating_profit`
- `operating_profit_to_profit`
- `inc_total_revenue_year_on_year`
- `inc_revenue_year_on_year`
- `inc_operation_profit_year_on_year`
- `inc_net_profit_year_on_year`
- `inc_net_profit_to_shareholders_year_on_year`

Defer for now:

- `gross_profit_margin`

Reason:

- banks do not always expose a stable gross-margin-style series in a useful way

### 2.4 Balance

Recommended for the first model panel:

- `cash_equivalents`
- `deferred_tax_assets`
- `lend_capital`
- `paidin_capital`
- `retained_profit`
- `total_assets`
- `total_liability`
- `total_owner_equities`
- `capital_reserve_fund`
- `equities_parent_company_owners`
- `ordinary_risk_reserve_fund`
- `surplus_reserve_fund`
- `taxs_payable`
- `salaries_payable`

Keep as optional extension candidates:

- `deposit_in_interbank`
- `fixed_assets`
- `borrowing_capital`
- `trading_assets`
- `sold_buyback_secu_proceeds`
- `loan_and_advance`
- `interest_receivable`

Defer for the first model panel:

- highly sparse balance-sheet tail fields
- fields whose economic meaning is too niche for the first-round factor pass

## 3. Supplemental Layers

### 3.1 Parent Balance

Current policy:

- do not place `parent_balance` into the main model whitelist
- keep it as an auxiliary diagnostic layer

Reason:

- even the best `parent_balance` fields have about `19%+` missingness
- a large part of that is `missing_target_report`
- this is useful for follow-up robustness work, but not ideal for the first main panel

### 3.2 Bank Indicator

Recommended annual supplemental whitelist:

- `Nonperforming_loan_rate`
- `capital_adequacy_ratio`
- `core_level_capital_adequacy_ratio`
- `cost_to_income_ratio`
- `deposit_loan_ratio`
- `net_interest_margin`
- `non_interest_income_ratio`
- `non_performing_loan_provision_coverage`
- `total_deposit`
- `total_loan`
- `weighted_risky_asset`

Interpretation:

- these are important banking-specific factors
- current missingness around `29%` is mainly driven by provider-wide absence in `2024-2026`
- keep them in the research panel with explicit annual-layer handling
- do not force them into the same completeness expectation as quarterly fields

## 4. Explicit Deferrals

Defer from the first model panel:

- `asset_impairment_loss`
- `credit_impairment_loss`
- `gross_profit_margin`
- most `parent_balance` fields
- ultra-sparse `bank_indicator` tail fields
- rare or source-specific supervisory details

## 5. Operational Recommendation

Build the first model-ready Phase 1 panel in two layers:

### 5.1 Main Quarterly Layer

Include:

- income whitelist
- cash-flow whitelist
- indicator whitelist
- balance whitelist

### 5.2 Annual Banking Layer

Include:

- selected `bank_indicator` whitelist fields

Merge rule:

- align by disclosure timing
- allow annual banking fields to update at annual frequency
- avoid fake quarterly forward-fill unless a later research note explicitly allows it

## 6. Files To Use

- missingness analysis: [field_missingness_analysis.csv](D:/hh/codex/v4/phase_1_fundamental/field_missingness_analysis.csv)
- full-sample summary: [all_banks_standardization_summary.csv](D:/hh/codex/v4/phase_1_fundamental/standardized_outputs/all_banks_standardization_summary.csv)
- missingness pivot: [all_banks_missing_reason_pivot.csv](D:/hh/codex/v4/phase_1_fundamental/standardized_outputs/all_banks_missing_reason_pivot.csv)
