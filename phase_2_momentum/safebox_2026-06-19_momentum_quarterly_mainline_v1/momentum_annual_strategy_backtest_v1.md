# Momentum Annual Strategy Backtest V1

Definition:
- alpha source = rolling-selected `alpha_only` scenario from `momentum_rolling_validation_v1_results.csv`
- expected current formal line = `mom_12_1` as the sole ranking alpha
- stock pool keeps the prior-20-trading-day liquidity and market-cap double-top-80% rule
- portfolio bucket = top quintile at each annual review date, equal-weight interpretation

- review rebalance rows: `4`
- candidate review folds in rolling plan: `5`
- top cumulative return: `0.4324144478`
- bottom cumulative return: `0.1124349343`
- long-short cumulative return: `0.3148626479`
- mean top turnover: `0.822222`

Per-year detail:
- `2021-05-06` | alpha=`mom_12_1` | top_return=`-0.0616676123` | bottom_return=`0.0013785563` | long_short=`-0.0630461686` | turnover=``
- `2022-05-05` | alpha=`mom_12_1` | top_return=`0.0077407012` | bottom_return=`-0.0241929927` | long_short=`0.0319336939` | turnover=`0.8`
- `2023-05-04` | alpha=`mom_12_1` | top_return=`0.1203360241` | bottom_return=`0.0035542095` | long_short=`0.1167818146` | turnover=`0.833333`
- `2024-05-06` | alpha=`mom_12_1` | top_return=`0.3521189072` | bottom_return=`0.1344139599` | long_short=`0.2177049473` | turnover=`0.833333`

Unscored review folds:
- `mom_fold_05` | review_start=`2025-05-06` | reason=`missing next annual return label in current panel`

Output:
- [momentum_annual_strategy_backtest_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\momentum_annual_strategy_backtest_v1_detail.csv)
