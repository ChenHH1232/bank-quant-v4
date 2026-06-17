# `bank_indicator` 53字段替代映射

更新时间：2026-06-17

结论先行：

- 可直接替代：1个
- 可近似替代或公式重建：12个
- 可用“上一期当前值”规则回填：6个
- 在当前可访问的聚宽/Tushare API范围内暂时无解：34个

判定口径：

- “直接替代”指官方常规接口里已有同口径或非常接近的现成字段。
- “近似替代/公式重建”指可以用三大报表或财务指标重新计算，但口径可能和 `bank_indicator` 的监管口径不完全一致。
- “规则回填”只适用于 `former_*` 这类“上年同期/上期口径”字段，本质上是滞后一期。
- “暂时无解”指在你当前可访问的聚宽普通/金融三大报表、财务指标、Tushare `income` / `balancesheet` / `cashflow` / `fina_indicator` 中，没有可靠同口径替代字段。

| 字段 | 分类 | 可用来源 | 替代思路 | 备注 |
| --- | --- | --- | --- | --- |
| `total_loan` | 近似替代 | Tushare `balancesheet.decr_in_disbur`；聚宽 `balance` 中贷款垫款相关字段 | 用期末贷款及垫款余额代替 | 常见可用，但不同库对减值前后、并表口径可能有差异 |
| `total_deposit` | 近似替代 | Tushare `balancesheet.depos` / `depos_ib_deposits` | 用吸收存款或“吸收存款及同业存放”代替 | 需先确认你最终采用客户存款口径还是广义负债口径 |
| `interest_earning_assets` | 近似替代 | 聚宽/Tushare 资产负债表 | 用贷款垫款、存放同业、买入返售、债权投资、部分交易性金融资产等求和 | 强依赖你定义的“生息资产”篮子 |
| `non_interest_earning_assets` | 近似替代 | 聚宽/Tushare 资产负债表 | `total_assets - interest_earning_assets` | 依赖上一项定义 |
| `interest_earning_assets_yield` | 近似替代 | 聚宽/Tushare 利润表 + 资产负债表 | `interest_income / average(interest_earning_assets)` | 需要自建平均余额口径 |
| `interest_bearing_liabilities` | 近似替代 | 聚宽/Tushare 资产负债表 | 用吸收存款、同业存放、向央行借款、拆入资金、应付债券等求和 | 依赖你定义的“付息负债”篮子 |
| `non_interest_bearing_liabilities` | 近似替代 | 聚宽/Tushare 资产负债表 | `total_liability - interest_bearing_liabilities` | 依赖上一项定义 |
| `interest_bearing_liabilities_interest_rate` | 近似替代 | 聚宽/Tushare 利润表 + 资产负债表 | `interest_expense / average(interest_bearing_liabilities)` | 需要自建平均余额口径 |
| `non_interest_income` | 近似替代 | 聚宽 `income`；Tushare `income` | 用手续费及佣金净收入、投资收益、公允价值变动、汇兑、其他收益等求和，或 `total_operating_revenue - interest_income` | 推荐保留一版“明细求和口径”与一版“收入差额口径” |
| `non_interest_income_ratio` | 近似替代 | 聚宽/Tushare 利润表 | `non_interest_income / total_operating_revenue` | 依赖上一项 |
| `net_interest_margin` | 近似替代 | 聚宽/Tushare 利润表 + 资产负债表 | `(interest_income - interest_expense) / average(interest_earning_assets)` | 监管口径与研究口径可能略有偏差 |
| `net_profit_margin` | 直接替代 | 聚宽 `indicator.net_profit_margin`；Tushare `fina_indicator.netprofit_margin` | 直接取值 | 这是当前最稳的一项 |
| `core_level_capital` | 暂时无解 | 无 | 无 | 监管资本定义带扣减项，普通三大报表无法可靠还原 |
| `net_core_level_capital` | 暂时无解 | 无 | 无 | 同上 |
| `core_level_capital_adequacy_ratio` | 暂时无解 | 无 | 无 | 需要监管资本与风险加权资产口径 |
| `net_level_1_capital` | 暂时无解 | 无 | 无 | 普通财报字段不够 |
| `level_1_capital_adequacy_ratio` | 暂时无解 | 无 | 无 | 普通财报字段不够 |
| `net_capital` | 暂时无解 | 无 | 无 | 普通财报字段不够 |
| `capital_adequacy_ratio` | 暂时无解 | 无 | 无 | 普通财报字段不够 |
| `weighted_risky_asset` | 暂时无解 | 无 | 无 | 风险加权资产不在当前可访问常规接口中 |
| `deposit_loan_ratio` | 近似替代 | 上面两项重建后 | `total_loan / total_deposit` | 依赖 `total_loan` 与 `total_deposit` 的最终口径 |
| `short_term_asset_liquidity_ratio_CNY` | 暂时无解 | 无 | 无 | 属于更细监管流动性指标 |
| `short_term_asset_liquidity_ratio_FC` | 暂时无解 | 无 | 无 | 属于更细监管流动性指标 |
| `Nonperforming_loan_rate` | 暂时无解 | 无 | 无 | 标准三大报表和 `fina_indicator` 里没有银行不良率专门字段 |
| `single_largest_customer_loan_ratio` | 暂时无解 | 无 | 无 | 客户集中度指标，不在当前常规 API |
| `top_ten_customer_loan_ratio` | 暂时无解 | 无 | 无 | 客户集中度指标，不在当前常规 API |
| `bad_debts_reserve` | 暂时无解 | 无 | 无 | 普通财报缺少可稳定映射的银行拨备余额字段 |
| `non_performing_loan_provision_coverage` | 暂时无解 | 无 | 无 | 依赖拨备余额和不良贷款余额/率，同样缺失 |
| `cost_to_income_ratio` | 近似替代 | 聚宽 `income` / `indicator`；Tushare `income` / `fina_indicator` | 推荐研究口径：`(operating_cost + administration_expense + financial_expense + sale_expense) / operating_revenue`，或直接用费用率字段组合 | 不同机构“成本收入比”监管披露口径可能不同 |
| `former_core_capital` | 规则回填 | 对应字段滞后一期 | `lag(core_level_capital, 1y)` | 仅当上一年当前值已知时可回填 |
| `former_net_core_capital` | 规则回填 | 对应字段滞后一期 | `lag(net_core_level_capital, 1y)` | 同上 |
| `former_net_core_capital_adequacy_ratio` | 规则回填 | 对应字段滞后一期 | `lag(core_level_capital_adequacy_ratio, 1y)` 或按最终字段名统一滞后 | 同上 |
| `former_net_capital` | 规则回填 | 对应字段滞后一期 | `lag(net_capital, 1y)` | 同上 |
| `former_capital_adequacy_ratio` | 规则回填 | 对应字段滞后一期 | `lag(capital_adequacy_ratio, 1y)` | 同上 |
| `former_weighted_risky_asset` | 规则回填 | 对应字段滞后一期 | `lag(weighted_risky_asset, 1y)` | 同上 |
| `normal_amount` | 暂时无解 | 无 | 无 | 五级分类贷款余额，当前常规 API 不提供 |
| `normal_amount_ratio` | 暂时无解 | 无 | 无 | 依赖五级分类明细 |
| `concerned_amount` | 暂时无解 | 无 | 无 | 五级分类贷款余额，当前常规 API 不提供 |
| `concerned_amount_ratio` | 暂时无解 | 无 | 无 | 依赖五级分类明细 |
| `secondary_amount` | 暂时无解 | 无 | 无 | 五级分类贷款余额，当前常规 API 不提供 |
| `secondary_amount_ratio` | 暂时无解 | 无 | 无 | 依赖五级分类明细 |
| `suspicious_amount` | 暂时无解 | 无 | 无 | 五级分类贷款余额，当前常规 API 不提供 |
| `suspicious_amount_ratio` | 暂时无解 | 无 | 无 | 依赖五级分类明细 |
| `loss_amount` | 暂时无解 | 无 | 无 | 五级分类贷款余额，当前常规 API 不提供 |
| `loss_amount_ratio` | 暂时无解 | 无 | 无 | 依赖五级分类明细 |
| `short_term_loan_average_balance` | 暂时无解 | 无 | 无 | 需要贷款期限结构平均余额，常规 API 不给 |
| `short_term_loan_annualized_average_interest_rate` | 暂时无解 | 无 | 无 | 需要贷款期限结构收益率，常规 API 不给 |
| `mid_term_loan_average_balance` | 暂时无解 | 无 | 无 | 需要贷款期限结构平均余额，常规 API 不给 |
| `mid_term_loan_annualized_average_interest_rate` | 暂时无解 | 无 | 无 | 需要贷款期限结构收益率，常规 API 不给 |
| `enterprise_deposits_average_balance` | 暂时无解 | 无 | 无 | 需要存款结构平均余额，常规 API 不给 |
| `enterprise_deposits_average_interest_rate` | 暂时无解 | 无 | 无 | 需要存款结构利率，常规 API 不给 |
| `savings_deposit_average_balance` | 暂时无解 | 无 | 无 | 需要存款结构平均余额，常规 API 不给 |
| `savings_deposit_average_interest_rate` | 暂时无解 | 无 | 无 | 需要存款结构利率，常规 API 不给 |

## 建议落地顺序

1. 先保留 `bank_indicator` 2014-2023 原值，不做口径改写。
2. 对 2024-2025 年，优先补一版“研究可用替代版”：
   - `total_loan`
   - `total_deposit`
   - `interest_earning_assets`
   - `interest_bearing_liabilities`
   - `non_interest_income`
   - `non_interest_income_ratio`
   - `net_interest_margin`
   - `net_profit_margin`
   - `deposit_loan_ratio`
   - `cost_to_income_ratio`
3. 把替代版字段单独打标，例如：
   - `source_type = original_bank_indicator`
   - `source_type = reconstructed_from_statements`
4. 把资本充足率、五级分类、客户集中度、贷款/存款期限结构等字段先从 2024-2025 横截面主模型里剔除，避免伪精确。

## 现阶段最值得补的“研究替代版”字段

- 资产规模：`total_loan`、`total_deposit`
- 息差经营：`interest_earning_assets_yield`、`interest_bearing_liabilities_interest_rate`、`net_interest_margin`
- 收入结构：`non_interest_income`、`non_interest_income_ratio`
- 经营效率：`cost_to_income_ratio`
- 盈利：`net_profit_margin`
- 结构性约束：`deposit_loan_ratio`

