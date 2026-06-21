# Quarterly Fundamental Monthly Momentum Validation Note V1

Conclusion:
- the `quarterly fundamental gate + monthly momentum rank` structure is economically coherent
- but in current pre-2021 rolling validation, it does not beat direct monthly momentum
- therefore it should be archived as a valid backup structure, not promoted to the active main line

## What Was Tested

Structure:
- quarterly refresh of a fundamental candidate pool `F_t`
- monthly `mom_12_1` ranking only inside `F_t`
- final monthly holdings = equal-weight top `6`

Compared strategies:
- `direct_mom12_top6`
- `quarterly_top16_mom12_top6`
- `quarterly_top20_mom12_top6`
- `quarterly_fundamental_top16_equal`
- `quarterly_fundamental_top20_equal`

## Result

Current ranking:

1. `direct_mom12_top6` cum return = `0.013251`
2. `quarterly_top20_mom12_top6` cum return = `0.010141`
3. `quarterly_top16_mom12_top6` cum return = `0.010109`
4. `quarterly_fundamental_top16_equal` cum return = `0.008723`
5. `quarterly_fundamental_top20_equal` cum return = `0.008229`

## What This Means

This gives two clear conclusions:

First:
- the quarterly fundamental gate really did become binding in this version
- so this test is more valid than the earlier underpowered gate test

Second:
- once the gate became binding, it still reduced total return relative to direct monthly momentum

So the current evidence does **not** support:

- promoting the quarterly fundamental gate as a return-improving overlay on top of direct monthly momentum

## What Still Worked

Inside the quarterly fundamental pool:

- monthly momentum ranking still added value

Because:

- `quarterly_top16_mom12_top6` beat `quarterly_fundamental_top16_equal`
- `quarterly_top20_mom12_top6` beat `quarterly_fundamental_top20_equal`

So the structure is not useless.

Its current interpretation is:

- if we insist on a quality-gated bank universe, monthly momentum is still the better selection rule inside that gated set

## Current Judgment

This branch should now be understood as:

- a coherent but more conservative structural alternative

It is not currently:

- the best return-seeking monthly momentum architecture
- or the next priority branch against the active state-routing candidate

## Promotion Decision

Current decision should be:

1. do not promote this branch to active main-line status
2. archive it as a quality-constrained backup structure
3. keep the active upgrade focus on the `annual entry + monthly weak_down exit` candidate instead

## References

- [quarterly_fundamental_monthly_momentum_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\quarterly_fundamental_monthly_momentum_rolling_validation_v1.md)
- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
