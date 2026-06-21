# Deterioration State Proxy Formal Conclusion V1

Conclusion:
- the current best observable state proxy for the bank dual-engine branch is `delta_median_only`
- the current most robust backup proxy is `breadth_only`
- both beat the fixed `60/40` baseline in pre-2021 rolling validation

## Final Candidate Ranking

Primary candidate:
- `delta_median_only`
- definition = `score_delta_median`
- best threshold setting so far = `q33 / q67`
- cumulative return = `0.004610`

Robust backup candidate:
- `breadth_only`
- definition = `- deterioration_ratio`
- robust threshold range = `q30 / q70`, `q33 / q67`, `q25 / q75`
- cumulative return range = `0.004598` to `0.004602`

Reference baseline:
- fixed `60/40`
- cumulative return = `0.004325`

## What This Means

The state signal is now better understood:

- the useful information is coming mainly from broad cross-sectional deterioration
- especially the median change of bank fundamental composite scores
- deep tail deterioration by itself is not the main driver
- more complicated multi-field combinations did not improve over the simpler median or breadth definitions

So the current interpretation should be:

- `delta_median_only` is the sharper candidate
- `breadth_only` is the more stable and simpler candidate

## Practical Promotion Rule

Current promotion should be:

1. promote `delta_median_only` to the active lead candidate
2. keep `breadth_only` as the formal robustness benchmark
3. demote the earlier `breadth_mean_bottom` composite from lead-candidate status

## Recommended Frozen Research Spec

Lead spec:
- state score = `score_delta_median`
- low cut = train-set `33%` quantile
- high cut = train-set `67%` quantile

Backup robustness spec:
- state score = `- deterioration_ratio`
- preferred cut range = train-set `30/70` or `33/67`

State mapping:
- `strong_up` => `60%` fundamental + `40%` momentum
- `neutral_flat` => `80%` fundamental + `20%` momentum
- `weak_down` => `100%` fundamental + `0%` momentum

## Deployment Interpretation

This does not yet mean:

- the state-routing branch should immediately replace the fixed `60/40` deployment baseline

It means:

- the observable-state branch now has a defensible frozen lead candidate
- future executable testing should be limited to this frozen candidate set
- new tuning should not reopen the broader state-proxy search unless this candidate fails later acceptance

## References

- [fundamental_deterioration_state_proxy_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_deterioration_state_proxy_validation_note_v1.md)
- [deterioration_state_proxy_refinement_v1.md](D:\hh\codex\v4\phase_2_momentum\deterioration_state_proxy_refinement_v1.md)
- [deterioration_state_threshold_sensitivity_v1.md](D:\hh\codex\v4\phase_2_momentum\deterioration_state_threshold_sensitivity_v1.md)
