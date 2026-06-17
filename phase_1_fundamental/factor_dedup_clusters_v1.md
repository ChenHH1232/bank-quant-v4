# Factor Dedup Clusters V1

Rule:
- built from pairwise `abs(spearman_corr) >= 0.8`
- only single-factor `A/B` candidates are included
- quarterly and annual targets are clustered separately

- Total clusters: `7`
- Total clustered factors: `36`

Clusters:
- `Q01` | keep `cash_flow__staff_behalf_paid` | size=`20`
- `Q02` | keep `cash_flow__invest_withdrawal_cash` | size=`4`
- `Q03` | keep `indicator__inc_net_profit_annual` | size=`3`
- `Q04` | keep `indicator__roe` | size=`3`
- `Q05` | keep `cash_flow__net_operate_cash_flow` | size=`2`
- `Q06` | keep `income__investment_income` | size=`2`
- `Q07` | keep `indicator__net_profit_margin` | size=`2`

Outputs:
- [factor_dedup_clusters_v1.csv](D:\hh\codex\v4\phase_1_fundamental\factor_dedup_clusters_v1.csv)
- [factor_dedup_cluster_members_v1.csv](D:\hh\codex\v4\phase_1_fundamental\factor_dedup_cluster_members_v1.csv)