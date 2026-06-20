# Mean Reversion Execution Comparison V1

Purpose:
- compare `daily execution` and `weekly execution` for the frozen standalone mean-reversion V1 spec
- keep the signal fixed as `rev5_abnvol`
- keep equal-weight holding count fixed at `5`
- keep liquidity and market-cap gate as cross-sectional bottom-20% exclusion on each trade date

Window:
- evaluation: `2019-01-01` to `2020-12-31`
- this keeps the execution-rhythm comparison inside the pre-2021 research reserve

Results:
- `weekly` | total_return=`0.140259` | annualized_proxy=`0.068263` | max_drawdown_proxy=`-0.217548` | return_2019=`0.246256` | return_2020=`-0.085052` | avg_turnover=`0.703922` | traded_periods=`102`
- `daily` | total_return=`0.047563` | annualized_proxy=`0.023554` | max_drawdown_proxy=`-0.292171` | return_2019=`0.150717` | return_2020=`-0.089643` | avg_turnover=`0.53786` | traded_periods=`486`

Current read:
- the stronger first-pass execution rhythm is `weekly` on this fixed signal spec
- this result should be treated as execution evidence, not as permission to retune the signal on later out-of-sample windows

Outputs:
- [mean_reversion_execution_comparison_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_execution_comparison_v1.csv)
- [mean_reversion_execution_comparison_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_execution_comparison_v1_detail.csv)
