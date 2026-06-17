import csv
import json
import re
from pathlib import Path


PAGE_RE = re.compile(r"===== PAGE (\d{4}) =====")
SEPARATOR = "\n\n-----\n\n"


def load_aliases(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["standard_fields"]


def load_manifest(path: Path) -> dict[tuple[str, int], dict]:
    rows: dict[tuple[str, int], dict] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            local_code = (row.get("local_code") or "").strip()
            report_year = int((row.get("report_year") or "0").strip() or 0)
            rows[(local_code, report_year)] = row
    return rows


def title_to_bank_name(title: str, local_code: str) -> str:
    if ":" in title:
        return title.split(":", 1)[0].strip()
    return local_code


def split_snippets(text: str) -> list[str]:
    if not text.strip() or text.strip() == "NO_HITS":
        return []
    return [part.strip() for part in text.split(SEPARATOR) if part.strip()]


def score_snippet(snippet: str, aliases: list[str]) -> int:
    score = 0
    first_line = snippet.splitlines()[0] if snippet.splitlines() else ""

    for alias in aliases:
        if alias in snippet:
            score += 10 + len(alias)
            start = 0
            while True:
                idx = snippet.find(alias, start)
                if idx < 0:
                    break
                tail = snippet[idx + len(alias): idx + len(alias) + 120]
                numeric_hits = re.findall(r"\d[\d,]*(?:\.\d+)?", tail)
                score += min(len(numeric_hits), 4) * 6
                if "注：" in tail[:20] or "注:" in tail[:20]:
                    score -= 12
                if "根据经审计的合并财务报表数据计算" in tail[:80]:
                    score -= 10
                if "集中度、" in tail[:40] or "比率、" in tail[:40]:
                    score -= 8
                start = idx + len(alias)
        if first_line == f"[{alias}]":
            score += 30
        elif alias in first_line:
            score += 18

    if "单位：" in snippet or "单位:" in snippet:
        score += 4
    if "项目" in snippet:
        score += 3
    if (
        "2024年12月31日" in snippet
        or "2025年12月31日" in snippet
        or "2024 年12 月31 日" in snippet
        or "2025 年12 月31 日" in snippet
    ):
        score += 4
    if "期末比率" in snippet or "期末 2024" in snippet or "期末 2025" in snippet:
        score += 5

    if "注：" in snippet[:200] or "注:" in snippet[:200]:
        score -= 10
    if "根据经审计的合并财务报表数据计算" in snippet:
        score -= 6
    if "董事会" in snippet and "建议" in snippet:
        score -= 8

    return score


def choose_best_snippet(snippets: list[tuple[int, str]], aliases: list[str]) -> tuple[int, str] | None:
    best: tuple[int, int, str] | None = None
    for idx, snippet in snippets:
        score = score_snippet(snippet, aliases)
        if best is None or score > best[0]:
            best = (score, idx, snippet)
    if best is None or best[0] <= 0:
        return None
    return best[1], best[2]


def extract_page(snippet: str) -> str:
    match = PAGE_RE.search(snippet)
    if not match:
        return ""
    return str(int(match.group(1)))


def discover_best_snippet_file(local_code: str, report_year: int, extracted_dir: Path, ocr_dir: Path) -> tuple[str, Path] | None:
    normalized_name = f"{local_code}_{report_year}_annual_report_windows_ocr_normalized_bank_indicator_snippets.txt"
    normalized_path = ocr_dir / normalized_name
    if normalized_path.exists():
        return "windows_ocr_normalized", normalized_path

    text_name = f"{local_code}_{report_year}_annual_report_bank_indicator_snippets.txt"
    text_path = extracted_dir / text_name
    if text_path.exists():
        return "direct_pdf_text", text_path

    return None


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    alias_path = base_dir / "eastmoney_bank_indicator_aliases.json"
    manifest_path = base_dir / "eastmoney_reports" / "batch" / "eastmoney_annual_report_manifest.csv"
    extracted_dir = base_dir / "eastmoney_reports" / "extracted_text"
    ocr_dir = base_dir / "eastmoney_reports" / "ocr_text"
    out_csv = base_dir / "eastmoney_bank_indicator_candidate_queue.csv"
    out_summary = base_dir / "eastmoney_bank_indicator_candidate_coverage.csv"

    alias_fields = load_aliases(alias_path)
    manifest_rows = load_manifest(manifest_path)

    queue_rows: list[dict] = []
    summary_rows: list[dict] = []

    for (local_code, report_year), manifest_row in sorted(manifest_rows.items()):
        if (manifest_row.get("status") or "").strip() != "downloaded":
            continue

        snippet_info = discover_best_snippet_file(local_code, report_year, extracted_dir, ocr_dir)
        if not snippet_info:
            continue

        extraction_method, snippet_path = snippet_info
        snippets = split_snippets(snippet_path.read_text(encoding="utf-8", errors="ignore"))
        indexed_snippets = list(enumerate(snippets, start=1))
        matched_fields = 0

        for field in alias_fields:
            aliases = field["aliases"]
            best = choose_best_snippet(indexed_snippets, aliases)
            if not best:
                continue

            matched_fields += 1
            snippet_idx, snippet_text = best
            title = (manifest_row.get("title") or "").strip()
            bank_name = title_to_bank_name(title, local_code)
            notice_date = (manifest_row.get("notice_date") or "").strip()[:10]
            source_file = f"{local_code}_{report_year}_annual_report.pdf"
            report_date = f"{report_year}-12-31"
            page = extract_page(snippet_text)

            queue_rows.append(
                {
                    "code": local_code.replace("_XSHE", ".XSHE").replace("_XSHG", ".XSHG"),
                    "bank_name": bank_name,
                    "source_type": "eastmoney_annual_report_pdf",
                    "source_file": source_file,
                    "field_name_english": field["field_name_english"],
                    "field_name_chinese": field["field_name_chinese"],
                    "report_year": report_year,
                    "report_date": report_date,
                    "notice_date": notice_date,
                    "value_scope": field["value_scope"],
                    "standard_threshold": field["standard_threshold"],
                    "mapping_target": field["mapping_target"],
                    "source_page": page,
                    "raw_snippet_reference": f"{snippet_path.name}#snippet_{snippet_idx:04d}",
                    "raw_snippet_text": snippet_text[:1200].replace("\n", " "),
                    "extraction_method": extraction_method,
                    "review_status": "unreviewed",
                    "review_note": "Best alias-based snippet match selected for this field/report.",
                    "confidence": "medium" if extraction_method == "direct_pdf_text" else "high",
                    "note": "Candidate queue row; numeric value not yet finalized.",
                }
            )

        summary_rows.append(
            {
                "local_code": local_code,
                "report_year": report_year,
                "snippet_source": extraction_method,
                "matched_field_count": matched_fields,
                "total_field_count": len(alias_fields),
                "coverage_ratio": round(matched_fields / len(alias_fields), 4),
                "snippet_file": snippet_path.name,
            }
        )

    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "code",
            "bank_name",
            "source_type",
            "source_file",
            "field_name_english",
            "field_name_chinese",
            "report_year",
            "report_date",
            "notice_date",
            "value_scope",
            "standard_threshold",
            "mapping_target",
            "source_page",
            "raw_snippet_reference",
            "raw_snippet_text",
            "extraction_method",
            "review_status",
            "review_note",
            "confidence",
            "note",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(queue_rows)

    with out_summary.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "local_code",
            "report_year",
            "snippet_source",
            "matched_field_count",
            "total_field_count",
            "coverage_ratio",
            "snippet_file",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"candidate_rows={len(queue_rows)}")
    print(f"summary_rows={len(summary_rows)}")
    print(out_csv)
    print(out_summary)


if __name__ == "__main__":
    main()
