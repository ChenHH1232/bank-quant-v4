import argparse
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


KEYWORDS = [
    "资本充足率",
    "資本充足率",
    "一级资本充足率",
    "一級資本充足率",
    "核心一级资本充足率",
    "核心一級資本充足率",
    "不良贷款率",
    "不良貸款率",
    "拨备覆盖率",
    "撥備覆蓋率",
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
    "单一最大客户贷款占资本净额比率",
    "單一最大客戶貸款占資本淨額比率",
    "最大十家客户贷款占资本净额比率",
    "最大十家客戶貸款占資本淨額比率",
    "单一客户贷款集中度",
    "單一客戶貸款集中度",
    "最大十家客户贷款集中度",
    "最大十家客戶貸款集中度",
    "单一集团客户授信集中度",
    "單一集團客戶授信集中度",
    "补充监管指标",
    "補充監管指標",
    "主要监管指标",
    "主要監管指標",
]


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def find_all(text: str, pattern: str) -> Iterable[int]:
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


def looks_like_pdf(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1024:
        return False
    return path.read_bytes()[:5] == b"%PDF-"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Eastmoney annual report text and bank-indicator snippets.")
    parser.add_argument(
        "--pdf",
        action="append",
        required=True,
        help="Annual report PDF filename under eastmoney_reports/batch. Can be passed multiple times.",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    pdf_dir = base_dir / "eastmoney_reports" / "batch"
    out_dir = base_dir / "eastmoney_reports" / "extracted_text"
    out_dir.mkdir(parents=True, exist_ok=True)

    for pdf_name in args.pdf:
        pdf_path = pdf_dir / pdf_name
        if not looks_like_pdf(pdf_path):
            print(f"SKIP_NON_PDF {pdf_name}")
            continue

        text = extract_pdf_text(pdf_path)
        text_path = out_dir / pdf_name.replace(".pdf", ".txt")
        text_path.write_text(text, encoding="utf-8")

        snippets = collect_snippets(text)
        snippet_path = out_dir / pdf_name.replace(".pdf", "_bank_indicator_snippets.txt")
        snippet_path.write_text("\n\n-----\n\n".join(snippets) if snippets else "NO_HITS", encoding="utf-8")

        print(f"EXTRACTED {pdf_name} text_chars={len(text)} snippets={len(snippets)}")


if __name__ == "__main__":
    main()
