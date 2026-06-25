# Monthly Relative Momentum Validation Summary 2026-06-23

## Scope

This note closes three follow-up experiments around pure-fundamental monthly style timing:

1. monthly relative momentum used to switch between two pure-fundamental branches
2. monthly relative momentum used to tilt profitability versus quality inside `base_core_6`
3. a more execution-like discrete tilt rule validated in rolling, then checked in full JoinQuant backtest

The purpose was to test whether monthly information can improve the pure-fundamental shell without turning the research into annual hindsight switching.

## Baseline Context

- current pure-fundamental base shell remains the `base_core_6` family
- branch A = balanced `base_core_6 + top_08`
- branch B = `base_core_6 - indicator__eps + bank_indicator__core_level_capital_adequacy_ratio`
- earlier work already showed branch B was a serious candidate, while persistent heavy quality overweight failed in JoinQuant

## 1. Monthly Relative Momentum Branch Switch

Files:

- `build_base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1.py`
- `base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1.md`
- `base_core_6_monthly_relative_momentum_branch_switch_rolling_validation_v1_config_results.csv`

Question tested:

- can monthly relative momentum between branch A and branch B improve over annual one-shot switching

Rolling result:

- `branch_b_always` ranked first on mean review return: `0.078288`
- best monthly switch rule `branch_b_if_rel_3m_gt_2pct` only reached `0.068630`
- `branch_a_always` baseline was `0.065544`

Interpretation:

- monthly switching added a little information, but not enough
- the main message from rolling was still that branch B itself was stronger
- this means the problem was not “how to switch between A and B better”
- the real message was “branch B may simply be the better standing candidate”

Decision:

- do not promote monthly branch switching into execution
- keep branch B as the stronger structural candidate, but do not add a monthly switch layer on top

## 2. Monthly Relative Momentum Continuous Tilt

Files:

- `build_base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1.py`
- `base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1.md`
- `base_core_6_monthly_relative_momentum_tilt_rolling_validation_v1_config_results.csv`

Question tested:

- instead of treating profitability and quality as opposites, can monthly relative momentum adjust the tilt between the two sleeves inside the same pure-fundamental shell

Rolling result:

- `equal_50_50` baseline mean review return: `0.023186`
- best rule `profit_70_if_rel_3m_gt_0_else_quality_70`: `0.025972`
- second best `profit_70_if_rel_3m_gt_2pct_else_quality_60`: `0.025163`

Interpretation:

- this direction was conceptually better than binary branch switching
- it matches the idea that quality is not the opposite of profitability, but a slower and more stability-oriented information layer
- however the observed gain was small
- average relative momentum itself was weak, so the signal did not look powerful enough to justify confidence

Decision:

- keep as a research-positive idea
- do not promote directly from this rolling alone
- any next step must use more execution-like validation before trusting the gain

## 3. Monthly Relative Momentum Discrete Tilt Plus JoinQuant Check

Files:

- `build_base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2.py`
- `base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2.md`
- `base_core_6_monthly_relative_momentum_tilt_discrete_rolling_validation_v2_config_results.csv`
- `joinquant_v4_annual_backtest_strategy_base_core_6_monthly_relative_momentum_tilt_discrete_v1.py`

Question tested:

- if continuous tilt is too soft and too approximate, can discrete rebalance-time buckets do better
- tested buckets around `50/50`, `40/60`, `30/70`, and a symmetric ladder

Rolling result:

- `equal_50_50` baseline mean review return: `0.023186`
- `quality_60_if_rel_3m_le_0_else_50`: `0.024334`
- `quality_70_if_rel_3m_le_0_else_50`: `0.025488`
- `quality_ladder_50_40_30_by_rel_3m`: `0.025178`
- `symmetric_ladder_70_50_30_by_rel_3m`: `0.025891`

Rolling interpretation:

- discrete buckets were cleaner than the earlier continuous tilt framing
- weak profitability-relative momentum did seem to argue for more quality
- among quality-side rules, `30/70` looked better than `40/60`
- however the gain was still modest

JoinQuant executable confirmation:

- implemented candidate: `quality_70_if_rel_3m_le_0_else_50`
- full-period JoinQuant result:
- strategy return `15.61%`
- annualized return `3.04%`
- excess return `-3.54%`
- sharpe `-0.051`
- max drawdown `25.97%`

JoinQuant interpretation:

- the rule failed clearly in executable backtest
- rolling did not survive execution
- this strongly suggests the rolling approximation here was too optimistic
- the likely source is that rolling combined sleeve returns linearly, while real execution changes ranking order, bucket membership, and holdings after the dynamic weight change
- the monthly signal itself also appeared weak and noisy

Decision:

- archive monthly discrete tilt as rolling-positive but JoinQuant-rejected
- do not move this path into the main pure-fundamental strategy

## Final Conclusions

- monthly relative momentum branch switching is not useful enough
- monthly profitability-quality tilt is conceptually better than binary switching
- but neither the continuous tilt nor the discrete tilt survived strong executable confirmation
- therefore monthly style timing should not be added to the current main line
- current evidence still favors keeping the pure-fundamental main path structurally simple

## Practical Takeaway

- use these results as a warning against building style-timing layers from weak relative signals
- if style timing is revisited later, it should start from more execution-faithful simulation rather than sleeve-return mixing
- until then, monthly relative momentum for pure-fundamental quality/profitability timing stays archived, not promoted
