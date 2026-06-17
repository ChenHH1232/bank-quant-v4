from pathlib import Path


PATTERNS = [
    "资本充足率",
    "一级资本充足率",
    "核心一级资本充足率",
    "不良贷款率",
    "拨备覆盖率",
    "成本收入比",
    "存贷比",
    "贷款拨备率",
    "流动性覆盖率",
    "净稳定资金比例",
    "资本",
    "不良贷款",
    "拨备",
    "流动性",
]


def find_all_occurrences(text: str, pattern: str) -> list[int]:
    hits: list[int] = []
    start = 0
    while True:
        idx = text.find(pattern, start)
        if idx < 0:
            break
        hits.append(idx)
        start = idx + len(pattern)
    return hits


def main() -> None:
    base = Path(__file__).resolve().parent / "eastmoney_reports" / "extracted_text"
    for txt in sorted(base.glob("000001_XSHE_*_annual_report.txt")):
        text = txt.read_text(encoding="utf-8", errors="ignore")
        snippets: list[str] = []

        for pattern in PATTERNS:
            for idx in find_all_occurrences(text, pattern):
                start = max(0, idx - 220)
                end = min(len(text), idx + len(pattern) + 280)
                snippet = text[start:end].replace("\x00", " ")
                snippets.append(f"[{pattern}]\n{snippet}")

        dedup: list[str] = []
        seen: set[str] = set()
        for snippet in snippets:
            key = snippet[:200]
            if key in seen:
                continue
            seen.add(key)
            dedup.append(snippet)

        out = txt.with_name(f"{txt.stem}_bank_indicator_snippets.txt")
        content = "\n\n-----\n\n".join(dedup[:120]) if dedup else "NO_HITS"
        out.write_text(content, encoding="utf-8")
        print(f"{out} :: {len(dedup)} snippets")


if __name__ == "__main__":
    main()
