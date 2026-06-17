# 平安银行专项指标标准化样例（2024-2025）

这份文件对应 [pingan_bank_indicator_sample_2024_2025.csv](D:\hh\codex\v4\phase_1_fundamental\pingan_bank_indicator_sample_2024_2025.csv)，已经按 [eastmoney_bank_indicator_schema_v1.md](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_schema_v1.md) 补齐为最终标准长表格式，可作为后续 42 家银行批量抽取的模板。

相关来源文件：
- [000001_XSHE_2024_annual_report.pdf](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\batch\000001_XSHE_2024_annual_report.pdf)
- [000001_XSHE_2025_annual_report.pdf](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\batch\000001_XSHE_2025_annual_report.pdf)
- [000001_XSHE_2024_annual_report_bank_indicator_snippets.txt](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\extracted_text\000001_XSHE_2024_annual_report_bank_indicator_snippets.txt)
- [000001_XSHE_2025_annual_report_bank_indicator_snippets.txt](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\extracted_text\000001_XSHE_2025_annual_report_bank_indicator_snippets.txt)

这版样例相对上一版的改动：
- 补入 `report_date`
- 补入 `value_scope`
- 补入 `standard_threshold`
- 补入 `mapping_target`
- 补入 `raw_snippet_reference`
- 补入 `raw_snippet_text`
- 补入 `extraction_method`
- 补入 `review_status`
- 补入 `review_note`
- 补入 `confidence`

当前保留的空列：
- `notice_date`
- `source_page`

保留为空的原因：
- 当前文本抽取链路已经能稳定定位到指标表，但还没有稳定抽出公告日和 PDF 页码。
- 这两个字段先留空，不影响后续批量化；等页码定位脚本稳定后可以回填。

当前样例覆盖的 10 个核心字段：
- `capital_adequacy_ratio`
- `tier_1_capital_adequacy_ratio`
- `core_tier_1_capital_adequacy_ratio`
- `non_performing_loan_ratio`
- `provision_coverage_ratio`
- `provision_to_loan_ratio`
- `liquidity_ratio`
- `liquidity_matching_ratio`
- `single_largest_customer_loan_ratio`
- `top_ten_customer_loan_ratio`

抽取口径说明：
- 资本充足率、一级资本充足率、核心一级资本充足率使用 `Group`
- 其余贷款质量和流动性指标使用 `Bank`
- `standard_threshold` 统一写成机器更容易解析的格式，比如 `>=10.75`、`<=10`、`not_applicable`
- `raw_snippet_text` 保留最小必要原文片段，方便后续人工复核和规则调试

后续建议：
- 先把这个结构复制到另外 2 到 3 家银行，检查字段名和监管阈值是否需要新增别名
- 再批量扩展到 42 家银行
