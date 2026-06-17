# 候选长表进度记录（2026-06-17）

本轮目标：
- 把已下载并完成文本抽取的银行年报整理成一张可批量复核的候选长表
- 每份报告、每个标准字段先落一条“最佳命中片段”
- 暂不强行写最终数值，先把字段映射层稳定下来

## 新增文件

- [build_eastmoney_bank_indicator_candidate_queue.py](D:\hh\codex\v4\phase_1_fundamental\build_eastmoney_bank_indicator_candidate_queue.py)
- [eastmoney_bank_indicator_candidate_queue.csv](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_candidate_queue.csv)
- [eastmoney_bank_indicator_candidate_coverage.csv](D:\hh\codex\v4\phase_1_fundamental\eastmoney_bank_indicator_candidate_coverage.csv)

## 当前结果

- 报告总数：`83`
- 候选长表行数：`988`
- 标准字段数：`12`

覆盖率统计：
- `82` 份报告达到 `12/12`
- `82` 份报告达到 `>=10/12`
- `1` 份报告低于 `5/12`

平均命中字段数：
- `11.90 / 12`

## 当前唯一低覆盖报告

- `601328_XSHG` `2025`
- 当前命中：`4 / 12`
- 片段来源：`windows_ocr_normalized`
- 公告标题：`交通银行:交通银行H股公告-2025年度报告`

说明：
- 这份报告已经不再是 `0 / 12`，补充繁体别名后可稳定命中：
  - `不良贷款率`
  - `拨备覆盖率`
  - `流动性比例`
  - `流动性覆盖率`
- 其余 `8` 个字段在当前 OCR 片段中确实未出现关键词，不是别名表遗漏导致的“假缺失”。
- 当前判断更接近“源文件覆盖不足/公告版本口径不足”：
  - 这份 Eastmoney 公告源是 `H股公告`
  - 当前抓到的监管专项片段没有包含资本充足、拨贷比、客户集中度、流动性匹配率等完整表述
- 因此这 1 份报告后续更适合走：
  - 备用公告源
  - 年报原文其他版本
  - 或单独人工/模型补录

## 这张表的用途

这不是最终数值表，而是：
- 复核队列表
- 数值抽取前的标准映射层
- 后续批量写正式长表时的稳定输入

每一行都已经带上：
- `code`
- `bank_name`
- `source_file`
- `field_name_english`
- `field_name_chinese`
- `report_year`
- `notice_date`
- `value_scope`
- `standard_threshold`
- `mapping_target`
- `source_page`
- `raw_snippet_reference`
- `raw_snippet_text`
- `extraction_method`

## 下一步建议

1. 把 `601328_XSHG 2025` 标记为“需备用源补齐”的特例
2. 先基于已完整覆盖的 `82` 份报告进入数值抽取
3. 数值层优先做 10-12 个核心银行专项字段，再扩展到正式面板
