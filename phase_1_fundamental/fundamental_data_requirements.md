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

Preferred provider:

- JoinQuant first
- Tushare supplement: `daily`, `daily_basic`, `pro_bar`

### 2.3 Three Core Financial Statements

- income statement
- balance sheet
- cash flow statement

Required structure:

- report period
- publish / disclosure date
- statement type if the provider distinguishes merged / parent / adjusted versions

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

Preferred provider:

- JoinQuant first
- Tushare supplement: `income`, `balancesheet`, `cashflow`

### 2.4 Financial-Industry Statements / Bank-Focused Fields

This group is mandatory.

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

- Raw data collection window: `2013-05-01` to `2026-05-01`
- Research window for rolling modeling: `2014-05-01` to `2026-05-01`
- Target backtest window: `2021-05-01` to `2026-05-01`
- Reason for the earlier raw-data start:
  - reserve at least one year of lookback for momentum, mean-reversion, trailing metrics, and other lagged derived features
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
