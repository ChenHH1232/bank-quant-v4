# Momentum Mean Reversion Entry Overlay Archive Conclusion 2026-06-22

Status:
- archive this branch
- do not promote into the executable momentum main line
- keep the research files for reference only

What was tested:
- base strategy fixed as `direct_mom12_top6`
- mean reversion used only as an entry execution overlay
- local rolling compared:
- `baseline_full_entry`
- `split_50_50_time`
- `split_50_50_reversion`
- signal focus after local screening:
- `rev_5d + q30`
- `rev_5d + q40`

Local rolling takeaway:
- local pre-execution rolling suggested `rev_5d + q40` was the strongest overlay candidate
- `rev_5d + q30` was secondary
- this looked like a possible execution improvement branch, but only as a narrow candidate pending JoinQuant confirmation

JoinQuant confirmation:
- default `baseline_full_entry`
- strategy return=`33.84%`
- annualized=`6.20%`
- max_drawdown=`23.75%`
- `split_50_50_reversion + rev_5d + q30`
- strategy return=`17.84%`
- annualized=`3.45%`
- excess return=`-1.69%`
- max_drawdown=`23.16%`
- `split_50_50_reversion + rev_5d + q40`
- strategy return=`23.07%`
- annualized=`4.38%`
- excess return=`2.68%`
- max_drawdown=`24.51%`

Final conclusion:
- the local rolling improvement did not transfer into JoinQuant executable results
- `q30` failed clearly and should be treated as invalid
- `q40` was better than `q30`, but still materially weaker than the baseline and did not reduce drawdown
- this means the current `50/50 delayed fill` mean reversion overlay is not robust enough for the momentum main line

Decision:
- archive `joinquant_v4_monthly_momentum_strategy_mean_reversion_entry_overlay_v1.py`
- archive `build_momentum_mean_reversion_entry_overlay_rolling_validation_v1.py`
- keep the monthly momentum main line unchanged
- do not spend more time tuning this exact overlay form

Next step preference:
- return focus to `fundamental main line + mean reversion entry optimization`
- if momentum is revisited later, test a lighter execution filter rather than this delayed-fill overlay
