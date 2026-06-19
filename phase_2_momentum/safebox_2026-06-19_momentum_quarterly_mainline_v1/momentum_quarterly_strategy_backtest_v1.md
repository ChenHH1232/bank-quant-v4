# Momentum Quarterly Strategy Backtest V1

Definition:
- alpha source = rolling-selected `alpha_only` scenario from `momentum_quarterly_rolling_validation_v1_results.csv`
- current formal line should therefore behave as a quarterly `mom_12_1` strategy
- stock pool keeps the prior-20-trading-day liquidity and market-cap double-top-80% rule
- portfolio bucket = top quintile at each quarterly review date, equal-weight interpretation

- scored review rebalances: `7`
- candidate quarterly review dates in plan: `7`
- top cumulative return: `0.103692271`
- bottom cumulative return: `-0.1150534001`
- long-short cumulative return: `0.2325325639`
- mean top turnover: `0.411111`

Per-quarter detail:
- `2021-09-01` | alpha=`mom_12_1` | top_return=`0.0405994689` | bottom_return=`-0.0178352849` | long_short=`0.0584347538` | turnover=``
- `2021-11-01` | alpha=`mom_12_1` | top_return=`0.0601889655` | bottom_return=`-0.0262287305` | long_short=`0.086417696` | turnover=`0.4`
- `2022-05-05` | alpha=`mom_12_1` | top_return=`-0.0589496612` | bottom_return=`-0.0611061132` | long_short=`0.002156452` | turnover=`0.4`
- `2022-09-01` | alpha=`mom_12_1` | top_return=`-0.0506170978` | bottom_return=`-0.0873358483` | long_short=`0.0367187505` | turnover=`0.333333`
- `2022-11-01` | alpha=`mom_12_1` | top_return=`0.1340438211` | bottom_return=`0.153257618` | long_short=`-0.0192137969` | turnover=`0.333333`
- `2023-05-04` | alpha=`mom_12_1` | top_return=`-0.0354981101` | bottom_return=`-0.0210470261` | long_short=`-0.014451084` | turnover=`0.666667`
- `2023-09-01` | alpha=`mom_12_1` | top_return=`0.0237500607` | bottom_return=`-0.0435547502` | long_short=`0.0673048109` | turnover=`0.333333`

Output:
- [momentum_quarterly_strategy_backtest_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\momentum_quarterly_strategy_backtest_v1_detail.csv)
