# Formal Candidate Rolling Comparison V1

Objective:
- close the current phase-2 candidate race inside one fixed rolling comparison frame
- compare only the current formal candidates, not every historical branch
- use a common monthly sample so the fixed baseline, state-switch candidate, and gated momentum candidate are directly comparable

Included candidates:
- `fixed_60_40` = fixed dual-engine baseline
- `annual_entry_monthly_exit_slow_fundamental` = annual-entry monthly-exit state-switch candidate
- `quarterly_top20_mom12_top6` = quarterly fundamental gate then monthly momentum ranking

Protocol:
- research scope = pre-2021 rolling validation only
- sample = common monthly dates present in both the state-machine detail table and the quarterly gate detail table
- fold alignment = preserve original fold ids and validation windows
- return aggregation = compound `portfolio_return` inside each fold and then summarize across folds

- fold count: `2`
- common monthly snapshots: `26`

Candidate summary:
- `quarterly_top20_mom12_top6` | role=`fundamental_gate_then_momentum_rank` | snapshots=`26` | mean_return=`0.000393` | cum_return=`0.010141` | mean_invested=`1.000000` | mean_cash=`0.000000` | positive_months=`14`
- `fixed_60_40` | role=`fixed_dual_engine_baseline` | snapshots=`26` | mean_return=`0.000307` | cum_return=`0.007940` | mean_invested=`0.915145` | mean_cash=`0.084855` | positive_months=`14`
- `annual_entry_monthly_exit_slow_fundamental` | role=`state_switch_candidate` | snapshots=`26` | mean_return=`0.000275` | cum_return=`0.007116` | mean_invested=`0.747738` | mean_cash=`0.252262` | positive_months=`14`

Fold summary:
- `fold_01`
- `fixed_60_40` | validation=`2018-11-01` to `2019-11-01` | months=`13` | cum_return=`0.006776` | mean_cash=`0.106502`
- `annual_entry_monthly_exit_slow_fundamental` | validation=`2018-11-01` to `2019-11-01` | months=`13` | cum_return=`0.005665` | mean_cash=`0.242985`
- `quarterly_top20_mom12_top6` | validation=`2018-11-01` to `2019-11-01` | months=`13` | cum_return=`0.007304` | mean_cash=`0.000000`
- `fold_02`
- `fixed_60_40` | validation=`2019-09-02` to `2020-09-01` | months=`13` | cum_return=`0.001156` | mean_cash=`0.063208`
- `annual_entry_monthly_exit_slow_fundamental` | validation=`2019-09-02` to `2020-09-01` | months=`13` | cum_return=`0.001442` | mean_cash=`0.261538`
- `quarterly_top20_mom12_top6` | validation=`2019-09-02` to `2020-09-01` | months=`13` | cum_return=`0.002816` | mean_cash=`0.000000`

Current reading:
- `quarterly_top20_mom12_top6` is the strongest current formal candidate on the common monthly rolling sample
- `fixed_60_40` is the second-line formal candidate and should be read mainly as a structural alternative rather than a promoted replacement
- `annual_entry_monthly_exit_slow_fundamental` currently trails on the same common sample and should stay archived as a coherent but weaker branch

Increment versus fixed baseline:
- `annual_entry_monthly_exit_slow_fundamental` minus `fixed_60_40` cum_return_delta=`-0.000824`
- `quarterly_top20_mom12_top6` minus `fixed_60_40` cum_return_delta=`0.002201`

Output:
- [formal_candidate_rolling_comparison_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\formal_candidate_rolling_comparison_v1_detail.csv)
