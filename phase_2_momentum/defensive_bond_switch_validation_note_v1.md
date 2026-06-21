# Defensive Bond Switch Validation Note V1

Conclusion:
- the weak-state `bond substitution` idea is reasonable
- but the current first-pass version did not beat the fixed `60/40` dual-engine baseline in pre-2021 rolling validation

## What Was Tested

Research scope:
- pre-2021 only
- same bank dual-engine framework as the earlier blend and state-gated tests
- same strict single-stock cap structure

State proxy:
- observable-only `z_mcap + z_mom6_positive_ratio - z_money`

Allocation rule:
- `strong_up` => `60%` bank fundamental + `40%` bank momentum
- `neutral_flat` => `80%` bank fundamental + `20%` bank momentum
- `weak_down` => `60%` bank fundamental + `40%` bond ETF

Defensive asset:
- `511010.XSHG`

Reference baselines:
- `fundamental_only`
- fixed `60/40`
- state-gated bank-only fallback

## Result

Strategy summary:
- fixed `60/40` cum return = `0.004325`
- state-gated bank-only cum return = `0.003511`
- state-gated bond-switch cum return = `0.003239`
- pure fundamental cum return = `0.002768`

So the current ranking is:

1. fixed `60/40`
2. state-gated bank-only
3. state-gated bond-switch
4. pure fundamental

## Interpretation

This means:

- weak-state bond substitution is not enough by itself to improve the current dual-engine allocation line
- the fallback asset choice did not solve the main problem

The likely bottleneck is still:

- weak state identification quality

Why this is the most likely explanation:

- in one weak-state snapshot, the bond sleeve helped
- in another weak-state snapshot, the bond sleeve hurt
- so the issue is not simply that bonds are always bad or always good
- the issue is that the current observable proxy does not reliably identify when the tactical sleeve should leave bank equity

## Practical Judgment

Current judgment should be:

- `bond substitution in weak states` remains a legitimate research branch
- but this first-pass implementation does not earn promotion
- fixed `60/40` remains the current better dual-engine baseline

## Stronger Observable State Direction

The next better state-research direction should not focus first on:

- changing the fallback destination again

It should focus on:

- improving the observable state definition

One especially promising observable candidate is:

- `fundamental deterioration breadth`

Meaning:

- how many bank stocks have worsening fundamental composite scores
- how large the score deterioration is

This can be turned into observable state features such as:

- share of stocks whose fundamental score is lower than the prior annual refresh
- cross-sectional mean score change
- cross-sectional median score change
- bottom-tail deterioration intensity

Why this may help:

- if bank fundamentals are broadly deteriorating, then a weak-state regime may be structural rather than only price-based
- that would give a more economically grounded warning than using price-breadth or liquidity structure alone

## Next Step

The next concrete task should be:

- build a first `fundamental deterioration state proxy` draft

Then compare:

- current observable momentum-state proxy
- fundamental deterioration proxy
- combined observable proxy

under the same pre-2021 rolling protocol.

## References

- [defensive_bond_switch_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\defensive_bond_switch_draft_v1.md)
- [defensive_bond_switch_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\defensive_bond_switch_rolling_validation_v1.md)
- [state_gated_dual_engine_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\state_gated_dual_engine_validation_note_v1.md)
