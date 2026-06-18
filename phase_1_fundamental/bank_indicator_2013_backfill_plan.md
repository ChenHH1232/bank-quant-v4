# 2013 Bank Indicator Backfill Plan

Goal:
- backfill the missing `2013` annual bank-indicator layer
- unlock `2014q1` to `2014q3` valid-quarter eligibility where possible

Why this exists:
- current standardized `bank_indicator` coverage for legacy listed banks starts at `2014`
- the valid-data rule requires at least one prior annual bank-indicator snapshot
- therefore `2014q1` to `2014q3` currently fail with `no_prior_annual_bank_indicator`

- Legacy banks needing 2013 backfill: `16`

Core fields to backfill first:
- `capital_adequacy_ratio` / `资本充足率` -> `bank_indicator__capital_adequacy_ratio`
- `core_level_capital_adequacy_ratio` / `核心一级资本充足率` -> `bank_indicator__core_level_capital_adequacy_ratio`
- `cost_to_income_ratio` / `成本收入比` -> `bank_indicator__cost_to_income_ratio`
- `deposit_loan_ratio` / `存贷比` -> `bank_indicator__deposit_loan_ratio`
- `net_interest_margin` / `净息差` -> `bank_indicator__net_interest_margin`
- `non_interest_income_ratio` / `非利息收入占比` -> `bank_indicator__non_interest_income_ratio`
- `non_performing_loan_provision_coverage` / `拨备覆盖率` -> `bank_indicator__non_performing_loan_provision_coverage`
- `Nonperforming_loan_rate` / `不良贷款率` -> `bank_indicator__Nonperforming_loan_rate`

Outputs:
- [bank_indicator_2013_backfill_banks.csv](D:\hh\codex\v4\phase_1_fundamental\bank_indicator_2013_backfill_banks.csv)
- [bank_indicator_2013_backfill_fields.csv](D:\hh\codex\v4\phase_1_fundamental\bank_indicator_2013_backfill_fields.csv)
- [run_2013_bank_indicator_backfill_download.ps1](D:\hh\codex\v4\phase_1_fundamental\run_2013_bank_indicator_backfill_download.ps1)

Suggested next step:
- download the 2013 Eastmoney annual reports for the legacy-bank subset
- then build a 2013-only candidate queue and extraction pass for the eight core fields