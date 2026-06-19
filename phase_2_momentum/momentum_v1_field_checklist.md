# Momentum V1 Field Checklist

## Objective

This checklist fixes the first-pass data contract for the momentum research branch. The goal is to support a clean annual strategy backtest from `2021-05-31` to `2026-05-31` while respecting the broader research window of `2014-01-01` to `2026-05-01`.

## Core Rule

Momentum factors must be built on exact trading dates. If a local file cannot recover the trading-date index unambiguously, that file is not considered usable for formal signal construction.

## Required Base Fields

| Field | Level | Why it is required | Local status | Preferred source |
| --- | --- | --- | --- | --- |
| `date` | daily | Align trading days, rebalance dates, and return windows | Missing in local `daily_price.csv` | JoinQuant daily price / trade calendar |
| `code` | daily | Cross-sectional merge key | Present in valuation, implicit in folder for price | JoinQuant / local universe |
| `close` | daily | Main momentum return anchor | Present | Local price after date repair |
| `open` | daily | Useful for tradability and gap checks | Present | Local price after date repair |
| `high` | daily | Optional price-range validation and limit-up diagnostics | Present | Local price after date repair |
| `low` | daily | Optional price-range validation and limit-down diagnostics | Present | Local price after date repair |
| `volume` | daily | Liquidity and trading activity filters | Present | Local price after date repair |
| `money` | daily | Turnover amount / liquidity proxy | Present | Local price after date repair |
| `turnover_ratio` | daily | Supplemental liquidity screen | Present | Local valuation |
| `market_cap` | daily | Size control / neutralization candidate | Present | Local valuation |
| `circulating_market_cap` | daily | Float-size control / liquidity context | Present | Local valuation |
| `start_date` | static | Listing-age filter and formation-window validity | Present in universe | Local universe |
| `trade_calendar` | calendar | Holiday-adjusted rebalance mapping | Not stored separately | JoinQuant trade days |

## Recommended Extension Fields

| Field | Why it helps | Current note |
| --- | --- | --- |
| `paused` | Avoids forming signals on suspended names | Prefer direct JoinQuant state query at rebalance |
| `is_st` | Filters abnormal trading status | Can be added later if strategy needs it |
| `high_limit` / `low_limit` | Helps enforce realistic execution | Better pulled directly in backtest layer |
| `factor` or adjusted-price hint | Clarifies whether returns use raw or adjusted prices | Important before finalizing momentum definitions |
| `amount_rank` / rolling liquidity stats | Stabilizes low-liquidity tails | Derived after base data is repaired |

## V1 Momentum Factors To Support

| Factor | Definition sketch | Data dependency |
| --- | --- | --- |
| `mom_1m` | 1-month cumulative return | `date`, `close` |
| `mom_3m` | 3-month cumulative return | `date`, `close` |
| `mom_6m` | 6-month cumulative return | `date`, `close` |
| `mom_12m` | 12-month cumulative return | `date`, `close` |
| `mom_12_1` | 12-month return skipping the most recent 1 month | `date`, `close` |
| `mom_6_1` | 6-month return skipping the most recent 1 month | `date`, `close` |
| `liq_turnover_1m` | 1-month average turnover ratio | `date`, `turnover_ratio` |
| `liq_money_1m` | 1-month average成交额 | `date`, `money` |

## Window Constraints

- To score the first live rebalance on `2021-05-31`, the price layer must provide enough prior history for the longest formation horizon in use.
- If `mom_12_1` is included, practical coverage should reach at least `2020-04` on a trading-day basis for already-listed banks.
- For late-listed banks, the factor engine should allow partial-universe participation instead of forcing a fake full-history backfill.

## Current Local Verdict

- Universe coverage is complete at the file level for all 42 banks.
- Valuation files are structurally ready because they already carry a daily date field.
- Price files are blocked for formal momentum work because they currently contain only `open,close,high,low,volume,money` without a date column.

## Next Data Action

1. Repair or re-download the daily price layer with explicit trading dates.
2. Confirm adjusted-price convention before defining the formal momentum return formula.
3. Keep the momentum and mean-reversion branches separated after the repaired base layer is ready.
