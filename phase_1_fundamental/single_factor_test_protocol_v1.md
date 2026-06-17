# Single-Factor Test Protocol V1

Updated: 2026-06-17

## Purpose

This document defines the official single-factor testing protocol for Phase 1 fundamental research.

The protocol is designed to:

- respect the V4 anti-leakage time rules
- test every currently usable factor on valid data segments
- separate in-sample factor setup from out-of-sample validation
- produce a consistent pass/fail decision for later multi-factor admission

## Fixed Time Window

Research window version: `V1`

- training window: `2014-05-01` to `2019-05-01`
- validation window: `2019-05-01` to `2021-05-01`

Important rule:

- the validation window is not allowed to participate in factor-direction choice, preprocessing design, threshold selection, or transformation selection

## Testing Universe

Use only rows that satisfy all of the following:

- row exists in [phase1_training_panel.csv](/D:/hh/codex/v4/phase_1_fundamental/phase1_training_panel.csv)
- row belongs to the valid disclosed-data segment framework
- row belongs to the dynamic rebalance framework
- row has `rebalance_stock_pool_flag = 1`

This means the single-factor study is performed only on the tradable effective sample of each rebalance date.

## Label Mapping

### Quarterly factors

Primary label:

- `y_quarter_avg_daily_return_close`

Applies to:

- quarterly accounting fields
- quarterly indicator fields
- quarterly-improvement variants that will be added later

### Annual bank-specific factors

Primary label:

- `y_year_avg_daily_return_close`

Applies to:

- `bank_indicator__*`

Secondary optional reference:

- annual factors may also be observed against quarterly `y`, but annual `y` is the formal first-pass evaluation target

## Factor Setup Procedure

For each factor, training-period work is allowed to determine:

1. signal direction
   - larger-is-better
   - smaller-is-better

2. preprocessing choice
   - raw
   - winsorized
   - standardized
   - optional log transform if strongly skewed

3. grouping scheme
   - primary: 5 groups
   - robustness check: 3 groups

Important constraint:

- all preprocessing parameters must be learned from the training window only

## Primary Metrics

Each factor should at minimum report the following for both training and validation windows.

### Cross-sectional statistics

- mean Rank IC
- Rank IC IR
- positive-IC ratio

### Portfolio structure statistics

- 5-group average returns
- top-minus-bottom return spread
- monotonicity check

### Sample statistics

- number of rebalance dates
- number of usable rows
- missing ratio inside the tradable sample

## Pass / Watch / Reject Rule

### Pass

A factor is marked `A` when:

- training-window direction is clear
- validation-window direction does not reverse
- and at least one structure signal remains acceptable in validation:
  - monotonic grouping shape
  - top-minus-bottom spread
  - positive mean Rank IC

### Watch

A factor is marked `B` when:

- training-window evidence is acceptable
- validation weakens materially
- but the sign does not clearly reverse

### Reject

A factor is marked `C` when:

- validation reverses direction
- or training strength disappears with no usable validation structure

### Deferred

A factor is marked `D` when:

- tradable-sample coverage is too low
- or missingness is too high for stable interpretation

## Current Implementation Scope

Phase 1 first-pass testing should cover all currently modeled feature columns in:

- income family
- cash_flow family
- indicator family
- balance family
- bank_indicator family

But exclude:

- identifiers
- pool flags
- market snapshot helper columns
- target columns
- bank-indicator source-year helper columns

## Standard Result Card

Each tested factor should eventually output:

- factor_name
- factor_family
- target_label
- training_rows
- validation_rows
- training_rank_ic_mean
- validation_rank_ic_mean
- training_rank_ic_ir
- validation_rank_ic_ir
- training_positive_ic_ratio
- validation_positive_ic_ratio
- training_top_minus_bottom
- validation_top_minus_bottom
- training_monotonic_flag
- validation_monotonic_flag
- final_status
- notes

## Next Build Target

The first implementation step is:

- build a candidate factor manifest from `phase1_training_panel.csv`
- classify each factor to quarterly-label or annual-label evaluation
- then implement the actual metric engine on top of this manifest
