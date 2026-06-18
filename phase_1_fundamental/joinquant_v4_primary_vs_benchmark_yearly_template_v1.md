# JoinQuant V4 Primary vs Benchmark Yearly Template V1

## Scope

- Purpose: compare `primary` and `benchmark` on the same annual review frame
- Suggested source files:
  - `joinquant_v4_annual_yearly_summary_v1.csv`
  - future `joinquant_v4_benchmark_annual_attribution_v1.csv`
- Coverage target: 2021 to 2025

## How To Use

1. Run the JoinQuant strategy once with `g.strategy_line = 'primary'`.
2. Run the same strategy again with `g.strategy_line = 'benchmark'`.
3. Extract yearly summaries for both lines into the CSV template.
4. Fill the annual comparison notes below.

## Yearly Comparison Table

Use this file together with:

- `joinquant_v4_primary_vs_benchmark_yearly_template_v1.csv`

Recommended fill order:

- `primary_rebalance_dates`
- `benchmark_rebalance_dates`
- `primary_active_plans`
- `benchmark_active_plans`
- `primary_core_holdings`
- `benchmark_core_holdings`
- `common_holdings`
- `primary_only_holdings`
- `benchmark_only_holdings`
- yearly return and drawdown fields
- final `comparison_takeaway`

## Annual Review Skeleton

### 2021

- Primary style:
- Benchmark style:
- Common holdings:
- Main differences:
- Return comparison:
- Drawdown comparison:
- Takeaway:

### 2022

- Primary style:
- Benchmark style:
- Common holdings:
- Main differences:
- Return comparison:
- Drawdown comparison:
- Takeaway:

### 2023

- Primary style:
- Benchmark style:
- Common holdings:
- Main differences:
- Return comparison:
- Drawdown comparison:
- Takeaway:

### 2024

- Primary style:
- Benchmark style:
- Common holdings:
- Main differences:
- Return comparison:
- Drawdown comparison:
- Takeaway:

### 2025

- Primary style:
- Benchmark style:
- Common holdings:
- Main differences:
- Return comparison:
- Drawdown comparison:
- Takeaway:

## Suggested Comparison Angles

- Whether the improvement layer changed holdings materially
- Whether `primary` rotated earlier into large banks or stayed longer in mid-sized quality banks
- Whether `primary` improved returns mainly through stock selection or mainly through avoiding drawdown
- Whether differences are concentrated in May annual refreshes or also persist in September and November rebalances

## Implementation Reminder

- The current JoinQuant implementation determines the active annual plan using `factor_date`, not actual rebalance date.
- So both `primary` and `benchmark` should be compared under the same execution convention before we judge relative performance.
