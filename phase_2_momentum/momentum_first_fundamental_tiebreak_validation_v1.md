# Momentum First Fundamental Tiebreak Validation V1

Protocol:
- research scope = pre-2021 only
- momentum remains the primary monthly selector
- fundamental score uses the latest visible quarterly snapshot only
- new structure = momentum first, fundamental second-stage ranking

Compared structures:
- `direct_mom12_top6`
- `quarterly_top20_mom12_top6`
- `mom12_top10_then_fundamental_top6`
- `mom12_top12_then_fundamental_top6`

- fold count: `2`
- strategy snapshots: `104`

Strategy summary:
- `mom12_top10_then_fundamental_top6` | snapshots=`26` | mean_return=`0.000528` | cum_return=`0.013706` | mean_stage1_count=`10.00` | mean_holding_count=`6.00`
- `direct_mom12_top6` | snapshots=`26` | mean_return=`0.000512` | cum_return=`0.013251` | mean_stage1_count=`14.69` | mean_holding_count=`6.00`
- `mom12_top12_then_fundamental_top6` | snapshots=`26` | mean_return=`0.000445` | cum_return=`0.011534` | mean_stage1_count=`12.00` | mean_holding_count=`6.00`
- `quarterly_top20_mom12_top6` | snapshots=`26` | mean_return=`0.000393` | cum_return=`0.010141` | mean_stage1_count=`13.27` | mean_holding_count=`6.00`

Interpretation target:
- if the momentum-first fundamental-second-stage variants beat direct momentum, basic fundamentals add value as a tie-break quality layer without taking over the fast signal
- if they also challenge or beat the quarterly gate structure, then momentum-first plus slow fundamental ranking becomes a meaningful new active branch

Output:
- [momentum_first_fundamental_tiebreak_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\momentum_first_fundamental_tiebreak_validation_v1_detail.csv)
