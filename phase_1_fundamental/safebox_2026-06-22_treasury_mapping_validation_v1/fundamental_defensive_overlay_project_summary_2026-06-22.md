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

## Treasury Branch Follow-Up

We also validated a second branch:

- compare each active annual factor with the same period one year earlier
- measure deterioration inside the filtered candidate pool
- map treasury exposure from deterioration breadth

Rolling research files:

- [build_fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2.py](D:/hh/codex/v4/phase_1_fundamental/build_fundamental_defensive_overlay_yoy_pool_linear_rolling_validation_v2.py)
- [build_fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_fundamental_defensive_overlay_yoy_pool_linear_mapping_validation_v1.py)
- [build_fundamental_defensive_overlay_yoy_pool_linear_persist_rolling_validation_v3.py](D:/hh/codex/v4/phase_1_fundamental/build_fundamental_defensive_overlay_yoy_pool_linear_persist_rolling_validation_v3.py)
- [build_fundamental_defensive_overlay_yoy_pool_linear_persist_exit_on_improve_rolling_validation_v4.py](D:/hh/codex/v4/phase_1_fundamental/build_fundamental_defensive_overlay_yoy_pool_linear_persist_exit_on_improve_rolling_validation_v4.py)

JoinQuant candidate files:

- [joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_treasury_thr40_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_treasury_thr40_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_treasury_thr50_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_treasury_thr50_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_treasury_thr60_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_treasury_thr60_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_persist_treasury_thr60_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_persist_treasury_thr60_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_half_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_half_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_cap40_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_cap40_v1.py)
- [joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_scale70_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_defensive_overlay_yoy_pool_linear_thr50_scale70_v1.py)

Rolling conclusions:

- `v2` linear treasury mapping preferred `thr40` locally, with `thr50` second and `thr60` weakest of the three
- after seeing repeated JoinQuant underperformance from overly defensive treasury sizing, we ran a separate mapping-only rolling comparison with threshold fixed at `50%`
- tested mappings were `half` (`0.5 * ratio`), `scale70` (`0.7 * ratio`), `full` (`1.0 * ratio`), and `cap40` (`min(ratio, 40%)`)
- on mean rolling `train/test/review` cumulative return, `full` ranked first, `cap40` second, `scale70` third, and `half` last
- fold winners were `full` in `4/5` annual folds and `cap40` in `1/5`; neither `half` nor `scale70` won any fold
- this means the softer mappings that looked intuitively safer in full-sample JoinQuant backtests were not supported by the rolling train/test evidence
- when moved into full JoinQuant backtests, `thr40` and `thr50` were too defensive
- `thr60` became the least-bad treasury version, but still lagged the short-bond segmented candidate
- `v3` adding persistence (`+10%` on streak 2, `+20%` on streak 3+, cap `60%`) improved on plain `thr60` in local rolling
- `v4` forcing immediate defensive exit on any improvement weakened the local rolling result versus `v3`

JoinQuant conclusions:

- linear treasury branch underperformed the main short-bond segmented branch
- persistence did not rescue the treasury branch enough to overtake `shortbond_6040_4055`
- immediate-exit-on-improvement looked conceptually clean but weakened the local evidence

Post-freeze softening variants:

- because the plain `thr50` linear treasury mapping still looked too defensive in full JoinQuant backtests, we created two softer `thr50` variants for follow-up validation
- `half_v1`: treasury weight = `0.5 * deteriorated_stock_ratio`
- `cap40_v1`: treasury weight = `min(deteriorated_stock_ratio, 40%)`
- `scale70_v1`: treasury weight = `0.7 * deteriorated_stock_ratio`
- both keep the same `50%` deterioration trigger and filtered candidate-pool breadth signal; they only soften the post-trigger treasury sizing

Observed JoinQuant result so far:

- `half_v1` (`0.5 * deteriorated_stock_ratio`) backtest metrics:
- total return: `35.83%`
- annualized return: `6.53%`
- excess return: `13.32%`
- benchmark return: `19.86%`
- alpha: `0.027`
- beta: `0.954`
- sharpe: `0.142`
- sortino: `0.229`
- information ratio: `0.353`
- max drawdown: `19.56%`
- excess max drawdown: `15.99%`
- volatility: `0.178`
- benchmark volatility: `0.168`
- max drawdown window: `2022/04/15` to `2022/10/31`

Preliminary read:

