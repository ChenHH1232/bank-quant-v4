# DeepSeek 长文审阅汇总（9 份零命中年报）

目标：
- 把 9 份关键词零命中的年报文本交给 DeepSeek 做长文浏览
- 先诊断失败原因，而不是直接抽全部数值
- 判断每份文件更适合：
  - 继续做关键词/别名扩展
  - 做文本清洗/归一化
  - 直接 OCR 原始 PDF

相关目录：
- Prompt 包：
  [deepseek_zero_hit_reviews/prompts](D:\hh\codex\v4\phase_1_fundamental\deepseek_zero_hit_reviews\prompts)
- 结果：
  [deepseek_zero_hit_reviews/results](D:\hh\codex\v4\phase_1_fundamental\deepseek_zero_hit_reviews\results)

## 执行结果

9 份文件已全部提交给 DeepSeek 审阅并落盘。

其中：
- `4` 份拿到了完整、可执行的诊断
- `5` 份由于长文本过大且编码损坏严重，DeepSeek 输出被截断或返回空白，未拿到完整结构化结论

## 明确拿到的结论

### 1. `601009_XSHG_2024`
- DeepSeek 结论：优先 `retry_with_normalization`
- OCR：`No`
- 含义：
  - 文本虽然有编码损坏，但不是完全不可用
  - 更适合先做文本清洗、归一化，再重试关键词搜索

### 2. `601328_XSHG_2025`
- DeepSeek 结论：优先 `ocr_pdf`
- OCR：`Yes`
- 含义：
  - 当前文本损坏程度已经超过普通关键词/别名修补的收益
  - 直接对原始 PDF 做高质量 OCR 更划算

### 3. `601398_XSHG_2025`
- DeepSeek 结论：优先 `ocr_pdf`
- OCR：`Yes`
- 含义：
  - 文本里有大量繁体混杂和编码坏字
  - DeepSeek 仍能识别出银行专项指标章节，但建议直接 OCR

### 4. `601963_XSHG_2025`
- DeepSeek 结论：优先 `retry_with_traditional_aliases` + `retry_with_normalization`
- OCR：`No`
- 含义：
  - 当前文本总体可用
  - 问题更偏向繁体口径、编码杂质和关键词不匹配

## 未完整拿到结构化结论的文件

这些文件确实已经交给 DeepSeek 跑过，但结果被截断或空白：
- `600036_XSHG_2024`
- `600036_XSHG_2025`
- `601009_XSHG_2025`
- `601328_XSHG_2024`
- `601963_XSHG_2024`

## 基于同银行相邻年度和本地文本观察的推断

下面是推断，不是 DeepSeek 完整返回的结构化结论。

### 较大概率需要 OCR
- `600036_XSHG_2024`
- `600036_XSHG_2025`
- `601328_XSHG_2024`

推断依据：
- 本地抽取文本中存在大面积严重乱码
- DeepSeek 对同类文件容易空白或被截断
- 同银行相邻年度 `601328_XSHG_2025` 已明确建议 OCR

### 较大概率先做归一化/别名扩展
- `601009_XSHG_2025`
- `601963_XSHG_2024`

推断依据：
- 同银行相邻年度已有明确结论：
  - `601009_XSHG_2024` 建议先做 normalization
  - `601963_XSHG_2025` 建议先做 normalization + traditional aliases

## 当前可执行分组

### A 组：先做 OCR
- `600036_XSHG_2024`
- `600036_XSHG_2025`
- `601328_XSHG_2024`
- `601328_XSHG_2025`
- `601398_XSHG_2025`

### B 组：先做文本清洗 / 繁体别名 / 编码归一化
- `601009_XSHG_2024`
- `601009_XSHG_2025`
- `601963_XSHG_2024`
- `601963_XSHG_2025`

## DeepSeek 代币汇总

本轮 9 份首轮长文审阅合计：
- 目标输出代币：`2880`
- 实际输入代币：`1368310`
- 实际输出代币：`4292`
- 实际总消耗：`1372602`

补充说明：
- 之后我又对 5 份不完整文件做了更短格式的重跑测试
- 但这些重跑结果更差或仍为空，因此没有作为正式结论写入上面的主表
- DeepSeek API 仍不返回“剩余代币”

## 下一步建议

先不要继续强行把这 9 份都塞给 DeepSeek 做第二轮全文浏览。

更有效的顺序是：
1. 先对 A 组做 OCR
2. 先对 B 组做文本归一化和繁体别名扩展
3. 再重新跑关键词片段抽取
4. 如果仍然失败，再做 DeepSeek 二次审阅
