# Momentum First Fundamental Tiebreak Candidate Note V1

## Candidate

Current proposed candidate:

- `mom12_top10_then_fundamental_top6`

Structure:

1. each month rank the tradable bank universe by `mom_12_1`
2. keep the top `10` momentum candidates
3. inside those `10`, rank by the latest visible fundamental composite score
4. hold the top `6` equally

This means:

- momentum remains the fast primary selector
- fundamentals do not define the outer pool
- fundamentals only improve quality inside the already momentum-strong candidate set

## Why This Candidate Matters

This branch answers a cleaner question than several earlier hybrids:

- can fundamentals help monthly momentum
- without taking control away from momentum

That is a different idea from:

- quarterly fundamental gate first, then momentum
- or letting fundamentals directly rewrite state-machine thresholds

The pre-2021 rolling evidence says this simpler hierarchy can work well enough to deserve formal comparison.

## Rolling Result

From [momentum_first_fundamental_tiebreak_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_first_fundamental_tiebreak_validation_v1.md):

- `mom12_top10_then_fundamental_top6` cum return = `0.013706`
- `direct_mom12_top6` cum return = `0.013251`
- `mom12_top12_then_fundamental_top6` cum return = `0.011534`
- `quarterly_top20_mom12_top6` cum return = `0.010141`

So the current best version is:

- momentum top `10`
- then fundamental top `6`

Not:

- momentum top `12`
- and not:
- quarterly fundamental gate first

## Interpretation

Current working interpretation:

- monthly momentum is still the best fast decision layer
- but inside the strongest momentum names, basic fundamentals improve selection quality
- this is more effective than letting fundamentals act as a hard outer admission gate

That is an important shift in understanding.

The better integration appears to be:

- momentum first
- fundamentals second

not:

- fundamentals first
- momentum second

## Acceptance Status

This branch did earn formal-candidate attention in pre-2021 rolling research.

Current rolling status:

- it beats pure monthly momentum in the current pre-2021 rolling test
- it beats the quarterly fundamental gate plus momentum line
- it also beats the current common-sample dual-engine and state-machine formal candidates on cumulative return

But the frozen post-2021 acceptance result changed the final deployment reading:

- `direct_mom12_top6`
  - strategy return = `40.09%`
  - excess return = `16.88%`
  - annualized return = `7.21%`
  - max drawdown = `21.30%`
- `mom12_top10_then_fundamental_top6`
  - strategy return = `27.18%`
  - excess return = `6.10%`
  - annualized return = `5.09%`
  - max drawdown = `21.45%`
- `mom12_top10_then_fundamental_top4`
  - strategy return = `14.21%`
  - excess return = `-4.72%`
  - annualized return = `2.78%`
  - max drawdown = `27.67%`

So the final status should now be:

- research-positive on rolling
- acceptance-failed as a deployment replacement
- archived as a useful structural finding, not promoted over the pure momentum executable main line

## Remaining Caveat

The same important caveat still applies:

- this is a fully invested monthly selection line
- `fixed_60_40` is an allocation-layer baseline with cash preserved under cap discipline

So this candidate should be described as:

- a strong rolling stock-selection research candidate

not as:

- the active deployment winner
- and not as the universal best portfolio-construction framework

## Current Best Reading

Safest current summary:

- strongest current allocation-layer baseline = `fixed_60_40`
- strongest current executable momentum main line = `direct_mom12_top6`
- `mom12_top10_then_fundamental_top6` remains an archived rolling-positive structural candidate

These three statements can all be true.

## References

- [momentum_first_fundamental_tiebreak_validation_v1.md](D:\hh\codex\v4\phase_2_momentum\momentum_first_fundamental_tiebreak_validation_v1.md)
- [formal_candidate_report_draft_v1.md](D:\hh\codex\v4\phase_2_momentum\formal_candidate_report_draft_v1.md)
- [allocation_vs_selection_framework_note_v1.md](D:\hh\codex\v4\phase_2_momentum\allocation_vs_selection_framework_note_v1.md)