- versus the original baseline in this summary (`44.48%` total return, `7.89%` annualized, `22.43%` max drawdown), `half_v1` reduced drawdown but gave up a noticeable amount of return
- the drawdown improvement exists, but the return give-up still looks large enough that this variant does not obviously overturn the current `shortbond_6040_4055` lead
- `cap40_v1` (`min(deteriorated_stock_ratio, 40%)`) backtest metrics:
- total return: `31.73%`
- annualized return: `5.85%`
- excess return: `9.90%`
- benchmark return: `19.86%`
- alpha: `0.020`
- beta: `0.865`
- sharpe: `0.113`
- sortino: `0.180`
- information ratio: `0.258`
- max drawdown: `16.57%`
- excess max drawdown: `20.45%`
- volatility: `0.164`
- benchmark volatility: `0.168`
- max drawdown window: `2022/04/15` to `2022/10/31`

Updated comparative read:

- `cap40_v1` is more defensive than `half_v1` in realized behavior: lower beta (`0.865` vs `0.954`), lower volatility (`0.164` vs `0.178`), and smaller max drawdown (`16.57%` vs `19.56%`)
- that extra defense came with another step down in return: total return fell from `35.83%` in `half_v1` to `31.73%` in `cap40_v1`, and annualized return fell from `6.53%` to `5.85%`
- relative to the original baseline (`44.48%` total return, `7.89%` annualized, `22.43%` max drawdown), `cap40_v1` improves drawdown materially but gives up even more return than `half_v1`
- between the two softened `thr50` treasury variants, `half_v1` currently looks like the better trade-off if the goal is to keep some upside while trimming risk
- neither softened treasury variant currently challenges the standing conclusion that the treasury breadth branch is weaker than the live `shortbond_6040_4055` candidate
- `scale70_v1` (`0.7 * deteriorated_stock_ratio`) backtest metrics:
- total return: `32.87%`
- annualized return: `6.04%`
- excess return: `10.85%`
- benchmark return: `19.86%`
- alpha: `0.022`
- beta: `0.907`
- sharpe: `0.120`
- sortino: `0.192`
- information ratio: `0.285`
- max drawdown: `18.33%`
- excess max drawdown: `18.96%`
- volatility: `0.171`
- benchmark volatility: `0.168`
- max drawdown window: `2022/04/15` to `2022/10/31`

Three-way read across the softened `thr50` treasury variants:

- `half_v1` remains the return leader of the three (`35.83%` total return, `6.53%` annualized), but it also carries the largest drawdown (`19.56%`)
- `cap40_v1` remains the most defensive of the three (`16.57%` max drawdown, `0.164` volatility, `0.865` beta), but it is also the weakest on return (`31.73%` total return, `5.85%` annualized)
- `scale70_v1` lands in the middle on both sides: return (`32.87%`) and annualized (`6.04%`) sit above `cap40_v1` but below `half_v1`; drawdown (`18.33%`), volatility (`0.171`), and beta (`0.907`) also sit between the other two
- this means the smoothing intuition was directionally correct, but the midpoint mapping did not produce a new efficient frontier winner
- if we judge this branch internally, `half_v1` still looks like the best upside-preserving softening, while `cap40_v1` is still the clearest low-drawdown choice
- `scale70_v1` is usable as a middle compromise, but based on current results it does not dominate either neighbor enough to become the preferred treasury variant

Branch decision:

- keep the treasury branch as an archived research branch
- do not promote it above the short-bond segmented candidate
- keep `shortbond_6040_4055` as the live main candidate

Treasury branch decision note:

- do not continue optimizing the `thr50` treasury sizing map through more `half / scale70 / cap40 / piecewise` variants
- reason: the fixed-`thr50` rolling mapping validation did not support the softer mappings that looked more comfortable in full-sample JoinQuant backtests
- within rolling `train/test/review`, `full` ranked first on average, `cap40` ranked second, and `scale70` plus `half` ranked behind them
- this gap between rolling evidence and full-sample backtest comfort is a warning sign for overfitting if we keep iterating on `thr50` mapping shape
- if treasury research is resumed later, the priority should be the `thr60` / persistence line rather than additional `thr50` mapping micro-tuning
- unless new evidence appears, treasury should remain a secondary archived branch and not displace `shortbond_6040_4055`

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
- the treasury breadth-mapping branch is research-complete for now but not promoted
- severe-state micro-tuning is not yet a priority

## Backup Targets

Recommended backup set:

- this summary file
- unified overlay strategy file
- rolling validation script
- rolling validation outputs
- JoinQuant short-bond candidate file
- downloaded short-bond and treasury defensive panels
