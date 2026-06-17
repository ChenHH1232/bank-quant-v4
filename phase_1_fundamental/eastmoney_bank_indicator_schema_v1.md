# 东方财富年报专项指标标准表结构 v1

用途：为东方财富年报 PDF 的银行专项指标抽取建立统一的长表结构，便于后续批量抽取、人工复核、与聚宽 `bank_indicator` 拼接。

## 必填字段

| column_name | type | purpose | example_value |
| --- | --- | --- | --- |
| `code` | `string` | 股票代码，带交易所后缀 | `000001.XSHE` |
| `bank_name` | `string` | 银行名称 | `平安银行` |
| `source_type` | `string` | 固定来源标签 | `eastmoney_annual_report_pdf` |
| `source_file` | `string` | PDF 文件名 | `000001_XSHE_2024_annual_report.pdf` |
| `field_name_english` | `string` | 标准化英文字段名 | `capital_adequacy_ratio` |
| `field_name_chinese` | `string` | 年报原始中文字段名 | `资本充足率` |
| `report_year` | `int` | 年报所属年份 | `2024` |
| `value` | `float` | 抽取后的数值 | `13.11` |
| `unit_or_percent` | `string` | 单位或百分比标识 | `%` |
| `value_scope` | `string` | 口径范围 | `Group` |
| `note` | `string` | 额外说明 | `标准值≥10.75（注2）` |

## 可选字段

| column_name | type | purpose | example_value |
| --- | --- | --- | --- |
| `source_page` | `int` | 指标所在 PDF 页码 | `20` |
| `raw_snippet_reference` | `string` | 对应文本片段文件或片段 id | `000001_XSHE_2024_annual_report_bank_indicator_snippets.txt#snippet_12` |
| `raw_snippet_text` | `string` | 原始片段文本 | `资本充足率 ≥10.75 13.11 13.43 13.01` |
| `extraction_method` | `string` | 抽取方式 | `deepseek_assisted_manual_review` |
| `review_status` | `string` | 复核状态 | `reviewed` |
| `review_note` | `string` | 复核备注 | `集团口径与本行口径已区分` |
| `report_date` | `string` | 报告期末日期 | `2024-12-31` |
| `notice_date` | `string` | 公告披露日期 | `2025-03-15` |
| `standard_threshold` | `string` | 年报中对应监管标准值 | `>=10.75` |
| `mapping_target` | `string` | 若需映射到旧 `bank_indicator` 的目标字段 | `capital_adequacy_ratio` |
| `confidence` | `string` | 抽取置信度 | `high` |

## Validation Rules

1. `code + field_name_english + report_year + source_file` 应唯一。
2. `report_year` 必须与 `source_file` 中的年份一致。
3. `value` 必须是可解析数值，不能保留 `%`、`≥`、`,` 等字符。
4. `unit_or_percent` 应只保留简洁单位，如 `%`、`bps`、`times`、`RMB bn`。
5. `value_scope` 只允许使用受控枚举：`Group`、`Bank`、`Unknown`。
6. 同一字段若同时存在集团口径和本行口径，应拆成两行，并在 `value_scope` 区分。
7. `field_name_english` 必须使用 snake_case，避免空格和中划线。
8. `field_name_chinese` 应尽量保留年报原始写法，不要自行改写。
9. 若值来自估计、补算或表格跨行拼接，应在 `review_note` 明确说明。
10. `review_status` 至少区分 `unreviewed`、`reviewed`、`needs_check`。
11. 抽取不到值时不要写空数值行，缺失应记录在单独缺失日志中。
12. 若同页存在多个相似指标，必须保留 `raw_snippet_reference` 方便回查。

## 最小核心字段

首批批量抽取建议优先覆盖以下 10 个指标：

| field_name_english | field_name_chinese |
| --- | --- |
| `capital_adequacy_ratio` | 资本充足率 |
| `tier_1_capital_adequacy_ratio` | 一级资本充足率 |
| `core_tier_1_capital_adequacy_ratio` | 核心一级资本充足率 |
| `non_performing_loan_ratio` | 不良贷款率 |
| `provision_coverage_ratio` | 拨备覆盖率 |
| `provision_to_loan_ratio` | 拨贷比 / 拨贷比率 |
| `liquidity_ratio` | 流动性比例（本外币） |
| `liquidity_matching_ratio` | 流动性匹配率 |
| `single_largest_customer_loan_ratio` | 单一最大客户贷款占资本净额比率 |
| `top_ten_customer_loan_ratio` | 最大十家客户贷款占资本净额比率 |

## 推荐文件格式

- 抽取主表：CSV
- 复核说明：Markdown
- 缺失日志：CSV
- 原始片段：TXT

## 与当前样例的关系

当前样例文件 [pingan_bank_indicator_sample_2024_2025.csv](D:/hh/codex/v4/phase_1_fundamental/pingan_bank_indicator_sample_2024_2025.csv) 已经符合本 schema 的最小主干，但后续建议补充：

- `value_scope`
- `source_page`
- `raw_snippet_reference`
- `extraction_method`
- `review_status`

