# DeepSeek 长读进度（2026-06-17）

## 本轮目标

- 判断哪些缺失字段适合继续写规则
- 判断哪些 OCR 困难报告更适合交给 DeepSeek 长文阅读
- 修正本地 DeepSeek runner 对 `reasoning_content` 的兼容

## 缺失分类结果

基于 [eastmoney_bank_indicator_extraction_missing.csv](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_extraction_missing.csv) 做了全文分类后，结果如下：

- `field_not_found_in_full_text`: `287`
- `field_found_in_full_text_needs_rule_upgrade`: `51`
- `field_found_in_ocr_full_text_needs_model_or_manual_review`: `23`
- `incomplete_candidate_coverage_fallback_source`: `4`

分类文件：
- [eastmoney_bank_indicator_missing_classified.csv](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_missing_classified.csv)
- [eastmoney_bank_indicator_missing_classified_summary_2026-06-17.md](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_missing_classified_summary_2026-06-17.md)

## 最适合 DeepSeek 长读的报告

首批优先报告：

- `601009_XSHG` `2024`
- `601009_XSHG` `2025`
- `600036_XSHG` `2024`

对应任务包：
- [601009_XSHG_2024_fullread_prompt.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_fullread\prompts\601009_XSHG_2024_fullread_prompt.txt)
- [601009_XSHG_2025_fullread_prompt.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_fullread\prompts\601009_XSHG_2025_fullread_prompt.txt)
- [600036_XSHG_2024_fullread_prompt.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_fullread\prompts\600036_XSHG_2024_fullread_prompt.txt)

## Runner 修复

已更新 [deepseek_task_runner.py](D:\hh\codex\v4\deepseek_task_runner.py)：

- 以前只读取 `message.content`
- 现在当 `content` 为空时，会自动回退读取 `reasoning_content`
- Token report 里会额外记录是否使用了 reasoning fallback

这次修复后，之前“看起来空输出”的一些任务其实已经能看到模型真实返回

## 601009_XSHG 2024 测试结果

### 测试 1：整份 OCR 长文

任务文件：
- `601009_XSHG_2024_fullread_prompt.txt`

结果：
- 输出为空
- 实际原因不是完全没响应，而是 prompt 过大、且返回落在推理侧字段

Token 使用：
- Remaining tokens: not returned by DeepSeek API
- Target tokens: `700`
- Actual tokens:
  - prompt=`131545`
  - completion=`1400`
  - total=`132945`

### 测试 2：压缩为监管片段包

任务文件：
- [601009_XSHG_2024_snippets_prompt.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_fullread\prompts\601009_XSHG_2024_snippets_prompt.txt)

结果：
- 成功读到 `reasoning_content`
- 仍未形成干净的最终表格输出
- 但已经在推理文本里给出部分可用判断

当前从可见返回中能提炼出的候选值：
- `capital_adequacy_ratio`: `13.72`
- `tier_1_capital_adequacy_ratio`: `11.12`
- `core_tier_1_capital_adequacy_ratio`: `9.36`

注意：
- 上述值来自模型推理文本，不是模型按指定表格格式稳定输出
- 还不能直接并入正式主表

Token 使用：
- Remaining tokens: not returned by DeepSeek API
- Target tokens: `600`
- Used reasoning fallback: `yes`
- Actual tokens:
  - prompt=`28374`
  - completion=`600`
  - total=`28974`

结果文件：
- [601009_XSHG_2024_fullread_result.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_fullread\601009_XSHG_2024_fullread_result.txt)
- [601009_XSHG_2024_snippets_result.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_fullread\601009_XSHG_2024_snippets_result.txt)

## 当前结论

- “整份 OCR 全文直接喂 DeepSeek” 成本过高，不推荐作为默认方案
- “监管片段压缩包 + reasoning fallback” 可行，但还需要继续把提示词压得更结构化
- 对于 `field_not_found_in_full_text` 这类条目，不值得继续外包，应直接标记为当前源未披露
- 对于 `field_found_in_full_text_needs_rule_upgrade`，优先继续写本地规则
- 对于 `field_found_in_ocr_full_text_needs_model_or_manual_review`，再继续打磨 DeepSeek 片段任务

## Targeted 方案（字段级候选片段）

为进一步压缩 token，本轮新增：

- [prepare_bank_indicator_deepseek_targeted_tasks.py](D:\hh\codex\v4\phase_1_fundamental\prepare_bank_indicator_deepseek_targeted_tasks.py)
- [run_bank_indicator_deepseek_targeted_tasks.py](D:\hh\codex\v4\phase_1_fundamental\run_bank_indicator_deepseek_targeted_tasks.py)

对应 prompt：

- [601009_XSHG_2024_targeted_prompt.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_targeted\prompts\601009_XSHG_2024_targeted_prompt.txt)
- [601009_XSHG_2025_targeted_prompt.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_targeted\prompts\601009_XSHG_2025_targeted_prompt.txt)
- [600036_XSHG_2024_targeted_prompt.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_targeted\prompts\600036_XSHG_2024_targeted_prompt.txt)

对应结果：

- [601009_XSHG_2024_targeted_result.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_targeted\results\601009_XSHG_2024_targeted_result.txt)
- [601009_XSHG_2025_targeted_result.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_targeted\results\601009_XSHG_2025_targeted_result.txt)
- [600036_XSHG_2024_targeted_result.txt](D:\hh\codex\v4\phase_1_fundamental\deepseek_bank_indicator_targeted\results\600036_XSHG_2024_targeted_result.txt)

### Token 使用

`601009_XSHG_2024_targeted`
- Remaining tokens: not returned by DeepSeek API
- Target tokens: `500`
- Used reasoning fallback: `yes`
- Actual tokens:
  - prompt=`3230`
  - completion=`500`
  - total=`3730`

`601009_XSHG_2025_targeted`
- Remaining tokens: not returned by DeepSeek API
- Target tokens: `500`
- Used reasoning fallback: `yes`
- Actual tokens:
  - prompt=`2223`
  - completion=`500`
  - total=`2723`

`600036_XSHG_2024_targeted`
- Remaining tokens: not returned by DeepSeek API
- Target tokens: `500`
- Used reasoning fallback: `yes`
- Actual tokens:
  - prompt=`2361`
  - completion=`500`
  - total=`2861`

### 当前观察

- Targeted 方案比“整份 OCR 全文”显著节省 token
- 但 DeepSeek 仍更倾向把结果放在 `reasoning_content`
- `601009_XSHG_2024` 的推理文本中已经再次出现可用候选值：
  - `capital_adequacy_ratio = 13.72`
  - `tier_1_capital_adequacy_ratio = 11.12`
  - `core_tier_1_capital_adequacy_ratio = 9.36`
- 这些值仍属于“推理层候选值”，暂未自动并入正式主表

### 下一步建议

1. 继续把 targeted prompt 压得更短，尽量按单字段或双字段拆包
2. 增加一个结果解析器，只从 `reasoning_content` 中提取明确数值候选
3. 对 `field_found_in_full_text_needs_rule_upgrade` 的 `51` 条继续优先修本地规则
