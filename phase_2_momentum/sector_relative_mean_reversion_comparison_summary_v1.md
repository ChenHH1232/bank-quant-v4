# Sector Relative Mean Reversion Comparison Summary V1

Date:
- `2026-06-22`

Question:
- can we use a bank sector ETF mean line as the reference anchor for single-stock mean reversion?
- tested ETF proxy = `sh512800`

Shared rolling setup:
- `38` monthly rolling folds
- target = next-month return `y_month_total_return_close`
- all versions use the same monthly rolling validation framework

Definitions:
- `V2`: return-difference
  - signal = stock short-term return minus ETF short-term return
- `V3`: price-ratio moving-average deviation
  - signal = `(stock close / ETF close) / rolling_mean - 1`
- `V4`: price-ratio zscore and bollinger deviation
  - signal = ratio zscore, or the amount by which ratio falls below the lower band

Comparison Table:

| Version | Core idea | Best review candidate | Review mean_rank_ic | Review top-bottom | Best validation candidate | Validation mean_rank_ic | Validation top-bottom | Stability read |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- |
| `V2` | stock underperforms ETF, then mean reverts | `rel_etf_rev_20d` | `0.069258` | `0.010248` | `rel_etf_rev_10d` | `0.009824` | `0.003933` | strongest local highlight, but review and validation disagree sharply |
| `V3` | stock/ETF ratio deviates from short MA | `ratio_to_ma_5d` | `0.019830` | `0.001490` | `ratio_to_ma_20d` | `0.005608` | `0.004535` | weaker but flatter; still no common winner across windows |
| `V4` | stock/ETF ratio zscore or lower-band break | `ratio_below_lower_10d` | `0.001746` | `-0.009633` | `ratio_z_40d` | `0.019353` | `0.001181` | no real improvement; bollinger branch is mostly weak |

Main read:
- `V2` is still the most interesting research branch because it produced the clearest review-phase alpha signal.
- `V3` is conceptually cleaner if we want a true "mean line" definition, but the signal is much weaker.
- `V4` did not improve stability; zscore and lower-band formulations still fail to give a train/validation/review-consistent winner.

What this means:
- the idea "single stock versus sector ETF can form a mean-reversion path" is valid as a research direction.
- but on current local rolling evidence, none of these ETF-relative variants is stable enough to promote into the main strategy line.
- for now, this should remain a side research branch, not a production rule.

Suggested next step:
- if we continue this branch, the best next move is not another small signal tweak.
- the better next test is to combine ETF-relative signal with an existing stronger primary engine:
- example 1: momentum first, ETF-relative mean reversion only as entry timing
- example 2: fundamental stock pool first, ETF-relative signal only as tactical overlay

Related files:
- [sector_relative_mean_reversion_rolling_validation_v2.md](D:\hh\codex\v4\phase_2_momentum\sector_relative_mean_reversion_rolling_validation_v2.md)
- [sector_relative_mean_reversion_rolling_validation_v3.md](D:\hh\codex\v4\phase_2_momentum\sector_relative_mean_reversion_rolling_validation_v3.md)
- [sector_relative_mean_reversion_rolling_validation_v4.md](D:\hh\codex\v4\phase_2_momentum\sector_relative_mean_reversion_rolling_validation_v4.md)
- [build_sector_relative_mean_reversion_rolling_validation_v2.py](D:\hh\codex\v4\phase_2_momentum\build_sector_relative_mean_reversion_rolling_validation_v2.py)
- [build_sector_relative_mean_reversion_rolling_validation_v3.py](D:\hh\codex\v4\phase_2_momentum\build_sector_relative_mean_reversion_rolling_validation_v3.py)
- [build_sector_relative_mean_reversion_rolling_validation_v4.py](D:\hh\codex\v4\phase_2_momentum\build_sector_relative_mean_reversion_rolling_validation_v4.py)
