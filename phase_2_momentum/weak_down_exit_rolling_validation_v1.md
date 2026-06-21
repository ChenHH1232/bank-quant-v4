# Weak Down Exit Rolling Validation V1

Protocol:
- research scope = pre-2021 only
- annual weak-state trigger = `breadth_only`
- monthly exit signal = cross-sectional `mom_6_1` positive ratio on the monthly bank pool
- monthly exit rule only upgrades `weak_down` to `neutral_flat`
- shared budget mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

- fold count: `2`
- strategy snapshots: `78`

Strategy summary:
- `fixed_60_40` | snapshots=`26` | mean_return=`0.000303` | cum_return=`0.007821` | mean_cash=`0.083768`
- `annual_breadth_with_monthly_exit` | snapshots=`26` | mean_return=`0.000258` | cum_return=`0.006663` | mean_cash=`0.248416`
- `annual_breadth_only` | snapshots=`26` | mean_return=`0.000212` | cum_return=`0.005463` | mean_cash=`0.271493`

Exit behavior summary:
- weak-down monthly snapshots=`20`
- released_to_neutral=`3`
- held_in_weak_down=`17`
- released mean return=`0.001418`
- held mean return=`-0.000078`

Output:
- [weak_down_exit_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_rolling_validation_v1_detail.csv)
