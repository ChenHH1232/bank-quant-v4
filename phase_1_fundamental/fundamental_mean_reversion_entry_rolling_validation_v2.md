# Fundamental Mean Reversion Entry Rolling Validation V2

Objective:
- extend V1 into a narrow grid over trigger threshold and trigger signal
- keep the fundamental stock-selection line unchanged
- compare whether the trigger should be stricter or looser, and whether `rev5_abnvol` is better than raw `rev_5d`

Frozen setup:
- scenario: `base_plus_top2_9`
- combo: `combo__ic_weight_train`
- hold bucket: `5` of `5`
- search window: `20` trading days after each rebalance date
- threshold grid: `20%, 30%, 40%`
- signal grid: `rev5_abnvol, rev_5d`

Current summary focus:
- compare `split_50_50_reversion` against `baseline_full_entry` and `split_50_50_time` inside each `(signal, threshold)` cell

Summary rows:
- `rev5_abnvol` q=`20%` `review` `baseline_full_entry` | periods=`12` | cum_return=`0.240004` | mean_return=`0.023731` | max_drawdown=`-0.300312` | positive_ratio=`0.583333`
- `rev5_abnvol` q=`30%` `review` `baseline_full_entry` | periods=`12` | cum_return=`0.240004` | mean_return=`0.023731` | max_drawdown=`-0.300312` | positive_ratio=`0.583333`
- `rev5_abnvol` q=`40%` `review` `baseline_full_entry` | periods=`12` | cum_return=`0.240004` | mean_return=`0.023731` | max_drawdown=`-0.300312` | positive_ratio=`0.583333`
- `rev_5d` q=`20%` `review` `baseline_full_entry` | periods=`12` | cum_return=`0.240004` | mean_return=`0.023731` | max_drawdown=`-0.300312` | positive_ratio=`0.583333`
- `rev_5d` q=`30%` `review` `baseline_full_entry` | periods=`12` | cum_return=`0.240004` | mean_return=`0.023731` | max_drawdown=`-0.300312` | positive_ratio=`0.583333`
- `rev_5d` q=`40%` `review` `baseline_full_entry` | periods=`12` | cum_return=`0.240004` | mean_return=`0.023731` | max_drawdown=`-0.300312` | positive_ratio=`0.583333`
- `rev_5d` q=`30%` `review` `split_50_50_reversion` | periods=`12` | cum_return=`0.293986` | mean_return=`0.026813` | max_drawdown=`-0.26158` | positive_ratio=`0.583333`
- `rev_5d` q=`40%` `review` `split_50_50_reversion` | periods=`12` | cum_return=`0.290264` | mean_return=`0.026609` | max_drawdown=`-0.264941` | positive_ratio=`0.583333`
- `rev5_abnvol` q=`40%` `review` `split_50_50_reversion` | periods=`12` | cum_return=`0.248417` | mean_return=`0.024176` | max_drawdown=`-0.287398` | positive_ratio=`0.583333`
- `rev_5d` q=`20%` `review` `split_50_50_reversion` | periods=`12` | cum_return=`0.240283` | mean_return=`0.022439` | max_drawdown=`-0.260463` | positive_ratio=`0.5`
- `rev5_abnvol` q=`30%` `review` `split_50_50_reversion` | periods=`12` | cum_return=`0.237895` | mean_return=`0.023598` | max_drawdown=`-0.292506` | positive_ratio=`0.583333`
- `rev5_abnvol` q=`20%` `review` `split_50_50_reversion` | periods=`12` | cum_return=`0.231485` | mean_return=`0.022665` | max_drawdown=`-0.273875` | positive_ratio=`0.583333`
- `rev5_abnvol` q=`20%` `review` `split_50_50_time` | periods=`12` | cum_return=`0.172874` | mean_return=`0.017444` | max_drawdown=`-0.261291` | positive_ratio=`0.5`
- `rev5_abnvol` q=`30%` `review` `split_50_50_time` | periods=`12` | cum_return=`0.172874` | mean_return=`0.017444` | max_drawdown=`-0.261291` | positive_ratio=`0.5`
- `rev5_abnvol` q=`40%` `review` `split_50_50_time` | periods=`12` | cum_return=`0.172874` | mean_return=`0.017444` | max_drawdown=`-0.261291` | positive_ratio=`0.5`
- `rev_5d` q=`20%` `review` `split_50_50_time` | periods=`12` | cum_return=`0.172874` | mean_return=`0.017444` | max_drawdown=`-0.261291` | positive_ratio=`0.5`
- `rev_5d` q=`30%` `review` `split_50_50_time` | periods=`12` | cum_return=`0.172874` | mean_return=`0.017444` | max_drawdown=`-0.261291` | positive_ratio=`0.5`
- `rev_5d` q=`40%` `review` `split_50_50_time` | periods=`12` | cum_return=`0.172874` | mean_return=`0.017444` | max_drawdown=`-0.261291` | positive_ratio=`0.5`

Outputs:
- [fundamental_mean_reversion_entry_rolling_validation_v2_detail.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_mean_reversion_entry_rolling_validation_v2_detail.csv)
- [fundamental_mean_reversion_entry_rolling_validation_v2_summary.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_mean_reversion_entry_rolling_validation_v2_summary.csv)
