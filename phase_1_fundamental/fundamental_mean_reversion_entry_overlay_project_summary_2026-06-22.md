# Fundamental Mean Reversion Entry Overlay Project Summary

Date: `2026-06-22`

## Objective

Starting from the original pure-fundamental annual bank strategy, validate whether short-horizon mean-reversion signals should be used only as a post-rebalance entry overlay.

Research order:

1. keep the fundamental stock-selection line fixed
2. run local rolling validation with only then-available data
3. freeze a small candidate set
4. move those candidates into JoinQuant for executable confirmation

## Scope

The stock-selection backbone stayed unchanged:

- annual fundamental plan library
- `primary` line
- top bucket holdings from the existing annual factor process

Only the entry execution layer was varied:

- `baseline_full_entry`
- `split_50_50_time`
- `split_50_50_reversion`

Signals tested locally:

- `rev5_abnvol`
- `rev_5d`

Threshold grid tested locally:

- `20%`
- `30%`
- `40%`

## Local Rolling V1

Script:

- [build_fundamental_mean_reversion_entry_rolling_validation_v1.py](D:/hh/codex/v4/phase_1_fundamental/build_fundamental_mean_reversion_entry_rolling_validation_v1.py)

Outputs:

- [fundamental_mean_reversion_entry_rolling_validation_v1.md](D:/hh/codex/v4/phase_1_fundamental/fundamental_mean_reversion_entry_rolling_validation_v1.md)
- [fundamental_mean_reversion_entry_rolling_validation_v1_detail.csv](D:/hh/codex/v4/phase_1_fundamental/fundamental_mean_reversion_entry_rolling_validation_v1_detail.csv)
- [fundamental_mean_reversion_entry_rolling_validation_v1_summary.csv](D:/hh/codex/v4/phase_1_fundamental/fundamental_mean_reversion_entry_rolling_validation_v1_summary.csv)

Frozen V1 setup:

- signal = pool-average `rev5_abnvol`
- threshold = train-window `30%` quantile
- search window = `20` trading days
- initial entry = `50%`
- remaining entry = triggered or forced by day `20`

V1 conclusions:

- `split_50_50_time` was clearly weaker than direct full entry
- `split_50_50_reversion` was slightly better than baseline in `test`
- `split_50_50_reversion` was roughly flat versus baseline in `review`

Interpretation:

- simple time-splitting was not useful
- the only promising path was trigger-based splitting

## Local Rolling V2 Grid

Script:

- [build_fundamental_mean_reversion_entry_rolling_validation_v2.py](D:/hh/codex/v4/phase_1_fundamental/build_fundamental_mean_reversion_entry_rolling_validation_v2.py)

Outputs:

- [fundamental_mean_reversion_entry_rolling_validation_v2.md](D:/hh/codex/v4/phase_1_fundamental/fundamental_mean_reversion_entry_rolling_validation_v2.md)
- [fundamental_mean_reversion_entry_rolling_validation_v2_detail.csv](D:/hh/codex/v4/phase_1_fundamental/fundamental_mean_reversion_entry_rolling_validation_v2_detail.csv)
- [fundamental_mean_reversion_entry_rolling_validation_v2_summary.csv](D:/hh/codex/v4/phase_1_fundamental/fundamental_mean_reversion_entry_rolling_validation_v2_summary.csv)

Main local ranking on the `review` window for `split_50_50_reversion`:

1. `rev_5d + q30`
2. `rev_5d + q40`
3. `rev5_abnvol + q40`

Local interpretation:

- raw `rev_5d` looked better than `rev5_abnvol` inside the rolling proxy
- a medium trigger (`30%`) looked strongest locally
- a looser trigger (`40%`) was second-best

## JoinQuant Executable File

Executable candidate file:

- [joinquant_v4_annual_backtest_strategy_mean_reversion_entry_overlay_v1.py](D:/hh/codex/v4/phase_1_fundamental/joinquant_v4_annual_backtest_strategy_mean_reversion_entry_overlay_v1.py)

This file keeps the original fundamental stock-selection logic and adds a switchable entry overlay layer in `initialize`:

- `g.entry_overlay_mode`
- `g.entry_signal_name`
- `g.entry_threshold_label`

Supported modes:

- `baseline_full_entry`
- `split_50_50_time`
- `split_50_50_reversion`

Supported signal choices:

- `rev_5d`
- `rev5_abnvol`

Supported threshold labels:

- `q20`
- `q30`
- `q40`

The per-plan trigger values for `annual_01` to `annual_05` were frozen directly from the local rolling V2 outputs.

## JoinQuant Confirmation Results

Pure fundamental reference line from earlier confirmation:

- total return: `43.87%`
- annualized return: `7.80%`
- max drawdown: `21.64%`

`split_50_50_reversion` with `rev_5d + q30`:

- total return: `36.98%`
- annualized return: `6.71%`
- max drawdown: `22.30%`

Interpretation:

- local rolling leader did not survive executable confirmation

`split_50_50_reversion` with `rev_5d + q40`:

- total return: `37.04%`
- annualized return: `6.72%`
- max drawdown: `22.83%`

Interpretation:

- almost identical to `rev_5d + q30`
- still materially weaker than the pure-fundamental line

`split_50_50_reversion` with `rev5_abnvol + q40`:

- total return: `42.78%`
- annualized return: `7.63%`
- max drawdown: `22.63%`

Interpretation:

- clearly stronger than the two `rev_5d` executable variants
- close to the pure-fundamental reference on return
- but still did not beat the pure-fundamental reference on return or drawdown

## Final Decision

Decision hierarchy for this branch:

1. keep the original pure-fundamental line as the main strategy
2. keep `rev5_abnvol + q40` as the only retained entry-overlay candidate
3. archive `rev_5d + q30`
4. archive `rev_5d + q40`

Branch interpretation:

- the local rolling evidence did not transfer cleanly into executable JoinQuant confirmation
- direct time splitting should be treated as rejected
- `rev5_abnvol + q40` passed a basic feasibility check but did not earn promotion over the pure-fundamental main line

## Practical Conclusion

At the current stage, the safest project-level conclusion is:

- pure fundamental remains the active annual deployment line
- mean reversion remains better interpreted as a research-side execution aid than a promoted live overlay
- if this branch is revisited later, the only executable candidate worth reopening first is `rev5_abnvol + q40`

## Backup Targets

Recommended backup set:

- this summary file
- V1 rolling script and outputs
- V2 rolling script and outputs
- JoinQuant executable overlay file
