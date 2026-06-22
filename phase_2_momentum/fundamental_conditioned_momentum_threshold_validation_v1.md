# Fundamental Conditioned Momentum Threshold Validation V1

Objective:
- test whether the monthly momentum release threshold should be conditioned on fundamental deterioration regime
- fixed release backbone = `mom6_positive_ratio`
- deteriorating regime = require stronger momentum confirmation
- improving regime = allow easier momentum release

Rule:
- if deterioration regime = `deteriorating`, release cut = train `q67`
- if deterioration regime = `improving`, release cut = train `q50`
- if deterioration regime = `neutral`, release cut = midpoint between `q50` and `q67`

- fold count: `2`

Conditioned-threshold summary:
- snapshots=`26`
- mean_return=`0.000258`
- cum_return=`0.006663`
- mean_cash=`0.248416`

Regime summary:
- `deteriorating` | snapshots=`2` | mean_return=`-0.001022` | mean_cut=`1.000000` | mean_signal=`0.705357`
- `improving` | snapshots=`2` | mean_return=`0.001320` | mean_cut=`0.854395` | mean_signal=`0.500000`
- `neutral` | snapshots=`22` | mean_return=`0.000277` | mean_cut=`0.927198` | mean_signal=`0.600105`

Weak-down release behavior:
- weak_down_snapshots=`20`
- released_to_neutral=`3`
- held_in_weak_down=`17`

Compare against fixed references:
- benchmark reference should be `mom6_positive_ratio_q50` from the weak-down exit refinement note
- if conditioned thresholds do not beat that baseline, keep the simpler fixed-threshold rule

Output:
- [fundamental_conditioned_momentum_threshold_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\fundamental_conditioned_momentum_threshold_validation_v1_detail.csv)
