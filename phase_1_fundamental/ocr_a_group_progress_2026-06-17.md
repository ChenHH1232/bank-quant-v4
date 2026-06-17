# A 组 OCR 进度记录（2026-06-17）

处理对象：
- `600036_XSHG_2024`
- `600036_XSHG_2025`
- `601328_XSHG_2024`
- `601328_XSHG_2025`
- `601398_XSHG_2025`

## 本轮做了什么

1. 安装 `PyMuPDF`
2. 验证了 Windows 自带 OCR（WinRT `Windows.Media.Ocr`）可用
3. 建立了完整链路：
   - PDF 渲染为 PNG
   - Windows OCR 扫页
   - OCR 全文落盘
   - 监管指标关键词片段二次抽取
4. 发现 OCR 原文里中文被拆成逐字空格
5. 增加了 OCR 文本归一化步骤，再重新抽片段

## 产物文件

脚本：
- [ocr_a_group_reports.py](D:\hh\codex\v4\phase_1_fundamental\ocr_a_group_reports.py)
- [normalize_windows_ocr_texts.py](D:\hh\codex\v4\phase_1_fundamental\normalize_windows_ocr_texts.py)

OCR 全文目录：
- [ocr_text](D:\hh\codex\v4\phase_1_fundamental\eastmoney_reports\ocr_text)

## 结果

归一化后片段命中数：
- `600036_XSHG_2024`: `171`
- `600036_XSHG_2025`: `162`
- `601328_XSHG_2024`: `12`
- `601328_XSHG_2025`: `13`
- `601398_XSHG_2025`: `69`

## 结论

- `600036` 两年年报已经被 OCR 明显救回，可以继续进入结构化抽取。
- `601398_2025` 也已经被 OCR 救回，可以继续进入结构化抽取。
- `601328` 两年年报虽然命中数不高，但已经从 `0` 变成可搜索状态，后续更适合继续补别名和规则，而不是重做整份 OCR。

## 下一步建议

优先顺序：
1. 用 OCR 归一化结果替换这 5 份文件在“零命中清单”中的状态
2. 对 `601009`、`601963` 做文本归一化和繁体/异体别名扩展
3. 再统一回看 9 份原始失败样本是否全部转为“可结构化”
