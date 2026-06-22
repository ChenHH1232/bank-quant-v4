# Momentum First Fundamental Tiebreak Grid V1

Objective:
- perform a limited neighborhood expansion around the momentum-first fundamental-second-stage idea
- keep the search deliberately narrow to avoid overfitting

Search axes:
- momentum backbone = `mom_12_1` vs `mom_6_1`
- stage-1 momentum candidate count = `8 / 10 / 12`
- final hold count = `4 / 6 / 8` in a very limited local extension
- control references = `direct_mom12_top6` and `quarterly_top20_mom12_top6`

- fold count: `2`
- strategy snapshots: `260`

Strategy ranking:
- `mom12_top10_then_fundamental_top4` | momentum=`score__mom12` | stage1=`10` | hold=`4` | snapshots=`26` | mean_return=`0.000529` | cum_return=`0.013712` | mean_stage1_actual_count=`10.00`
- `mom12_top10_then_fundamental_top6` | momentum=`score__mom12` | stage1=`10` | hold=`6` | snapshots=`26` | mean_return=`0.000528` | cum_return=`0.013706` | mean_stage1_actual_count=`10.00`
- `direct_mom12_top6` | momentum=`score__mom12` | stage1=`all` | hold=`6` | snapshots=`26` | mean_return=`0.000512` | cum_return=`0.013251` | mean_stage1_actual_count=`14.69`
- `mom12_top8_then_fundamental_top6` | momentum=`score__mom12` | stage1=`8` | hold=`6` | snapshots=`26` | mean_return=`0.000449` | cum_return=`0.011607` | mean_stage1_actual_count=`8.00`
- `mom12_top12_then_fundamental_top6` | momentum=`score__mom12` | stage1=`12` | hold=`6` | snapshots=`26` | mean_return=`0.000445` | cum_return=`0.011534` | mean_stage1_actual_count=`12.00`
- `mom12_top10_then_fundamental_top8` | momentum=`score__mom12` | stage1=`10` | hold=`8` | snapshots=`26` | mean_return=`0.000433` | cum_return=`0.011197` | mean_stage1_actual_count=`10.00`
- `mom6_top12_then_fundamental_top6` | momentum=`score__mom6` | stage1=`12` | hold=`6` | snapshots=`26` | mean_return=`0.000419` | cum_return=`0.010854` | mean_stage1_actual_count=`12.00`
- `mom6_top8_then_fundamental_top6` | momentum=`score__mom6` | stage1=`8` | hold=`6` | snapshots=`26` | mean_return=`0.000399` | cum_return=`0.010299` | mean_stage1_actual_count=`8.00`
- `quarterly_top20_mom12_top6` | momentum=`score__mom12` | stage1=`all` | hold=`6` | snapshots=`26` | mean_return=`0.000393` | cum_return=`0.010141` | mean_stage1_actual_count=`13.27`
- `mom6_top10_then_fundamental_top6` | momentum=`score__mom6` | stage1=`10` | hold=`6` | snapshots=`26` | mean_return=`0.000350` | cum_return=`0.009043` | mean_stage1_actual_count=`10.00`

Recommended next-step shortlist:
- `mom12_top10_then_fundamental_top4` | cum_return=`0.013712` | mean_return=`0.000529`
- `mom12_top10_then_fundamental_top6` | cum_return=`0.013706` | mean_return=`0.000528`
- `direct_mom12_top6` | cum_return=`0.013251` | mean_return=`0.000512`

Interpretation rule:
- prefer a small cluster of nearby strong variants over a single isolated winner
- only those shortlisted variants should move to the frozen post-2021 JoinQuant acceptance stage

Output:
- [momentum_first_fundamental_tiebreak_grid_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\momentum_first_fundamental_tiebreak_grid_v1_detail.csv)
