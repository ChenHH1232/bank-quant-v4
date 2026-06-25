# Phase 2 Rolling OOS Comparison V1

Objective:
- place the current phase-2 candidate lines into one rolling out-of-sample comparison frame
- make the current comparable evidence explicit before final report writing

Included lines:
- `fundamental_only`
- `momentum_only`
- `blend_60_40`
- `annual_entry_monthly_exit_slow_fundamental`

Important comparability note:
- all lines below are drawn from the same pre-2021 rolling family
- but `momentum_only` currently collapses to the same realized result as `fundamental_only` in the common-sample capped framework
- and the state-machine branch is evaluated on a denser monthly sequence than the sparse common snapshots used by the basic dual-engine table
- so the current table is best read as a project-level checkpoint, not as the final clean independent-engine horse race

Strategy summary:
- `annual_entry_monthly_exit_slow_fundamental` | source=`state_machine_common_sample` | snapshots=`26` | mean_return=`0.000275` | cum_return=`0.007116` | mean_cash=`0.252262` | mean_invested=`0.747738`
- `blend_60_40` | source=`dual_engine_common_sample` | snapshots=`8` | mean_return=`0.000540` | cum_return=`0.004325` | mean_cash=`0.081127` | mean_invested=`0.918873`
- `fundamental_only` | source=`dual_engine_common_sample` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_cash=`0.318750` | mean_invested=`0.681250`
- `momentum_only` | source=`dual_engine_common_sample` | snapshots=`8` | mean_return=`0.000346` | cum_return=`0.002768` | mean_cash=`0.318750` | mean_invested=`0.681250`

Fold summary:
- `fold_01`
- `fold_01` `fundamental_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000`
- `fold_01` `momentum_only` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.000960` | mean_cash=`0.350000`
- `fold_01` `blend_60_40` | validation=`2018-11-01` to `2019-11-01` | dates=`4` | cum_return=`0.001528` | mean_cash=`0.090862`
- `fold_01` `annual_entry_monthly_exit_slow_fundamental` | validation=`2018-11-01` to `2019-11-01` | dates=`13` | cum_return=`0.005665` | mean_cash=`0.242985`
- `fold_02`
- `fold_02` `fundamental_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500`
- `fold_02` `momentum_only` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.001806` | mean_cash=`0.287500`
- `fold_02` `blend_60_40` | validation=`2019-09-02` to `2020-09-01` | dates=`4` | cum_return=`0.002792` | mean_cash=`0.071392`
- `fold_02` `annual_entry_monthly_exit_slow_fundamental` | validation=`2019-09-02` to `2020-09-01` | dates=`13` | cum_return=`0.001442` | mean_cash=`0.261538`

Current project-level reading:
- `blend_60_40` remains the strongest practical rolling baseline among the currently comparable lines
- `annual_entry_monthly_exit_slow_fundamental` remains the strongest current state-machine challenger
- the state-machine branch still improves over its weaker internal variants, but it should be compared to `blend_60_40` only with the snapshot-density caveat kept explicit
- the current pure-engine common-sample comparison is still structurally limited by cap-induced selection collapse

What this means for the next step:
- this unified frame is already sufficient for report-level sequencing and candidate hierarchy
- but a final independent `pure momentum vs pure fundamental` statement should not rely only on this capped common-sample table
- that separation still needs the broader momentum branch evidence already archived elsewhere

Output:
- [phase2_rolling_oos_comparison_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\phase2_rolling_oos_comparison_v1_detail.csv)
