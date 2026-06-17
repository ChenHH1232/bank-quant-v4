# Fundamental Data Requirements

Updated: 2026-06-16

Scope:

- This phase only covers fundamental data
- Core providers:
  - JoinQuant as the preferred provider for covered A-share daily/fundamental research
  - Tushare as a supplement inside the confirmed 2000-point scope

## 1. Stock Universe

- China bank sector listed stocks
- Current target size: about 48 banks
- Include:
  - state-owned large banks
  - joint-stock banks
  - city commercial banks
  - rural commercial banks when covered by the chosen universe definition

Future universe filtering rule for the portfolio-construction stage:

- start from the bank-sector eligible universe on that rebalance date
- compute cross-sectional liquidity ranking inside the bank universe
- compute cross-sectional market-cap ranking inside the bank universe
- keep the top 80% by liquidity
- keep the top 80% by market cap
- the downstream stock pool should be based on the intersection of those two filters unless a later research note changes the rule explicitly

Current implementation note:

- this rule is not part of the raw fundamental data pull step
- during the current data-collection phase, we only need to retain the liquidity and market-cap inputs required for this future filter

## 2. Required Data Groups

### 2.1 General Market Metadata

- trading calendar
- stock code mapping
- stock list / active listed universe
- stock name and exchange metadata
- listing date
- delisting date if applicable

Preferred provider:

- JoinQuant

### 2.2 Daily Market Basics

- daily close
- daily open
- daily high
- daily low
- daily volume
- daily amount
- adjustment status or adjusted price support
- market cap
- circulating market cap
- PB
- PE if available and meaningful
- dividend yield if available

This group is mandatory not only for market context, but also because:

- daily price data will be used later to construct quarterly and annual average return targets / response variables
- daily price data is part of the `y` construction base for fundamental-phase testing
- keep both `open` and `close`
- use `close` as the primary baseline for first-round return / target construction
- keep `open` as a secondary price series for later event-timing and robustness checks
- liquidity and market-cap data from this group will also be stored for later rebalance-date stock-pool filtering
- during the current phase, these fields are collected and retained, but no stock filtering is applied at raw-download time

Additional daily-price-derived target inputs to retain:

- daily return
- forward-return construction base
- quarterly average daily return base
- annual average daily return base

Additional stock-pool filtering inputs to retain:

- daily traded amount as the primary liquidity measure
- daily traded volume as the secondary liquidity measure
- rolling average traded amount over the chosen pre-rebalance lookback window
- rolling average traded volume over the chosen pre-rebalance lookback window
- market cap
- circulating market cap
- turnover rate when a stable provider path is confirmed

Current working rule for first-round universe construction:

- use rolling average daily traded amount as the primary liquidity ranking signal
- use market cap as the primary size ranking signal
- retain circulating market cap and volume so we can test alternative liquidity / size filters later without a second raw-data pull

Preferred provider:

- JoinQuant first
- Tushare supplement: `daily`, `daily_basic`, `pro_bar`

### 2.3 Three Core Financial Statements

- income statement
- balance sheet
- cash flow statement

Important interpretation for financial institutions:

- For banks, securities firms, and insurers, we should not treat these as ordinary industrial-company statements only
- We must collect:
  - the general three-statement interface layer
  - the dedicated financial-industry three-statement interface layer
  - the financial-industry-specific fields embedded inside those statement interfaces
- In current JoinQuant SDK usage, this means:
  - `balance`
  - `income`
  - `cash_flow`
  are still the base statement interfaces
  - and dedicated financial-company statement interfaces are also available under `finance.*`
  - but we must explicitly retain the financial-company fields inside them rather than only keeping generic industrial fields

Required structure:

- report period
- publish / disclosure date
- statement type if the provider distinguishes merged / parent / adjusted versions
- quarterly coverage is required for:
  - `balance`
  - `income`
  - `cash_flow`
  - `indicator`
  - dedicated `finance.*` financial-company statement tables

Key fields to prioritize:

- revenue
- operating profit
- total profit
- net profit attributable to parent
- interest income
- interest expense
- net interest income if directly available
- fee and commission income
- investment income
- credit impairment loss
- assets total
- liabilities total
- shareholder equity
- loans and advances
- deposits
- cash and cash equivalents
- operating cash flow
- settlement provisions if applicable
- lend capital
- trading assets
- bought sellback assets
- interest receivable / related banking fields when present
- deposits in interbank / central-bank-related fields when present

Preferred provider:

- JoinQuant first
- Tushare supplement: `income`, `balancesheet`, `cashflow`

Dedicated financial-company three-statement interfaces confirmed in local testing:

- `finance.FINANCE_INCOME_STATEMENT`
- `finance.FINANCE_CASHFLOW_STATEMENT`
- `finance.FINANCE_BALANCE_SHEET_PARENT`

