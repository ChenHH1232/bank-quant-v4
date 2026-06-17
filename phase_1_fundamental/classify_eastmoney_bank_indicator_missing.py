import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
MISSING_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_extraction_missing.csv"
ALIASES_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_aliases.json"
EXTRACTED_DIR = SCRIPT_DIR / "eastmoney_reports" / "extracted_text"
OCR_DIR = SCRIPT_DIR / "eastmoney_reports" / "ocr_text"
OUTPUT_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_missing_classified.csv"
SUMMARY_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_missing_classified_summary_2026-06-17.md"


def load_alias_map(path: Path) -> dict[str, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        item["field_name_english"]: sorted(set(item["aliases"] + [item["field_name_chinese"]]), key=len, reverse=True)
        for item in payload["standard_fields"]
    }


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def local_code_from_source_file(source_file: str) -> str:
    stem = source_file.replace("_annual_report.pdf", "")
    parts = stem.split("_")
    return "_".join(parts[:2])


def resolve_full_text_path(local_code: str, report_year: str, extraction_method: str) -> Path:
    if extraction_method == "windows_ocr_normalized":
        return OCR_DIR / f"{local_code}_{report_year}_annual_report_windows_ocr_normalized.txt"
    return EXTRACTED_DIR / f"{local_code}_{report_year}_annual_report.txt"


def classify_row(row: dict[str, str], alias_map: dict[str, list[str]], full_text_cache: dict[tuple[str, str, str], str]) -> dict[str, str]:
    field = row["field_name_english"]
    aliases = alias_map.get(field, [row["field_name_chinese"]])
    local_code = local_code_from_source_file(row["source_file"])
    cache_key = (local_code, row["report_year"], row["extraction_method"])
    if cache_key not in full_text_cache:
        full_path = resolve_full_text_path(local_code, row["report_year"], row["extraction_method"])
        full_text_cache[cache_key] = full_path.read_text(encoding="utf-8", errors="ignore") if full_path.exists() else ""
    full_text = full_text_cache[cache_key]

    matched_aliases = [alias for alias in aliases if alias in full_text]
    alias_hit_count = sum(full_text.count(alias) for alias in matched_aliases)

    if row["reason"] == "fallback_source_required":
        classification = "incomplete_candidate_coverage_fallback_source"
        detail = "Candidate coverage for this report was incomplete; use backup source before value extraction."
    elif alias_hit_count == 0:
        classification = "field_not_found_in_full_text"
        detail = "No standard alias was found in the current full-text source."
    elif row["extraction_method"] == "windows_ocr_normalized":
        classification = "field_found_in_ocr_full_text_needs_model_or_manual_review"
        detail = "Field alias exists in OCR full text, but numeric extraction likely needs long-context reconstruction."
    else:
        classification = "field_found_in_full_text_needs_rule_upgrade"
        detail = "Field alias exists in full text, but current rule-based numeric extraction did not recover the value."

    return {
        **row,
        "local_code": local_code,
        "alias_hit_count": str(alias_hit_count),
        "matched_alias_preview": " | ".join(matched_aliases[:5]),
        "classification": classification,
        "classification_detail": detail,
    }


def main() -> None:
    rows = load_rows(MISSING_PATH)
    alias_map = load_alias_map(ALIASES_PATH)
    full_text_cache: dict[tuple[str, str, str], str] = {}
    classified_rows = [classify_row(row, alias_map, full_text_cache) for row in rows]

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = [
            "code",
            "bank_name",
            "local_code",
            "report_year",
            "field_name_english",
            "field_name_chinese",
            "source_file",
            "reason",
            "detail",
            "raw_snippet_reference",
            "extraction_method",
            "alias_hit_count",
            "matched_alias_preview",
            "classification",
            "classification_detail",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)

    class_counter = Counter(row["classification"] for row in classified_rows)
    by_report = defaultdict(int)
    for row in classified_rows:
        if row["classification"] == "field_found_in_ocr_full_text_needs_model_or_manual_review":
            by_report[(row["local_code"], row["report_year"])] += 1

    top_reports = sorted(by_report.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:10]
    lines = [
        "# Eastmoney 银行专项指标缺失分类（2026-06-17）",
        "",
        f"- 总缺失条目：`{len(classified_rows)}`",
        "",
        "分类统计：",
    ]
    for key, value in sorted(class_counter.items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "最适合交给 DeepSeek 长文阅读的报告：",
        ]
    )
    for (local_code, report_year), value in top_reports:
        lines.append(f"- `{local_code}` `{report_year}`: `{value}` 条")
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
