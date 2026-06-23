# Pure Fundamental Manual Style Switch Guide 2026-06-23

Use this guide with:

- `joinquant_v4_annual_backtest_strategy_base_core_6_manual_style_switch_v1.py`

Status note:

- this guide is an execution convenience note for the current codebase
- it does **not** mean manual style switching has already been validated as a superior production framework
- the validated statement today is narrower:
  - `balanced` is the formal default line
  - `core_level` is an accepted structural variant

Switch location:

- set `g.manual_style_mode` in `initialize`
- available values:
  - `balanced`
  - `core_level`

## Default Choice

Default to `balanced`.

Reason:

- this is the current main executable pure-fundamental line
- it is the more stable all-around baseline
- repeated validation has shown it is hard to beat cleanly without adding fragile timing logic

## When To Prefer `balanced`

Prefer `balanced` when the next stage is expected to favor:

- broader profitability expression rather than only large-bank balance-sheet resilience
- cleaner stock-selection breadth across the bank universe
- a more neutral stance when there is no strong regime view

Practical reading:

- if you do not have high conviction, stay with `balanced`
- this should be treated as the safe default main line

## When To Prefer `core_level`

Prefer `core_level` when the next stage is expected to favor:

- stronger capital quality
- resilience of larger and more conservatively capitalized banks
- tighter balance-sheet preference over near-term profitability expression

Practical reading:

- use `core_level` only when you have a clear forward-looking thesis that the market will reward capital strength, safety, and balance-sheet quality more than EPS-style expression

## When Not To Switch

Do not switch just because:

- one recent backtest looked better
- one recent year was strong
- monthly or quarterly relative momentum looked interesting

Current research conclusion:

- automatic timing rules around these two styles were not strong enough
- monthly style-timing also failed executable confirmation
- therefore switching should remain a deliberate and conservative human decision, not a routine optimization loop
- if this is used in practice, the decision should ideally be recorded as an ex-ante note rather than changed retrospectively after the year is known

## Working Rule

If judgment is unclear:

- keep `balanced`

If there is a clear next-year thesis around capital strength and conservative balance sheets:

- switch to `core_level`

Recommended operational caution:

- treat `balanced` as the only formal default history line
- treat `core_level` as a shadow or explicit discretionary variant unless a future logged regime process proves useful over time
