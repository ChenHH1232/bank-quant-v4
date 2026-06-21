# Slow Fundamental Fast Exit Execution Validation V1

Protocol:
- research scope = pre-2021 only
- annual entry and monthly exit signal stay fixed at the current active candidate
- only execution permission changes:
- fundamental sleeve may rebuild on quarterly fundamental refresh dates
- on non-quarter dates, fundamental sleeve may sell down but may not buy new fundamental positions
- monthly restored risk budget still goes to the momentum sleeve

- fold count: `2`

Strategy summary:
- `fixed_60_40` | snapshots=`26` | mean_return=`0.000307` | cum_return=`0.007940` | mean_cash=`0.084855` | mean_f_weight=`0.596154` | mean_m_weight=`0.400000`
- `annual_entry_monthly_exit_slow_fundamental` | snapshots=`26` | mean_return=`0.000275` | cum_return=`0.007116` | mean_cash=`0.252262` | mean_f_weight=`0.663462` | mean_m_weight=`0.084615`
- `annual_entry_monthly_exit_unconstrained` | snapshots=`26` | mean_return=`0.000263` | cum_return=`0.006799` | mean_cash=`0.233031` | mean_f_weight=`0.682692` | mean_m_weight=`0.084615`

Constraint behavior summary:
- non-quarter weak_down snapshots=`8`
- mean actual fundamental weight in slow variant=`0.663462`

Output:
- [slow_fundamental_fast_exit_execution_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_validation_v1_detail.csv)
