# State-Gated Dual-Engine Validation Note V1

Conclusion:
- the idea of turning momentum off in weak states remains conceptually valid
- but the current observable state proxy did not beat the fixed `60/40` dual-engine baseline in pre-2021 rolling validation

## What Was Tested

Research scope:
- pre-2021 only
- same dual-engine framework as the earlier blend test
- same strict stock-cap structure

Observable state proxy:
- `z__cross_mcap_median`
- `z__cross_mom6_positive_ratio`
- `- z__cross_money_median`

State allocation rule:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

Reference baselines:
- `fundamental_only`
- fixed `80/20`
- fixed `60/40`

## Result

Strategy summary:
- fixed `60/40` cum return = `0.004325`
- fixed `80/20` cum return = `0.003852`
- `state_gated_dual_engine` cum return = `0.003511`
- `fundamental_only` cum return = `0.002768`

So the current ranking is:

1. fixed `60/40`
2. fixed `80/20`
3. state-gated dual engine
4. pure fundamental

## Interpretation

This means:

- the current state-gating rule does add discipline
- but the present observable proxy is not strong enough to improve allocation quality over a simple fixed blend

The likely reason is:

- in the available validation folds, the proxy mostly produced `neutral_flat` and `weak_down`
- it did not create enough convincing `strong_up` exposure
- so the rule mostly reduced momentum rather than selectively redeploying it at the right times

## Practical Judgment

Current judgment should be:

- `weak-state momentum shutdown` remains a valid research direction
- but this specific observable proxy does not earn promotion
- fixed `60/40` remains the current better dual-engine baseline

## Next Step

If this branch continues, the next improvement target should be:

- better observable state-definition research

Not:

- more allocation-tier tweaking on top of the same weak proxy

That means the next serious iteration should focus on:

- improving state observability
- improving `strong_up` detection quality
- then rerunning the same pre-2021 rolling comparison

## References

- [momentum_on_off_rule_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_on_off_rule_draft_v1.md)
- [build_state_gated_dual_engine_rolling_validation_v1.py](D:\hh\codex\v4\phase_2_momentum\build_state_gated_dual_engine_rolling_validation_v1.py)
- [state_gated_dual_engine_rolling_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\state_gated_dual_engine_rolling_validation_v1.md)
