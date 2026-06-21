# Weak Down Exit Signal Refinement V1

Protocol:
- research scope = pre-2021 only
- annual weak-state entry stays fixed at `breadth_only`
- release destination stays fixed at `neutral_flat`
- only the monthly release trigger is refined here

- fold count: `2`

Signal ranking:
- `mom6_positive_ratio_q50` | col=`mom6_positive_ratio` | q=`0.50` | snapshots=`26` | mean_return=`0.000263` | cum_return=`0.006799` | mean_cash=`0.233031`
- `mom6_positive_ratio_q67` | col=`mom6_positive_ratio` | q=`0.67` | snapshots=`26` | mean_return=`0.000258` | cum_return=`0.006663` | mean_cash=`0.248416`
- `mom36_combo_q50` | col=`mom36_combo` | q=`0.50` | snapshots=`26` | mean_return=`0.000250` | cum_return=`0.006453` | mean_cash=`0.209954`
- `mom3_positive_ratio_q50` | col=`mom3_positive_ratio` | q=`0.50` | snapshots=`26` | mean_return=`0.000241` | cum_return=`0.006230` | mean_cash=`0.217647`
- `mom36_combo_q67` | col=`mom36_combo` | q=`0.67` | snapshots=`26` | mean_return=`0.000233` | cum_return=`0.006013` | mean_cash=`0.240723`
- `mom3_positive_ratio_q67` | col=`mom3_positive_ratio` | q=`0.67` | snapshots=`26` | mean_return=`0.000215` | cum_return=`0.005556` | mean_cash=`0.233031`

Top signal exit behavior:
- top_signal=`mom6_positive_ratio_q50`
- weak_down_snapshots=`20`
- released_to_neutral=`5`
- held_in_weak_down=`15`

Output:
- [weak_down_exit_signal_refinement_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\weak_down_exit_signal_refinement_v1_detail.csv)
