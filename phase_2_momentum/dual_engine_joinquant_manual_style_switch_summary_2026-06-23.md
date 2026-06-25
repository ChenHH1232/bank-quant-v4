# Dual-Engine JoinQuant Manual-Style Switch Summary 2026-06-23

Date: `2026-06-23`

Core code:

- [joinquant_v4_dual_engine_manual_style_switch_v1.py](D:/hh/codex/v4/phase_2_momentum/joinquant_v4_dual_engine_manual_style_switch_v1.py)

Related rolling note:

- [fundamental_momentum_dual_engine_rolling_test_v3.md](D:/hh/codex/v4/phase_2_momentum/fundamental_momentum_dual_engine_rolling_test_v3.md)

## Purpose

This note records the first JoinQuant full-backtest check for the two dual-engine candidates that were promoted from the updated pure-fundamental main line:

- `balanced_60_40`
- `core_level_shadow_70_30`

The implementation keeps one JoinQuant file and switches variants in `initialize`.

## Variant Definitions

- `balanced_60_40`
  - fundamental sleeve = `balanced`
  - budget split = fundamental `60%` + momentum `40%`
- `core_level_shadow_70_30`
  - fundamental sleeve = `core_level_shadow`
  - budget split = fundamental `70%` + momentum `30%`

Shared execution logic:

- fundamental sleeve uses the validated annual manual-style plan library
- momentum sleeve uses monthly `12-1`
- liquidity + market-cap pool filter remains unchanged
- engine cap = `5%`
- final stock cap = `8%`

## Rolling Expectation Before JoinQuant

Pre-2021 rolling gave this internal ordering:

- best `60/40` branch = `balanced`
- best `70/30` branch = `core_level_shadow`

This did not prove either branch should replace the pure-fundamental live main line.
It only suggested:

- `balanced_60_40` is the stronger candidate inside the `60/40` allocation
- `core_level_shadow_70_30` is the stronger candidate inside the `70/30` allocation

## JoinQuant Full-Backtest Results

### 1. `balanced_60_40`

- strategy return = `36.21%`
- annualized return = `6.59%`
- excess return = `13.64%`
- alpha = `0.028`
- beta = `0.885`
- sharpe = `0.166`
- max drawdown = `18.63%`
- excess max drawdown = `8.87%`
- excess sharpe = `-0.260`
- volatility = `0.156`

Interpretation:

- this branch is clearly more defensive than the current pure-fundamental main line
- it gives up too much upside to become the new default main line
- its value is mainly lower portfolio risk and shallower excess-drawdown path

### 2. `core_level_shadow_70_30`

- strategy return = `39.14%`
- annualized return = `7.06%`
- excess return = `16.09%`
- alpha = `0.032`
- beta = `0.825`
- sharpe = `0.209`
- max drawdown = `18.79%`
- excess max drawdown = `8.55%`
- excess sharpe = `-0.158`
- volatility = `0.146`

Interpretation:

- this branch improves on `balanced_60_40` on almost every important dimension
- it earns more, carries lower beta, has lower volatility, and slightly better excess-drawdown behavior
- total max drawdown is nearly the same as `balanced_60_40`, so the small difference there is not decisive

## Internal Ranking Inside Dual-Engine

Current ordering after JoinQuant:

1. `core_level_shadow_70_30`
2. `balanced_60_40`

Why:

- `core_level_shadow_70_30` has higher return and annualized return
- `core_level_shadow_70_30` has higher excess return
- `core_level_shadow_70_30` has lower `beta`
- `core_level_shadow_70_30` has lower volatility
- `core_level_shadow_70_30` has slightly better excess max drawdown

## Position Versus Pure-Fundamental Main Line

Current pure-fundamental main line benchmark:

- pure-fundamental `balanced`
- strategy return = `48.38%`
- annualized return = `8.49%`
- max drawdown = `22.29%`
- excess max drawdown = `11.47%`

Comparison:

- pure-fundamental `balanced` remains the stronger return engine
- dual-engine `core_level_shadow_70_30` is the stronger risk-controlled execution alternative
- dual-engine `balanced_60_40` is now a weaker neighbor and no longer the preferred dual-engine representative

Practical reading:

- if the objective is maximum validated return, stay with pure-fundamental `balanced`
- if the objective is a smoother path with lower beta and lower volatility, the best current dual-engine branch is `core_level_shadow_70_30`

## Working Conclusion

The dual-engine line is currently best treated as a defensive backup line, not the primary return main line.

Scope note:

- this is a project-level conclusion tied to the current A-share bank universe, the `mom_12_1` momentum definition, and the independent sleeve-combination framework
- it should not be generalized into a claim that momentum is universally invalid for all bank stocks or all execution structures

Current hierarchy:

- primary return main line = pure-fundamental `balanced`
- defensive backup line = dual-engine `core_level_shadow_70_30`
- secondary dual-engine branch = `balanced_60_40`

## Next-Step Discipline

- do not promote the dual-engine line over pure-fundamental `balanced` on return grounds
- if we retain one dual-engine branch for future use, retain `core_level_shadow_70_30`
- future evaluation should pay extra attention to:
  - excess max drawdown
  - beta
  - volatility
  - whether lower-risk behavior remains stable out of sample
