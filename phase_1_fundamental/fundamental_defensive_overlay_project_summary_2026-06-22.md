# Fundamental Defensive Overlay Project Summary

Date: `2026-06-22`

## Objective

Starting from the original pure-fundamental annual bank strategy, validate whether a defensive overlay based on fundamental deterioration can improve out-of-sample behavior.

Research order:

1. local rolling validation with only then-available data
2. freeze candidate rule
3. move the frozen rule into JoinQuant for full strategy backtest

## Scope We Validated

- deterioration trigger rule
- equity weight mapping after trigger
- defensive sleeve choice among `cash`, `511260.XSHG`, `511010.XSHG`

Core deterioration metrics considered locally:

- `npl`
- `capital`
- `coverage`
- `roe`
- `profit_growth`

## Local Rolling Validation

Script:

- [build_fundamental_defensive_overlay_rolling_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_fundamental_defensive_overlay_rolling_validation_v1.py)

Outputs:

- [fundamental_defensive_overlay_rolling_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/fundamental_defensive_overlay_rolling_validation_v1.md)
- [fundamental_defensive_overlay_rolling_validation_v1_config_results.csv](D:/hh/codex/v4/phase_1_fundamental/fundamental_defensive_overlay_rolling_validation_v1_config_results.csv)
- [fundamental_defensive_overlay_rolling_validation_v1_chosen.csv](D:/hh/codex/v4/phase_1_fundamental/fundamental_defensive_overlay_rolling_validation_v1_chosen.csv)

Protocol:

- annual `5Y train + 2Y test + 1Y review`
- freeze the pure-fundamental annual factor set first
- then search only the overlay layer

Main local findings:

- the most stable trigger family was `bank_core_3`
- the most informative warning threshold was `40%`
- `55%` versus `60%` severe threshold had little practical separation
- `warning=60%` equity was more useful than `warning=80%`
- `severe=20%` versus `40%` looked secondary locally
- with full defensive sleeve data added, review diagnostics ranked:
  `511260.XSHG > 511010.XSHG > cash`

Interpretation:

- local rolling suggested the useful part of the overlay is mainly the warning layer
- severe-state tuning did not look like the main source of edge

## JoinQuant Data Support

Downloaded defensive ETF panels from JoinQuant:

- [bond_defensive_panel_full_v1.csv](D:/hh/codex/v4/phase_2_momentum/bond_defensive_panel_full_v1.csv)
- [short_bond_defensive_panel_v1.csv](D:/hh/codex/v4/phase_2_momentum/short_bond_defensive_panel_v1.csv)

Downloader used:

- [download_joinquant_bond_defensive_panel_v1.py](D:/hh/codex/v4/phase_2_momentum/download_joinquant_bond_defensive_panel_v1.py)

## JoinQuant Candidate Files

Candidate strategy files created:

- [joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_v1_standalone.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_v1_standalone.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_cash_6020_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_cash_6020_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_cash_4060_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_cash_4060_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_shortbond_6040_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_candidate_shortbond_6040_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_unified_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_unified_v1.py)

## JoinQuant Backtest Results

Baseline:

- total return: `44.48%`
- annualized return: `7.89%`
- max drawdown: `22.43%`
- sharpe: `0.199`
- sortino: `0.324`
- volatility: `0.196`

`cash_6040_4055`:

- total return: `43.87%`
- annualized return: `7.80%`
- max drawdown: `21.64%`
- sharpe: `0.224`
- sortino: `0.366`
- volatility: `0.170`

Interpretation:

- better risk-adjusted profile than baseline
- but slightly lower return

`cash_6020_4055`:

- identical to `cash_6040_4055`

`cash_6040_4060`:

- identical to `cash_6040_4055`

Interpretation:

- severe branch did not materially affect realized backtest behavior
- current improvement came mainly from the warning layer

`shortbond_6040_4055`:

- total return: `46.09%`
- annualized return: `8.14%`
- max drawdown: `21.73%`
- sharpe: `0.245`
- sortino: `0.399`
- volatility: `0.169`

Interpretation:

- improved return over baseline
- improved sharpe, sortino, and volatility over baseline
- drawdown remained better than baseline and only slightly above `cash_6040_4055`
- this is the strongest candidate found in the current round

## Current Recommended Candidate

Current best candidate:

- trigger metrics: `bank_core_3`
- warning threshold: `40%`
- severe threshold: `55%`
- warning equity weight: `60%`
- severe equity weight: `40%`
- defensive asset: `511260.XSHG`

In the unified file, the default preset is now:

- `shortbond_6040_4055`

## Practical Conclusion

At this stage, the most defensible simplified conclusion is:

- keep the original pure-fundamental strategy as the baseline
- the overlay appears useful mainly through the warning-state risk reduction
- `shortbond` works better than `cash` in realized JoinQuant testing
- severe-state micro-tuning is not yet a priority

## Backup Targets

Recommended backup set:

- this summary file
- unified overlay strategy file
- rolling validation script
- rolling validation outputs
- JoinQuant short-bond candidate file
- downloaded short-bond and treasury defensive panels
