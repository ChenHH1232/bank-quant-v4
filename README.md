# Bank Quant V4

一个关于 A 股银行股的量化研究项目，核心关注点是：哪些信号真的有效，哪些模块只是让回测看起来更好。  
An A-share bank-stock quantitative research project focused on a simple question: which signals truly add value, and which modules merely make backtests look better.

## 项目概览 | Overview

V4 从一个更大的设想出发：基本面、动量、均值回归和防守 overlay 都曾被认真纳入研究。  
V4 started from a broader thesis: fundamentals, momentum, mean reversion, and defensive overlays were all seriously explored.

但随着 rolling 验证和 JoinQuant 可执行回测不断推进，项目最后收敛成了一个更简单的结论：  
As rolling validation and executable JoinQuant checks accumulated, the project converged to a simpler conclusion:

> 在本项目的样本、因子定义与执行框架下，真正有效的核心是纯基本面选股；风险控制应独立处理，而不是主要依赖动量去稀释权益仓位。  
> Under this project's sample, factor definitions, and execution framework, the effective alpha core is pure fundamental stock selection, while risk control should be handled independently rather than mainly through momentum dilution.

## 最终结构 | Final Structure

当前正式候选排序：  
Current formal ranking:

1. `core_level_shadow_shortbond_overlay`
2. `balanced_shortbond_overlay`
3. `pure core_level_shadow`
4. `pure balanced`

这意味着 V4 最终没有走向“基本面 + 动量 + 均值回归”的理论完整形态，而是接受了实证结果：  
This means V4 did not end as a theoretically complete "fundamental + momentum + mean reversion" framework. It accepted the empirical result instead:

- 基本面是 alpha 主体  
  Fundamentals are the alpha engine.
- shortbond overlay 是风险控制层  
  Shortbond overlay is the risk-control layer.
- 动量与均值回归退出正式主线  
  Momentum and mean reversion are outside the formal main line.

## 这个仓库记录了什么 | What This Repository Captures

- 从 `base_core_7` 到 `base_core_6` 的因子收缩过程  
  The factor-pruning path from `base_core_7` to `base_core_6`
- 纯基本面主线 `balanced` / `core_level_shadow` 的形成  
  The formation of the two main pure-fundamental branches: `balanced` and `core_level_shadow`
- 动量分支为什么在最终执行层被拒绝  
  Why the momentum branch was rejected at the final executable-validation layer
- shortbond overlay 为什么从防守旁支升级为正式候选  
  Why shortbond overlay was promoted from a defensive side branch into the formal candidate stack
- safebox 归档如何保留每一阶段的研究现场  
  How safebox archives preserve the research trail at each stage

## 研究方法 | Research Approach

这个项目最重要的部分，不只是结果本身，而是研究纪律。  
The most important part of this project is not only the results, but the research discipline behind them.

V4 后期逐渐固定了一个很明确的证据顺序：  
Late in V4, the workflow settled into a clear evidence hierarchy:

1. 本地 rolling 负责提出候选  
   Local rolling generates candidates.
2. JoinQuant 可执行回测负责最终接受或拒绝  
   Executable JoinQuant results decide final acceptance or rejection.

这也是为什么这个项目最后会变得更简单，而不是更复杂。  
That is also why the final structure became simpler rather than more complex.

## 仓库结构 | Repository Structure

- `phase_1_fundamental`  
  纯基本面主线、因子筛选、rolling 验证、JoinQuant 执行版本  
  Pure-fundamental core, factor selection, rolling validation, and JoinQuant execution versions

- `phase_2_momentum`  
  动量、双引擎、手动切换等研究分支  
  Momentum, dual-engine, and manual-switch research branches

- `phase_3_mean_reversion`  
  均值回归与价格层辅助研究  
  Mean-reversion and price-layer supporting research

- `safebox_*`  
  分阶段归档快照，保留研究过程与当时结论  
  Time-stamped archive snapshots preserving intermediate decisions and context

## 推荐阅读 | Suggested Reading

1. [v4_full_project_report_executive_summary_2026-06-24.md](./v4_full_project_report_executive_summary_2026-06-24.md)
2. [v4_full_project_report_2026-06-24.md](./v4_full_project_report_2026-06-24.md)
3. [phase_1_fundamental/v4_final_structure_2026-06-23.md](./phase_1_fundamental/v4_final_structure_2026-06-23.md)
4. [phase_1_fundamental/v4_final_candidate_ranking_2026-06-23.md](./phase_1_fundamental/v4_final_candidate_ranking_2026-06-23.md)

## 个人陈述 | Personal Note

这份仓库也是一份个人学习记录。  
This repository is also a personal learning record.

作者没有系统性学习过金融学知识，也并非金融或相关专业出身；项目中相当一部分具体代码实现由 AI 协助完成。  
The author has not received systematic academic training in finance and is not from a finance-related major; a substantial portion of the concrete code implementation was completed with AI assistance.

因此，这个仓库更适合被理解为一个尽量诚实保留研究轨迹的项目归档，而不是一个已经被完整证明、可以直接迁移到真实资金上的成熟产品。  
Accordingly, this repository is best read as an honest archive of an evolving research process rather than as a fully proven product ready for direct capital deployment.

## 免责声明 | Disclaimer

本仓库仅作为个人研究与学习记录，不构成任何投资建议。  
This repository is a personal research and learning record and does not constitute investment advice.

仓库中的策略结果仅基于历史回测，没有经过实盘验证，可能存在过拟合、执行偏差、样本特异性以及本地研究与真实部署之间的落差。  
The strategy results shown here are based on historical backtests only and have not been validated by live trading. They may contain overfitting risk, execution bias, sample-specific distortions, and gaps between local research and real deployment.
