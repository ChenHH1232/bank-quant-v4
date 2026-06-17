# Eastmoney 银行专项指标数值抽取进度（2026-06-17）

- 候选全覆盖报告数：`80`
- 已输出结构化数值行数：`707`
- 已覆盖报告数：`80`
- 备用源待补条目数：`8`
- 数值未自动识别条目数：`253`

当前规则：
- 只对 `12/12` 全覆盖报告进入正式数值抽取
- `601328_XSHG 2025` 整份报告单独记入备用源待补
- 自动抽取结果默认标记为 `needs_check`，后续可继续用 DeepSeek 或人工批量复核

输出文件：
- [eastmoney_bank_indicator_extracted_values.csv](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_extracted_values.csv)
- [eastmoney_bank_indicator_extraction_missing.csv](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_extraction_missing.csv)