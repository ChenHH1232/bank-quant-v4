# Fundamental Mean Reversion Entry Rolling Validation V1

Objective:
- keep the current primary fundamental stock-selection line unchanged
- test whether mean reversion should only change post-rebalance entry speed
- keep the evaluation causal by using a train-window signal threshold

Frozen setup:
- scenario: `base_plus_top2_9`
- combo: `combo__ic_weight_train`
- hold bucket: `5` of `5`
- reversion signal: pool-average `rev5_abnvol`
- trigger threshold: train-window `30`th percentile
- search window: `20` trading days after each rebalance date

Compared entry styles:
- `baseline_full_entry`: buy the full basket on the first tradable day
- `split_50_50_time`: buy `50%` immediately and force the other `50%` at day 20
- `split_50_50_reversion`: buy `50%` immediately and trigger the other `50%` when the signal crosses the train threshold, otherwise force at day 20

Summary:
- `test` `baseline_full_entry` | periods=`25` | cum_return=`1.50052` | mean_return=`0.041889` | max_drawdown=`-0.191616` | positive_ratio=`0.56` | mean_delay_days=`0.0` | mean_cash_days=`0.0`
- `test` `split_50_50_time` | periods=`25` | cum_return=`1.16761` | mean_return=`0.03505` | max_drawdown=`-0.174506` | positive_ratio=`0.52` | mean_delay_days=`27.32` | mean_cash_days=`13.66`
- `test` `split_50_50_reversion` | periods=`25` | cum_return=`1.51369` | mean_return=`0.041977` | max_drawdown=`-0.177399` | positive_ratio=`0.56` | mean_delay_days=`7.16` | mean_cash_days=`3.58`
- `review` `baseline_full_entry` | periods=`12` | cum_return=`0.240004` | mean_return=`0.023731` | max_drawdown=`-0.300312` | positive_ratio=`0.583333` | mean_delay_days=`0.0` | mean_cash_days=`0.0`
- `review` `split_50_50_time` | periods=`12` | cum_return=`0.172874` | mean_return=`0.017444` | max_drawdown=`-0.261291` | positive_ratio=`0.5` | mean_delay_days=`27.583333` | mean_cash_days=`13.791667`
- `review` `split_50_50_reversion` | periods=`12` | cum_return=`0.237895` | mean_return=`0.023598` | max_drawdown=`-0.292506` | positive_ratio=`0.583333` | mean_delay_days=`6.083333` | mean_cash_days=`3.041667`
- `all` `baseline_full_entry` | periods=`37` | cum_return=`2.100656` | mean_return=`0.036` | max_drawdown=`-0.216898` | positive_ratio=`0.567568` | mean_delay_days=`0.0` | mean_cash_days=`0.0`
- `all` `split_50_50_time` | periods=`37` | cum_return=`1.542332` | mean_return=`0.02934` | max_drawdown=`-0.192249` | positive_ratio=`0.513514` | mean_delay_days=`27.405405` | mean_cash_days=`13.702703`
- `all` `split_50_50_reversion` | periods=`37` | cum_return=`2.111685` | mean_return=`0.036016` | max_drawdown=`-0.221136` | positive_ratio=`0.567568` | mean_delay_days=`6.810811` | mean_cash_days=`3.405405`

Outputs:
- [fundamental_mean_reversion_entry_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_mean_reversion_entry_rolling_validation_v1_detail.csv)
- [fundamental_mean_reversion_entry_rolling_validation_v1_summary.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_mean_reversion_entry_rolling_validation_v1_summary.csv)
