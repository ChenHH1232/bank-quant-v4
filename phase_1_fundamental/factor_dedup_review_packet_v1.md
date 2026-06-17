# Factor Dedup Review Packet V1

Purpose:
- prepare a human-review packet for factor de-duplication
- explain each high-correlation cluster in plain language
- mark suggested keep and suggested drop candidates before manual override

## Q01

- Suggested keep: `cash_flow__staff_behalf_paid`
- Theme: 大规模簇：多数成员都在共同反映银行体量、经营规模或利润规模，强烈疑似“规模因子簇”。
- Keep reason: `highest_validation_rank_ic_mean_within_cluster`

Members:
- `cash_flow__staff_behalf_paid` | keep=`1` | val_ic=`0.07194` | corr_to_keep=``
  Meaning: 支付给职工以及为职工支付的现金，常与经营规模同步变化。
- `balance__capital_reserve_fund` | keep=`0` | val_ic=`0.032047` | corr_to_keep=`0.874163`
  Meaning: 资本公积，反映股本溢价等资本性积累。
- `balance__cash_equivalents` | keep=`0` | val_ic=`0.06421` | corr_to_keep=`0.893736`
  Meaning: 期末现金及现金等价物余额，反映账面流动现金头寸。
- `balance__deferred_tax_assets` | keep=`0` | val_ic=`0.003085` | corr_to_keep=`0.855391`
  Meaning: 递延所得税资产，反映未来可抵扣暂时性差异形成的资产。
- `balance__equities_parent_company_owners` | keep=`0` | val_ic=`0.042982` | corr_to_keep=`0.907106`
  Meaning: 归属于母公司股东权益，反映母公司口径净资产。
- `balance__ordinary_risk_reserve_fund` | keep=`0` | val_ic=`0.026662` | corr_to_keep=`0.88018`
  Meaning: 一般风险准备，银行为覆盖风险提取的准备。
- `balance__total_assets` | keep=`0` | val_ic=`0.07015` | corr_to_keep=`0.901503`
  Meaning: 总资产，反映银行整体规模。
- `balance__total_liability` | keep=`0` | val_ic=`0.067974` | corr_to_keep=`0.90118`
  Meaning: 总负债，反映银行整体负债规模。
- `balance__total_owner_equities` | keep=`0` | val_ic=`0.048194` | corr_to_keep=`0.906017`
  Meaning: 所有者权益合计，反映总净资产规模。
- `cash_flow__interest_and_commission_cashin` | keep=`0` | val_ic=`0.012403` | corr_to_keep=`0.874191`
  Meaning: 收取利息和手续费收到的现金，反映经营现金流入规模。
- `income__commission_income` | keep=`0` | val_ic=`0.031597` | corr_to_keep=`0.896455`
  Meaning: 手续费及佣金收入，反映中间业务收入规模。
- `income__interest_expense` | keep=`0` | val_ic=`0.023357` | corr_to_keep=`0.870835`
  Meaning: 利息支出，反映负债端资金成本规模。
- `income__interest_income` | keep=`0` | val_ic=`0.023568` | corr_to_keep=`0.907962`
  Meaning: 利息收入，反映生息资产收入规模。
- `income__net_profit` | keep=`0` | val_ic=`0.041145` | corr_to_keep=`0.888703`
  Meaning: 净利润，反映期间最终盈利规模。
- `income__np_parent_company_owners` | keep=`0` | val_ic=`0.048804` | corr_to_keep=`0.889736`
  Meaning: 归母净利润，反映归属于母公司股东的盈利。
- `income__operating_profit` | keep=`0` | val_ic=`0.028211` | corr_to_keep=`0.893691`
  Meaning: 营业利润，反映主营经营利润。
- `income__operating_revenue` | keep=`0` | val_ic=`0.033189` | corr_to_keep=`0.93083`
  Meaning: 营业收入，反映收入总规模。
- `income__total_profit` | keep=`0` | val_ic=`0.028211` | corr_to_keep=`0.89379`
  Meaning: 利润总额，税前利润口径。
- `indicator__adjusted_profit` | keep=`0` | val_ic=`0.037743` | corr_to_keep=`0.890542`
  Meaning: 调整后利润，剔除部分非经常性影响后的利润口径。
- `indicator__operating_profit` | keep=`0` | val_ic=`0.019338` | corr_to_keep=`0.85235`
  Meaning: 经营利润指标口径，和利润表经营利润高度接近。

## Q02

