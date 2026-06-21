# Active Mainline JoinQuant Execution Gap Note V1

Objective:
- translate the frozen execution-preparation spec into a concrete JoinQuant implementation checklist
- lock what the current executable script must change before the next official execution round

## Scope

Reference script:
- [joinquant_v4_state_routed_dual_engine_strategy_v1.py](D:\hh\codex\v4\phase_2_momentum\joinquant_v4_state_routed_dual_engine_strategy_v1.py)

Frozen target candidate:
- `annual breadth entry + monthly mom6 q50 exit + slow fundamental, fast exit`

Reference baseline:
- `fixed_60_40`

## Current Script Status

The current script is usable as an earlier state-routed prototype, but it does not yet match the frozen active-mainline execution contract.

It still mixes:
- baseline branch
- old annual-only proxy branches
- monthly momentum refresh logic
- unconstrained cross-date fundamental rebuild behavior

So it is not yet the final executable form for the active candidate.

## Gap 1: Variant Scope Is Too Wide

Current script still exposes:
- `fixed_60_40`
- `delta_median_only`
- `breadth_only`

Execution-preparation scope should keep only:
1. `fixed_60_40`
2. active candidate with annual entry plus monthly exit

Required change:
- remove `delta_median_only`
- remove annual-only `breadth_only` from the executable comparison round
- replace the active non-baseline branch with a dedicated candidate variant name

Recommended candidate variant name:
- `annual_entry_monthly_exit_slow_fundamental`

## Gap 2: State Schedule Is Annual-Only

Current script uses frozen annual budget schedules only.

That is enough for:
- baseline
- annual-only breadth route

That is not enough for the active candidate because the active candidate needs:
- annual entry state from `breadth_only`
- monthly repair check from bank cross-sectional `mom_6_1` positive ratio
- `weak_down -> neutral_flat` release only

Required change:
- keep the frozen annual breadth schedule as the annual anchor
- add a monthly release evaluation layer on monthly refresh dates
- do not allow monthly logic to reopen `strong_up`
- do not allow monthly logic to change states other than `weak_down -> neutral_flat`

## Gap 3: Exit Signal Is Wrong Layer

Current script refreshes the momentum sleeve monthly, but it does not implement the frozen monthly exit signal as a state-transition rule.

Frozen monthly exit rule:
- signal = bank cross-sectional `mom_6_1` positive ratio
- threshold = train-set `q50`
- action = only release from `weak_down` to `neutral_flat`

Required change:
- compute monthly `mom_6_1` positive ratio on monthly refresh dates
- compare against the frozen `q50` threshold
- if annual anchor state is `weak_down` and release condition is met, temporarily use `neutral_flat`
- otherwise retain annual anchor state

Implementation note:
- this is a state override layer
- this is not a new annual classification layer

## Gap 4: Execution Permission Is Too Loose

Current script rebuilds:
- fundamental sleeve from the latest approved pool
- momentum sleeve from the monthly score frame

Then it directly combines both sleeves into one target map and trades to that target.

This behavior is too loose for the frozen interpretation because it allows the monthly cycle to effectively rebuild the whole portfolio every time.

Frozen execution boundary:
- on fundamental rebalance dates:
- fundamental sleeve may buy, sell, and rebuild
- on non-fundamental dates:
- fundamental sleeve may sell down
- fundamental sleeve may not buy new fundamental positions
- restored tactical budget should first reactivate the momentum sleeve

Required change:
- separate the fundamental sleeve target from the momentum sleeve target
- track the currently held fundamental base book
- on non-fundamental dates, do not create new fundamental positions just because the combined target map wants them
- if monthly release restores risk budget, allocate the restored tactical part to momentum first

## Gap 5: Rebalance Reason Is Too Coarse

Current rebalance reasons:
- `initial_build`
- `fundamental_refresh`
- `monthly_momentum_refresh`

For the active candidate, the monthly refresh path should distinguish:
- plain monthly momentum rerank under unchanged state
- monthly release event from `weak_down` to `neutral_flat`
- monthly no-release event while staying in `weak_down`

Required change:
- enrich log labels so later backtest review can tell whether a trade day was:
- annual rebuild
- monthly release
- monthly maintenance
- no-op because the state remained defensive

## Gap 6: Logging Does Not Expose Candidate State Mechanics

Current logging already reports:
- budget plan
- fundamental codes
- momentum preview
- combined weights

But it does not explicitly expose:
- annual anchor state
- monthly release signal value
- release threshold
- effective state after monthly override
- whether the fundamental sleeve was constrained by the slow-fundamental rule

Required change:
- add explicit logs for:
- annual_anchor_state
- monthly_release_metric
- monthly_release_threshold
- monthly_release_triggered
- effective_state_bucket
- fundamental_trade_permission
- fundamental_budget_target
- momentum_budget_target

## Gap 7: Momentum Deployment Factor Must Stay Frozen

Current script ranks the momentum sleeve with:
- `mom_12_1`

Execution-preparation contract keeps:
- monthly exit state signal = `mom_6_1` positive ratio
- monthly deployment ranking = `mom_12_1`

This is not a bug, but it must remain explicit so later edits do not accidentally switch the deployment factor.

Required change:
- keep `mom_12_1` for momentum stock selection
- use `mom_6_1` only for the release-state check

## Gap 8: Comparison Set Must Be Narrowed

The next executable round should not re-open search space.

Do not include:
- `delta_median_only`
- annual-only `breadth_only`
- unconstrained candidate
- layered fundamental gate plus momentum rank branch
- score-mixing branch

Required change:
- keep one baseline
- keep one active candidate
- freeze all other branches as documentation only

## Suggested Implementation Order

1. narrow variant list to baseline plus active candidate
2. add monthly release-state evaluation from `mom_6_1` positive ratio
3. split annual anchor state and monthly effective state
4. enforce `slow fundamental, fast exit` trading permissions
5. expand logs for state and permission diagnostics
6. run the official execution comparison round

## Practical Interpretation To Preserve

The final executable candidate should mean:

- annual layer decides the main regime anchor
- monthly layer only decides whether a defensive annual `weak_down` state can be partially released to `neutral_flat`
- fundamental capital remains slow capital
- momentum capital remains the fast tactical sleeve

This interpretation is the main thing the executable version must protect.

## References

- [active_mainline_execution_prep_spec_v1.md](D:\hh\codex\v4\phase_2_momentum\active_mainline_execution_prep_spec_v1.md)
- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
- [slow_fundamental_fast_exit_execution_rule_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\slow_fundamental_fast_exit_execution_rule_draft_v1.md)
