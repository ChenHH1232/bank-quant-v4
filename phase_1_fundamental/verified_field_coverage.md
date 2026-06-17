# Verified Field Coverage

Updated: 2026-06-16

Verification basis:

- Spot-checked on Ping An Bank
  - JoinQuant code: `000001.XSHE`
  - Tushare code: `000001.SZ`
- Main validation target:
  - confirm whether core fundamental fields are actually reachable under the current account permissions
  - distinguish `verified available` from `documented but not yet validated`

## 1. JoinQuant: verified available

### 1.1 Daily valuation / market-cap style fields

- `pb_ratio`
- `pe_ratio`
- `market_cap`
- `circulating_market_cap`
- `turnover_ratio`

Validation note:

- Retrieved successfully through `valuation` in local testing
- `turnover_ratio_f` was not supported in the current JoinQuant SDK/API path, so do not assume it is available in production pulls

### 1.2 Daily price / liquidity base fields

- `open`
- `close`
- `high`
- `low`
- `volume`
- `money`

Validation note:

- Retrieved successfully through `get_price(..., fields=["open", "close", "high", "low", "volume", "money"])` in local testing
- This is enough to construct first-round liquidity filters from rolling average traded amount and rolling average traded volume
- Combined with `market_cap` and `circulating_market_cap`, the current JoinQuant path already covers the planned bank-universe top-80% liquidity and size screening backbone

### 1.3 General statement-layer fields

From `income`:

- `np_parent_company_owners`
- `operating_profit`
- `total_profit`
- `interest_income`
- `commission_income`
- `asset_impairment_loss`

From `balance`:

- `total_assets`
- `total_liability`
- `cash_equivalents`
- `lend_capital`
- `trading_assets`

### 1.4 Financial indicator layer

- `roe`
- `roa`
- `eps`
- `inc_total_revenue_year_on_year`
- `inc_net_profit_to_shareholders_year_on_year`

### 1.5 Bank-specific indicator layer

- `net_interest_margin`
- `Nonperforming_loan_rate`
- `non_performing_loan_provision_coverage`
- `capital_adequacy_ratio`
- `core_level_capital_adequacy_ratio`
- `cost_to_income_ratio`
- `non_interest_income_ratio`
- `deposit_loan_ratio`
- `total_loan`
- `total_deposit`
- `weighted_risky_asset`

### 1.6 Dedicated financial-company statement interfaces confirmed

- `finance.FINANCE_INCOME_STATEMENT`
- `finance.FINANCE_CASHFLOW_STATEMENT`
- `finance.FINANCE_BALANCE_SHEET_PARENT`

Important note:

- these dedicated financial-company tables return both current-period and comparative rows
- current production assumption:
  - keep `report_type = 0` as the main current-period record
  - treat `report_type = 1` as bundled comparative context, not as an additional quarter

## 2. Tushare: verified available

### 2.1 Income statement fields

- `n_income_attr_p`
- `total_profit`
- `revenue`
- `int_income`
- `comm_income`

### 2.2 Balance-sheet fields

- `total_assets`
- `total_liab`
- `total_hldr_eqy_exc_min_int`
- `trad_asset`

### 2.3 Financial-indicator fields

- `roe`
- `eps`
- `bps`
- `or_yoy`
- `netprofit_yoy`
- `assets_yoy`
- `equity_yoy`

## 3. Tushare: documented but not stably validated in current environment

### 3.1 Daily basic market fields

- `pb`
- `pe`
- `total_mv`
- `circ_mv`
- `turnover_rate`
- `turnover_rate_f`

Current status:

- API scope should be allowed under the current 2000-point account
- local test failed due to proxy / connectivity instability, not a confirmed permission denial
- treat these fields as `likely available but network-path unverified`
- if later validated, Tushare `daily_basic` can serve as a useful cross-check source for size and turnover-based liquidity screens

### 3.2 Intermittent nulls

- `roa` in `fina_indicator` returned `None` in the current spot check

Current rule:

- do not assume every fundamental field is complete for every bank-period
- missing-value handling is mandatory

## 4. Not yet verified, do not assume available

- special-regulatory detail fields beyond the currently validated `bank_indicator` set
- detailed watch-list loan ratios
- overdue-loan breakdowns
- more granular five-category loan-classification splits
- other ultra-specific supervisory disclosure metrics

Recommended search order when needed:

1. `JoinQuant bank_indicator`
2. `JoinQuant finance.FINANCE_*`
3. `JoinQuant balance / income / cash_flow / indicator`
4. `Tushare income / balancesheet / cashflow / fina_indicator / daily_basic`
5. annual report / announcement extraction as a later fallback

## 5. Operational conclusion

- The current data plan already covers most of the first-round bank fundamental backbone
- JoinQuant should remain the primary source
- Tushare should be treated as a supplement and cross-check source
- The first production pull should focus on fields that are already verified, then expand to the unverified tail
