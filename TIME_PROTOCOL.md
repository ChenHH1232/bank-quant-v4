# V4 Time Protocol

## Purpose

This document defines the official time-splitting and anti-leakage rules for the V4 research and backtest framework.

The goal is to ensure that:

- factor research does not accidentally use future data
- model selection is separated from formal out-of-sample backtest evaluation
- each rebalance decision uses only information that was actually visible at that time

## Master Date Range

- Data coverage: `2014-01-01` to `2026-05-01`
- Formal backtest start: `2021-05-01`
- Formal backtest end: `2026-05-01`

## Two-Stage Framework

### Stage 1: Research And Specification Freeze

- Time range: `2014-01-01` to `2021-05-01`
- Purpose:
  - factor definition
  - data cleaning rules
  - single-factor testing
  - multi-factor structure selection
  - label definition
  - hyperparameter comparison

Rules:

- only data dated on or before `2021-05-01` may be used
- rolling experiments are allowed only if both training and validation windows remain fully before `2021-05-01`
- no result from after `2021-05-01` may be used to select factors, thresholds, or model structure

Valid example:

- training: `2014-05-01` to `2019-05-01`
- validation: `2019-05-01` to `2021-05-01`

### Stage 2: Formal Walk-Forward Backtest

- Time range: `2021-05-01` to `2026-05-01`
- Purpose:
  - simulate realistic rolling deployment
  - evaluate true out-of-sample performance

Rules:

- on each rebalance date `T`, the model may use only information visible on or before `T`
- the rolling training window is the previous 5 years ending at `T`
- the model is retrained at each rebalance date
- predictions apply only to the future period after `T`

## Rebalance-Time Rule

For each rebalance date `T`:

- available features must be limited to data published or observable by `T`
- the stock pool must be recomputed at `T`, not fixed once for the whole backtest
- market-cap and liquidity screens must use the `T`-date market snapshot
- quarterly and annual accounting fields must respect their publication dates

## What Counts As Leakage

The following are forbidden:

- using any data from after `2021-05-01` to design the model that will later be evaluated from `2021-05-01`
- screening factors on the full sample first and then calling the post-`2021-05-01` backtest "out-of-sample"
- fitting standardization, winsorization, or imputation rules on full-sample data and reusing them in earlier periods
- assigning a financial statement to a rebalance date before the statement was publicly available
- using future price paths to define current signals

## Current V4 Implementation Implication

At the current phase:

- phase 1 single-factor testing should be limited to the research window ending on `2021-05-01`
- the formal backtest window beginning on `2021-05-01` must remain untouched for true walk-forward evaluation
- any factor admitted into the production candidate set should be justified using only pre-`2021-05-01` evidence

## Operational Summary

The clean interpretation is:

- pre-`2021-05-01`: research, compare, freeze methodology
- post-`2021-05-01`: walk-forward only, no hindsight redesign
