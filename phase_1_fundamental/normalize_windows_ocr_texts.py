from pathlib import Path


KEYWORDS = [
    "资本充足率",
    "資本充足率",
    "资本适足率",
    "資本適足率",
    "一级资本充足率",
    "一級資本充足率",
    "一级资本适足率",
    "一級資本適足率",
    "核心一级资本充足率",
    "核心一級資本充足率",
    "核心一级资本适足率",
    "核心一級資本適足率",
    "不良贷款率",
    "不良貸款率",
    "不良贷款比率",
    "不良貸款比率",
    "拨备覆盖率",
    "撥備覆蓋率",
    "备抵覆盖率",
    "備抵覆蓋率",
    "拨贷比",
    "撥貸比",
    "贷款拨备率",
    "貸款撥備率",
    "流动性比例",
    "流動性比例",
    "流动性匹配率",
    "流動性匹配率",
    "流动性覆盖率",
    "流動性覆蓋率",
    "流动性覆盖比率",
    "流動性覆蓋比率",
    "单一最大客户贷款占资本净额比率",
    "單一最大客戶貸款占資本淨額比率",
    "单一客户贷款集中度",
    "單一客戶貸款集中度",
    "最大十家客户贷款占资本净额比率",
    "最大十家客戶貸款占資本淨額比率",
    "最大十家客户贷款集中度",
    "最大十家客戶貸款集中度",
    "单一集团客户授信集中度",
    "單一集團客戶授信集中度",
    "主要监管指标",
    "主要監管指標",
    "补充监管指标",
    "補充監管指標",
]


def find_all(text: str, pattern: str):
    start = 0
    while True:
        idx = text.find(pattern, start)
        if idx < 0:
            return
        yield idx
        start = idx + len(pattern)


def collect_snippets(text: str) -> list[str]:
    snippets: list[str] = []
    seen: set[str] = set()
    for keyword in KEYWORDS:
        for idx in find_all(text, keyword):
            start = max(0, idx - 260)
            end = min(len(text), idx + len(keyword) + 520)
            snippet = text[start:end].replace("\x00", " ").strip()
            key = snippet[:240]
            if key in seen:
                continue
            seen.add(key)
            snippets.append(f"[{keyword}]\n{snippet}")
    return snippets


def normalize_text(text: str) -> str:
    out_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("===== PAGE"):
            out_lines.append(line)
        else:
            compact = line.replace(" ", "")
            out_lines.append(compact)
    return "\n".join(out_lines)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    ocr_dir = base_dir / "eastmoney_reports" / "ocr_text"

    for raw_path in sorted(ocr_dir.glob("*_windows_ocr.txt")):
        normalized_text = normalize_text(raw_path.read_text(encoding="utf-8", errors="ignore"))
        normalized_path = raw_path.with_name(raw_path.stem + "_normalized.txt")
        snippet_path = raw_path.with_name(raw_path.stem + "_normalized_bank_indicator_snippets.txt")
        normalized_path.write_text(normalized_text, encoding="utf-8")
        snippets = collect_snippets(normalized_text)
        snippet_path.write_text("\n\n-----\n\n".join(snippets) if snippets else "NO_HITS", encoding="utf-8")
        print(f"{raw_path.name} -> snippets={len(snippets)}")


if __name__ == "__main__":
    main()
