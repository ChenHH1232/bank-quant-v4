# Momentum Mean Reversion Entry Overlay Rolling Validation V1

Objective:
- keep the momentum main line fixed as `direct_mom12_top6`
- test whether mean reversion works better as entry timing than as a separate stock-selection layer
- use only train-window information to freeze trigger thresholds inside each fold

Frozen setup:
- base strategy: `direct_mom12_top6`
- folds: `38` monthly rolling folds from the momentum main-line framework
- hold count: `6`
- search window: `20` trading days after each rebalance date
- signal grid: `rev5_abnvol, rev_5d`
- threshold grid: `20%, 30%, 40%`
- strategy comparison = `baseline_full_entry` vs `split_50_50_time` vs `split_50_50_reversion`

- evaluated snapshots: `5658` raw strategy rows

Review summary:
- `rev5_abnvol` q=`20%` `baseline_full_entry` | periods=`312` | cum_return=`11.446582` | mean_return=`0.008656` | max_drawdown=`-0.355276` | positive_ratio=`0.647436` | mean_delay_days=`0.0`
- `rev5_abnvol` q=`30%` `baseline_full_entry` | periods=`312` | cum_return=`11.446582` | mean_return=`0.008656` | max_drawdown=`-0.355276` | positive_ratio=`0.647436` | mean_delay_days=`0.0`
- `rev5_abnvol` q=`40%` `baseline_full_entry` | periods=`312` | cum_return=`11.446582` | mean_return=`0.008656` | max_drawdown=`-0.355276` | positive_ratio=`0.647436` | mean_delay_days=`0.0`
- `rev_5d` q=`20%` `baseline_full_entry` | periods=`312` | cum_return=`11.446582` | mean_return=`0.008656` | max_drawdown=`-0.355276` | positive_ratio=`0.647436` | mean_delay_days=`0.0`
- `rev_5d` q=`30%` `baseline_full_entry` | periods=`312` | cum_return=`11.446582` | mean_return=`0.008656` | max_drawdown=`-0.355276` | positive_ratio=`0.647436` | mean_delay_days=`0.0`
- `rev_5d` q=`40%` `baseline_full_entry` | periods=`312` | cum_return=`11.446582` | mean_return=`0.008656` | max_drawdown=`-0.355276` | positive_ratio=`0.647436` | mean_delay_days=`0.0`
- `rev_5d` q=`40%` `split_50_50_reversion` | periods=`312` | cum_return=`15.756136` | mean_return=`0.009608` | max_drawdown=`-0.363623` | positive_ratio=`0.673077` | mean_delay_days=`3.666667`
- `rev_5d` q=`30%` `split_50_50_reversion` | periods=`312` | cum_return=`10.827819` | mean_return=`0.008452` | max_drawdown=`-0.372433` | positive_ratio=`0.673077` | mean_delay_days=`5.740385`
- `rev5_abnvol` q=`40%` `split_50_50_reversion` | periods=`312` | cum_return=`9.477839` | mean_return=`0.008076` | max_drawdown=`-0.380178` | positive_ratio=`0.647436` | mean_delay_days=`3.778846`
- `rev5_abnvol` q=`30%` `split_50_50_reversion` | periods=`312` | cum_return=`8.856819` | mean_return=`0.007886` | max_drawdown=`-0.449535` | positive_ratio=`0.673077` | mean_delay_days=`5.330128`
- `rev5_abnvol` q=`20%` `split_50_50_reversion` | periods=`312` | cum_return=`5.359165` | mean_return=`0.006419` | max_drawdown=`-0.434568` | positive_ratio=`0.637821` | mean_delay_days=`7.682692`
- `rev_5d` q=`20%` `split_50_50_reversion` | periods=`312` | cum_return=`4.632186` | mean_return=`0.00601` | max_drawdown=`-0.412779` | positive_ratio=`0.673077` | mean_delay_days=`11.205128`
- `rev5_abnvol` q=`20%` `split_50_50_time` | periods=`312` | cum_return=`1.349181` | mean_return=`0.002955` | max_drawdown=`-0.281794` | positive_ratio=`0.682692` | mean_delay_days=`26.740385`
- `rev5_abnvol` q=`30%` `split_50_50_time` | periods=`312` | cum_return=`1.349181` | mean_return=`0.002955` | max_drawdown=`-0.281794` | positive_ratio=`0.682692` | mean_delay_days=`26.740385`
- `rev5_abnvol` q=`40%` `split_50_50_time` | periods=`312` | cum_return=`1.349181` | mean_return=`0.002955` | max_drawdown=`-0.281794` | positive_ratio=`0.682692` | mean_delay_days=`26.740385`
- `rev_5d` q=`20%` `split_50_50_time` | periods=`312` | cum_return=`1.349181` | mean_return=`0.002955` | max_drawdown=`-0.281794` | positive_ratio=`0.682692` | mean_delay_days=`26.740385`
- `rev_5d` q=`30%` `split_50_50_time` | periods=`312` | cum_return=`1.349181` | mean_return=`0.002955` | max_drawdown=`-0.281794` | positive_ratio=`0.682692` | mean_delay_days=`26.740385`
- `rev_5d` q=`40%` `split_50_50_time` | periods=`312` | cum_return=`1.349181` | mean_return=`0.002955` | max_drawdown=`-0.281794` | positive_ratio=`0.682692` | mean_delay_days=`26.740385`

Outputs:
- [momentum_mean_reversion_entry_overlay_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\momentum_mean_reversion_entry_overlay_rolling_validation_v1_detail.csv)
- [momentum_mean_reversion_entry_overlay_rolling_validation_v1_summary.csv](D:\hh\codex\v4\phase_2_momentum\momentum_mean_reversion_entry_overlay_rolling_validation_v1_summary.csv)
