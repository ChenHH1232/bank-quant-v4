# Eastmoney 银行专项指标小样本验证（2025 年报）

验证目标：
- 检查 [eastmoney_bank_indicator_schema_v1.md](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_schema_v1.md) 能否直接复用于更多银行
- 检查现有 10 个核心字段在不同银行年报中的命名差异
- 提前发现批量抽取前的下载和抽取风险

本次验证样本：
- `001227.XSHE` 兰州银行
- `002142.XSHE` 宁波银行
- `002807.XSHE` 江阴银行

对应文件：
- [001227_XSHE_2025_annual_report.pdf](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\batch\001227_XSHE_2025_annual_report.pdf)
- [002142_XSHE_2025_annual_report.pdf](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\batch\002142_XSHE_2025_annual_report.pdf)
- [002807_XSHE_2025_annual_report.pdf](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\batch\002807_XSHE_2025_annual_report.pdf)
- [001227_XSHE_2025_annual_report_bank_indicator_snippets.txt](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\extracted_text\001227_XSHE_2025_annual_report_bank_indicator_snippets.txt)
- [002142_XSHE_2025_annual_report_bank_indicator_snippets.txt](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\extracted_text\002142_XSHE_2025_annual_report_bank_indicator_snippets.txt)
- [002807_XSHE_2025_annual_report_bank_indicator_snippets.txt](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\extracted_text\002807_XSHE_2025_annual_report_bank_indicator_snippets.txt)

## 结论

现有标准长表结构可以继续用，不需要改列结构。
需要扩的是标准字段字典，而不是 CSV 列本身。

需要补的是“字段别名规则”，否则同一经济含义的专项指标会因为银行写法不同而漏抓。

## 兼容性结果

3 家样本共同稳定出现的字段：
- `capital_adequacy_ratio`
- `tier_1_capital_adequacy_ratio`
- `core_tier_1_capital_adequacy_ratio`
- `non_performing_loan_ratio`
- `provision_coverage_ratio`
- `liquidity_ratio`

存在口径或命名差异的字段：
- `provision_to_loan_ratio`
  - 平安银行写作 `拨贷比`
  - 兰州银行、宁波银行更常见写作 `贷款拨备率`
- 流动性附加指标
  - 平安银行、江阴银行出现 `流动性匹配率`
  - 兰州银行、宁波银行出现 `流动性覆盖率`
  - 这两者不应强行并入同一个字段，建议拆开保留

集中度类字段存在明显写法差异：
- 平安银行样例使用
  - `单一最大客户贷款占资本净额比率`
  - `最大十家客户贷款占资本净额比率`
- 兰州银行样本出现
  - `单一客户贷款集中度`
  - `最大十家客户贷款集中度`
  - `单一集团客户授信集中度`
- 这说明集中度字段必须维护别名字典，不能只靠平安银行的原始中文名

## 建议的字段映射

建议直接加入如下别名映射：

| standard field | candidate aliases |
| --- | --- |
| `provision_to_loan_ratio` | `拨贷比`, `贷款拨备率` |
| `liquidity_ratio` | `流动性比例`, `流动性比例（本外币）` |
| `liquidity_matching_ratio` | `流动性匹配率` |
| `liquidity_coverage_ratio` | `流动性覆盖率` |
| `single_largest_customer_loan_ratio` | `单一最大客户贷款占资本净额比率`, `单一客户贷款集中度` |
| `top_ten_customer_loan_ratio` | `最大十家客户贷款占资本净额比率`, `最大十家客户贷款集中度` |

## 下载风险

当前 `2025` 年报批量文件里，实际验证结果是：
- 真 PDF：`9`
- 非 PDF：`33`

这些非 PDF 文件多数是东方财富返回的反爬脚本页，不是真年报文件。

这意味着：
- 已有下载清单不能直接当作“全部可抽取”
- 批量结构化前必须先做文件有效性筛查
- 上海市场样本目前受影响尤其明显，需要后续修复下载链路

## 已做的修正

已经在 [extract_eastmoney_bank_indicator_samples.py](D:\hh\codex\v4\phase_1_fundamental\extract_eastmoney_bank_indicator_samples.py) 里补入这些关键词：
- `贷款拨备率`
- `流动性覆盖率`
- `单一客户贷款集中度`
- `最大十家客户贷款集中度`
- `单一集团客户授信集中度`

## 下一步建议

优先顺序建议如下：
- 先修复东方财富下载链路，尽量把 33 份假 PDF 替换成真 PDF
- 然后把“字段别名映射”正式写入结构化抽取规则
- 最后再批量生成 42 家银行的专项指标标准长表
