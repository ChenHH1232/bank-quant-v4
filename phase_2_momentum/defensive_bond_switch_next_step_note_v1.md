# Defensive Bond Switch Next Step Note V1

Current status:
- the bond-switch research direction is defined
- but the local rolling validation cannot be completed yet because the defensive bond sleeve does not have a prepared local forward-return panel

## Missing Input

Required file:
- `bond_defensive_panel_v1.csv`

Required columns:
- `rebalance_date`
- `bond_code`
- `bond_forward_return`

Recommended first-pass instrument:
- `511010.XSHG`

## Why This Blocks Rolling

The current bank rolling panel already provides:
- bank cross-sectional features
- bank forward target returns
- observable state proxy

But the weak-state bond-switch branch additionally needs:
- the forward return of the defensive bond ETF on the same rebalance dates

Without that column, we cannot honestly compare:
- weak-state bank-only fallback
- weak-state bond substitution

## Prepared Scaffold

The loader scaffold is ready in:
- [build_defensive_bond_switch_rolling_validation_v1.py](D:\hh\codex\v4\phase_2_momentum\build_defensive_bond_switch_rolling_validation_v1.py)

That script currently does one job:
- verify whether the local bond panel exists and has the required columns

## Immediate Next Step

The next concrete action should be:
- download or export `511010.XSHG` history
- convert it into rebalance-date aligned `bond_forward_return`
- save it as `bond_defensive_panel_v1.csv`
- then finish the rolling comparison against:
- fixed `60/40`
- state-gated bank-only dual engine
- pure fundamental

## Practical Judgment

So the bond-switch line is:
- structurally ready
- data-blocked, not logic-blocked