Observed examples of financial-specific fields in these dedicated interfaces:

- `finance.FINANCE_INCOME_STATEMENT`
  - `interest_net_revenue`
  - `interest_income`
  - `interest_expense`
  - `commission_net_income`
  - `commission_income`
- `finance.FINANCE_CASHFLOW_STATEMENT`
  - `operate_cash_flow`
  - `net_loan_and_advance_decrease`
  - `net_deposit_increase`
  - `net_borrowing_from_central_bank`
- `finance.FINANCE_BALANCE_SHEET_PARENT`
  - `deposit_in_ib`
  - `cash_equivalents`
  - `deposit_client`
  - `cash_in_cb`
  - `settlement_provi`
  - `settlement_provi_client`

### 2.4 Financial-Industry Statements / Bank-Focused Fields

This group is mandatory.

Important rule:

- Treat this as a third mandatory layer in addition to:
  - the general three statements
  - the dedicated financial-company three-statement interfaces
- For banks, we need both:
  - financial-company statement fields from `balance / income / cash_flow`
  - dedicated financial-company statement tables from `finance.*`
  - standalone bank-specific indicators from `bank_indicator`
- current working assumption:
  - `bank_indicator` is primarily annual or sparse-reporting coverage
  - do not assume quarterly completeness for `bank_indicator` unless separately verified

Key bank-specific metrics to collect if covered:

- net interest margin
- non-performing loan ratio
- provision coverage ratio
- loan loss provision ratio / provision-to-loan style fields
- capital adequacy ratio
- core tier-1 capital adequacy ratio
- tier-1 capital adequacy ratio
- cost-to-income ratio
- non-interest income ratio
- deposit-loan ratio or comparable structure fields if available
- impairment / credit cost related fields

Preferred provider:

- JoinQuant first
- Tushare supplement only when the exact field is clearly supported

Relevant JoinQuant table objects already confirmed in local testing:

- `balance`
- `income`
- `cash_flow`
- `indicator`
- `bank_indicator`
- `finance.FINANCE_INCOME_STATEMENT`
- `finance.FINANCE_CASHFLOW_STATEMENT`
- `finance.FINANCE_BALANCE_SHEET_PARENT`

Observed examples of financial-company-specific statement fields already returned for Ping An Bank 2020:

- `balance`
  - `settlement_provi`
  - `lend_capital`
  - `trading_assets`
  - `bought_sellback_assets`
- `income`
  - `interest_income`
  - `commission_income`
  - `asset_impairment_loss`
- `cash_flow`
  - `net_deposit_increase`
  - `net_borrowing_from_central_bank`
  - `interest_and_commission_cashin`
  - `net_loan_and_advance_increase`

Operational constraint confirmed in local testing:

- Current JoinQuant account `auth license = 1`
- Fundamental download scripts should use a single authenticated connection and avoid parallel fetches against JoinQuant

### 2.5 Financial Indicator Layer

- ROE
- ROA
- EPS
- BVPS
- net profit growth
- revenue growth
- asset growth
- equity growth
- leverage related metrics

Preferred provider:

- Tushare `fina_indicator` where appropriate
- JoinQuant if the same metric is easier to align with bank statements

## 3. Time Coverage

- Raw data collection window: `2014-01-01` to `2026-05-01`
- Research window for rolling modeling: `2014-01-01` to `2026-05-01`
- Target backtest window: `2021-05-01` to `2026-05-01`
- Reason for the earlier start:
  - ensure full coverage of 2014 Q1 financial reporting data
  - keep enough history for early derived features inside the current research window design
- Final model research window should still obey the V4 rolling protocol

## 4. Alignment Rules

- Use disclosure-date-aware alignment
- Do not use statement values before they were publicly available
- Keep annual and quarterly frequencies distinguishable
- Preserve report period and disclosure date as separate fields

## 5. Cleaning Rules

- keep raw downloads unchanged in a raw layer
- create cleaned tables separately
- record missingness by field and by bank
- standardize units before factor construction
- detect duplicated rows by stock, report period, and statement type

## 6. First Statistical Testing Targets

Initial factor families to test in Phase 1:

- valuation
  - PB
  - dividend yield
- profitability
  - ROE
  - ROA
- growth
  - net profit growth
  - revenue growth
- asset quality
  - non-performing loan ratio
  - provision coverage ratio
- capital strength
  - capital adequacy ratio
  - core tier-1 capital adequacy ratio
- business structure
  - non-interest income ratio
  - cost-to-income ratio

## 7. Deliverables

- raw source mapping table
- cleaned fundamental panel
- disclosure-date alignment log
- missing-data summary
- first-round factor test report for fundamentals only
