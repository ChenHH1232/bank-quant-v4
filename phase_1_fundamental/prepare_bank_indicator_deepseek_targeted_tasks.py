import csv
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CLASSIFIED_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_missing_classified.csv"
CANDIDATE_QUEUE_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_candidate_queue.csv"
PROMPT_DIR = SCRIPT_DIR / "deepseek_bank_indicator_targeted" / "prompts"

TARGET_CLASSIFICATION = "field_found_in_ocr_full_text_needs_model_or_manual_review"
TARGET_REPORTS = [
    ("601009_XSHG", "2024"),
    ("601009_XSHG", "2025"),
    ("600036_XSHG", "2024"),
]

INSTRUCTION = """You are reviewing OCR-derived candidate snippets from one Chinese bank annual report.

Task:
Extract only the current-year values for the listed fields.

Rules:
- Use only the supplied candidate snippets.
- If the current-year value is clear, return it.
- If the field is present but the value is not reliable because OCR merged rows badly, return NOT_RECOVERABLE.
- If the supplied snippets do not really contain this field, return NOT_FOUND.
- Do not guess.
- Output only the final table. Do not add explanation.

Output format:
field_name_english|field_name_chinese|value|unit_or_percent|value_scope|confidence|evidence_excerpt
"""


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def local_code_from_source_file(source_file: str) -> str:
    stem = source_file.replace("_annual_report.pdf", "")
    parts = stem.split("_")
    return "_".join(parts[:2])


def main() -> None:
    classified_rows = load_rows(CLASSIFIED_PATH)
    candidate_rows = load_rows(CANDIDATE_QUEUE_PATH)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)

    candidate_lookup: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in candidate_rows:
        local_code = local_code_from_source_file(row["source_file"])
        key = (local_code, row["report_year"], row["field_name_english"])
        candidate_lookup[key] = row

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in classified_rows:
        if row["classification"] != TARGET_CLASSIFICATION:
            continue
        key = (row["local_code"], row["report_year"])
        grouped[key].append(row)

    for local_code, report_year in TARGET_REPORTS:
        key = (local_code, report_year)
        if key not in grouped:
            continue

        field_blocks: list[str] = []
        for row in sorted(grouped[key], key=lambda item: item["field_name_english"]):
            candidate = candidate_lookup.get((local_code, report_year, row["field_name_english"]))
            if not candidate:
                continue
            field_blocks.append(
                "\n".join(
                    [
                        f"FIELD={row['field_name_english']}",
                        f"CHINESE={row['field_name_chinese']}",
                        f"SCOPE={candidate['value_scope']}",
                        f"REFERENCE={candidate['raw_snippet_reference']}",
                        f"SNIPPET={candidate['raw_snippet_text']}",
                    ]
                )
            )

        if not field_blocks:
            continue

        prompt = (
            INSTRUCTION
            + "\n"
            + f"REPORT={local_code}_{report_year}\n"
            + f"CURRENT_YEAR={report_year}\n\n"
            + "\n\n-----\n\n".join(field_blocks)
            + "\n"
        )
        out_path = PROMPT_DIR / f"{local_code}_{report_year}_targeted_prompt.txt"
        out_path.write_text(prompt, encoding="utf-8")
        print(out_path)


if __name__ == "__main__":
    main()