- Suggested keep: `cash_flow__invest_withdrawal_cash`
- Theme: 投资现金流簇：本质上都在描述投资活动流入/流出。
- Keep reason: `highest_validation_rank_ic_mean_within_cluster`

Members:
- `cash_flow__invest_withdrawal_cash` | keep=`1` | val_ic=`0.056969` | corr_to_keep=``
  Meaning: 收回投资收到的现金，反映投资现金流入。
- `cash_flow__invest_cash_paid` | keep=`0` | val_ic=`0.011663` | corr_to_keep=`0.923177`
  Meaning: 投资支付的现金，反映投资现金流出。
- `cash_flow__subtotal_invest_cash_inflow` | keep=`0` | val_ic=`0.037029` | corr_to_keep=`0.998358`
  Meaning: 投资活动现金流入小计，投资流入总额。
- `cash_flow__subtotal_invest_cash_outflow` | keep=`0` | val_ic=`0.015089` | corr_to_keep=`0.920668`
  Meaning: 投资活动现金流出小计，投资流出总额。

## Q03

- Suggested keep: `indicator__inc_net_profit_annual`
- Theme: 利润增速簇：都在描述利润改善速度。
- Keep reason: `highest_validation_rank_ic_mean_within_cluster`

Members:
- `indicator__inc_net_profit_annual` | keep=`1` | val_ic=`0.089146` | corr_to_keep=``
  Meaning: 净利润同比增速，反映年度盈利改善。
- `indicator__inc_net_profit_to_shareholders_annual` | keep=`0` | val_ic=`0.074383` | corr_to_keep=`0.997927`
  Meaning: 归母净利润同比增速，和净利润同比几乎同义。
- `indicator__inc_operation_profit_annual` | keep=`0` | val_ic=`0.036185` | corr_to_keep=`0.96608`
  Meaning: 营业利润同比增速，反映经营利润改善。

## Q04

- Suggested keep: `indicator__roe`
- Theme: 盈利能力簇：都在描述资本或资产回报能力。
- Keep reason: `highest_validation_rank_ic_mean_within_cluster`

Members:
- `indicator__roe` | keep=`1` | val_ic=`0.124165` | corr_to_keep=``
  Meaning: 净资产收益率，反映股东资本回报能力。
- `indicator__inc_return` | keep=`0` | val_ic=`0.111121` | corr_to_keep=`0.997302`
  Meaning: 净资产收益率类回报指标口径，与 ROE 高度接近。
- `indicator__roa` | keep=`0` | val_ic=`0.040731` | corr_to_keep=`0.879294`
  Meaning: 总资产收益率，反映资产使用效率。

## Q05

- Suggested keep: `cash_flow__net_operate_cash_flow`
- Theme: 现金含金量簇：都在描述经营现金流质量。
- Keep reason: `highest_validation_rank_ic_mean_within_cluster`

Members:
- `cash_flow__net_operate_cash_flow` | keep=`1` | val_ic=`0.050865` | corr_to_keep=``
  Meaning: 经营活动现金流净额，反映经营现金创造能力。
- `indicator__ocf_to_revenue` | keep=`0` | val_ic=`0.049566` | corr_to_keep=`0.892268`
  Meaning: 经营现金流/收入，反映收入含金量。

## Q06

- Suggested keep: `income__investment_income`
- Theme: 投资/估值收益簇：都和投资类或公允价值收益相关。
- Keep reason: `highest_validation_rank_ic_mean_within_cluster`

Members:
- `income__investment_income` | keep=`1` | val_ic=`0.086041` | corr_to_keep=``
  Meaning: 投资收益，反映投资类业务贡献。
- `indicator__value_change_profit` | keep=`0` | val_ic=`0.004985` | corr_to_keep=`0.826809`
  Meaning: 公允价值变动收益，反映估值变动类收益。

## Q07

- Suggested keep: `indicator__net_profit_margin`
- Theme: 净利率簇：两个字段基本是重复口径。
- Keep reason: `highest_validation_rank_ic_mean_within_cluster`

Members:
- `indicator__net_profit_margin` | keep=`1` | val_ic=`0.179843` | corr_to_keep=``
  Meaning: 净利率，净利润/收入。
- `indicator__net_profit_to_total_revenue` | keep=`0` | val_ic=`0.179843` | corr_to_keep=`1.0`
  Meaning: 净利润占总收入比，和净利率几乎同义。

Outputs:
- [factor_dedup_review_packet_v1.csv](D:\hh\codex\v4\phase_1_fundamental\factor_dedup_review_packet_v1.csv)