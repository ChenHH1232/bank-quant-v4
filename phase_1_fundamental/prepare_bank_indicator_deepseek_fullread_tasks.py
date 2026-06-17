import csv
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CLASSIFIED_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_missing_classified.csv"
OCR_DIR = SCRIPT_DIR / "eastmoney_reports" / "ocr_text"
PROMPT_DIR = SCRIPT_DIR / "deepseek_bank_indicator_fullread" / "prompts"

TARGET_CLASSIFICATION = "field_found_in_ocr_full_text_needs_model_or_manual_review"
TARGET_REPORTS = [
    ("601009_XSHG", "2024"),
    ("601009_XSHG", "2025"),
    ("600036_XSHG", "2024"),
]

INSTRUCTION = """You are reading one OCR-normalized Chinese bank annual report text.

Task:
Extract only the bank-indicator fields listed below for the stated report year.

Rules:
- Read the long text carefully. The OCR text may be compressed, cross-line, or partially damaged.
- If a field is clearly present, return the current-year value only.
- If a field is mentioned but no reliable numeric value can be recovered, mark it as VALUE=NOT_RECOVERABLE.
- If the field does not appear to be disclosed in this report text, mark it as VALUE=NOT_FOUND.
- Do not guess.
- Keep original scope semantics when obvious:
  - capital adequacy fields usually use Group scope
  - loan quality / liquidity / customer concentration fields usually use Bank scope
- Output only under the exact headings below.

Output format:
1. FILE
2. REPORT_YEAR
3. EXTRACTION_TABLE

Under EXTRACTION_TABLE, output pipe-separated rows with this exact header:
field_name_english|field_name_chinese|value|unit_or_percent|value_scope|confidence|evidence_excerpt

Confidence values:
- high
- medium
- low

Keep evidence_excerpt short, at most 120 characters each.

===== TARGET FIELDS START =====
"""


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = load_rows(CLASSIFIED_PATH)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["classification"] != TARGET_CLASSIFICATION:
            continue
        key = (row["local_code"], row["report_year"])
        grouped[key].append(row)

    for local_code, report_year in TARGET_REPORTS:
        key = (local_code, report_year)
        if key not in grouped:
            continue

        target_rows = sorted(grouped[key], key=lambda item: item["field_name_english"])
        field_lines = [
            f"- {row['field_name_english']} | {row['field_name_chinese']}"
            for row in target_rows
        ]
        source_path = OCR_DIR / f"{local_code}_{report_year}_annual_report_windows_ocr_normalized.txt"
        source_text = source_path.read_text(encoding="utf-8", errors="ignore")
        prompt = (
            INSTRUCTION
            + "\n".join(field_lines)
            + "\n===== TARGET FIELDS END =====\n"
            + f"FILE={source_path.name}\n"
            + f"REPORT_YEAR={report_year}\n"
            + "===== OCR TEXT START =====\n"
            + source_text
            + "\n===== OCR TEXT END =====\n"
        )
        out_path = PROMPT_DIR / f"{local_code}_{report_year}_fullread_prompt.txt"
        out_path.write_text(prompt, encoding="utf-8")
        print(out_path)


if __name__ == "__main__":
    main()
