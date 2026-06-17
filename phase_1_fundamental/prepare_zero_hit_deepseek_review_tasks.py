from pathlib import Path


ZERO_HIT_FILES = [
    "600036_XSHG_2024_annual_report.txt",
    "600036_XSHG_2025_annual_report.txt",
    "601009_XSHG_2024_annual_report.txt",
    "601009_XSHG_2025_annual_report.txt",
    "601328_XSHG_2024_annual_report.txt",
    "601328_XSHG_2025_annual_report.txt",
    "601398_XSHG_2025_annual_report.txt",
    "601963_XSHG_2024_annual_report.txt",
    "601963_XSHG_2025_annual_report.txt",
]


INSTRUCTION = """You are reviewing one extracted annual-report text file that failed our keyword-based bank-indicator snippet search.

Your job is not to extract every value yet. Your job is to browse the long text and diagnose why our search failed.

Please return concise English under these exact headings:
1. FILE
2. LIKELY_REPORT_LANGUAGE
3. TEXT_QUALITY
4. LIKELY_BANK_INDICATOR_SECTION
5. USEFUL_ALTERNATIVE_KEYWORDS
6. WHETHER_OCR_IS_NEEDED
7. NEXT_ACTION

Rules:
- Focus on bank regulatory indicators such as capital adequacy, NPL ratio, provision coverage, provision-to-loan ratio, liquidity ratio, liquidity matching ratio, liquidity coverage ratio, and customer concentration ratios.
- If the text appears garbled, say so clearly.
- If the text is traditional Chinese, mixed script, or encoding-damaged, say so clearly.
- Under USEFUL_ALTERNATIVE_KEYWORDS, list 5-12 candidate search strings exactly as they appear or are most likely to appear in this file.
- Under NEXT_ACTION, recommend one of:
  - retry with traditional-Chinese aliases
  - retry with normalization/cleaning
  - OCR the PDF
  - manual review
- Keep the answer short and practical.

===== FILE TEXT START =====
"""


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    extracted_dir = base_dir / "eastmoney_reports" / "extracted_text"
    out_dir = base_dir / "deepseek_zero_hit_reviews" / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)

    for file_name in ZERO_HIT_FILES:
        source_path = extracted_dir / file_name
        text = source_path.read_text(encoding="utf-8", errors="ignore")
        prompt = (
            INSTRUCTION
            + text
            + "\n===== FILE TEXT END =====\n"
        )
        prompt_path = out_dir / file_name.replace(".txt", "_deepseek_review_prompt.txt")
        prompt_path.write_text(prompt, encoding="utf-8")
        print(prompt_path)


if __name__ == "__main__":
    main()
