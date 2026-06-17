import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CANDIDATE_QUEUE_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_candidate_queue.csv"
COVERAGE_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_candidate_coverage.csv"
ALIASES_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_aliases.json"
EXTRACTED_DIR = SCRIPT_DIR / "eastmoney_reports" / "extracted_text"
OCR_DIR = SCRIPT_DIR / "eastmoney_reports" / "ocr_text"
OUTPUT_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_extracted_values.csv"
MISSING_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_extraction_missing.csv"
SUMMARY_PATH = SCRIPT_DIR / "eastmoney_bank_indicator_extraction_summary_2026-06-17.md"

NUMBER_RE = re.compile(r"(?<![\dA-Za-z])-?\d[\d,]*(?:\.\d+)?")
YEAR_VALUES = {"2022", "2023", "2024", "2025", "2026"}
SKIP_PREFIXES = ("<", ">", "≤", "≥", "=")


@dataclass
class ExtractionResult:
    value: str | None
    unit_or_percent: str
    confidence: str
    review_status: str
    review_note: str


def load_alias_map(path: Path) -> dict[str, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        item["field_name_english"]: item["aliases"] + [item["field_name_chinese"]]
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


def normalize_text(text: str) -> str:
    normalized = text.replace("\u3000", " ").replace("％", "%")
    normalized = normalized.replace("，", ",").replace("：", ":").replace("（", "(").replace("）", ")")
    normalized = normalized.replace("。", ".").replace("；", ";")
    return normalized


def clean_row_segment(text: str) -> str:
    cleaned = re.sub(r"\(注\d+\)", " ", text)
    cleaned = re.sub(r"注\d+", " ", cleaned)
    cleaned = re.sub(r"(?:>=|<=|≥|≤|>|<)\s*\d+(?:\.\d+)?", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def score_anchor(snippet: str, idx: int, alias: str) -> int:
    prefix = snippet[max(0, idx - 4):idx]
    tail = snippet[idx + len(alias):idx + len(alias) + 120]
    score = 0
    score += len(NUMBER_RE.findall(tail)) * 5
    if re.search(r"(?:>=|<=|≥|≤|>|<)\s*\d", tail):
        score += 15
    if "%" in tail or "单位" in tail:
        score += 4
    if idx == 0 or prefix.endswith((" ", "目 ", "日 ", "率 ", "）", ")", "]", "】")):
        score += 6
    if prefix and re.search(r"[\u4e00-\u9fffA-Za-z0-9]$", prefix):
        score -= 10
    if any(bad in tail[:24] for bad in ["指标", "口径", "根据", "注：", "注:"]):
        score -= 12
    return score


def choose_anchor(snippet: str, aliases: list[str]) -> tuple[int, str] | None:
    best: tuple[int, str, int] | None = None
    for alias in aliases:
        start = 0
        while True:
            idx = snippet.find(alias, start)
            if idx < 0:
                break
            score = score_anchor(snippet, idx, alias)
            if best is None or score > best[2] or (score == best[2] and idx < best[0]):
                best = (idx, alias, score)
            start = idx + len(alias)
    if best is None:
        return None
    return best[0], best[1]


def token_is_year(token: str) -> bool:
    clean = token.replace(",", "")
    return clean in YEAR_VALUES


def looks_like_threshold(snippet: str, start: int) -> bool:
    prefix = snippet[max(0, start - 5):start].strip()
    return any(prefix.endswith(symbol) for symbol in SKIP_PREFIXES)


def build_row_segment(snippet: str, anchor: str, all_aliases: list[str]) -> str:
    normalized = normalize_text(snippet)
    anchor_info = choose_anchor(normalized, [anchor])
    if not anchor_info:
        return normalized

    anchor_start = anchor_info[0]
    search_start = anchor_start + len(anchor)
    next_positions: list[int] = []
    for alias in all_aliases:
        idx = normalized.find(alias, search_start)
        if idx >= 0:
            next_positions.append(idx)

    end = min(next_positions) if next_positions else min(len(normalized), search_start + 320)
    return normalized[anchor_start:end]


def find_numeric_tokens(text: str) -> list[tuple[str, int, int]]:
    return [(match.group(0).replace(",", ""), match.start(), match.end()) for match in NUMBER_RE.finditer(text)]


def find_first_valid_numeric(text: str) -> str | None:
    for token, start, _ in find_numeric_tokens(text):
        if token_is_year(token):
            continue
        if looks_like_threshold(text, start):
            continue
        return token
    return None


def iter_keyword_occurrences(text: str, keyword: str) -> list[int]:
    positions: list[int] = []
    start = 0
    while True:
        idx = text.find(keyword, start)
        if idx < 0:
            break
        positions.append(idx)
        start = idx + len(keyword)
    return positions


def score_keyword_window(window: str, keyword: str) -> int:
    score = 0
    if "%" in window[:80]:
        score += 20
    if "期末" in window[:80] or "2024年" in window[:80] or "2025年" in window[:80]:
        score += 10
    if "项目" in window[:80] or "比率" in window[:80] or "指标" in window[:80]:
        score += 8
    if "注：" in window[:80] or "说明" in window[:80]:
        score -= 12
    if keyword.endswith("率") and f"{keyword}（%）" in window[:40]:
        score += 15
    return score


def extract_value_after_keyword(text: str, keyword: str, limit: int = 160) -> str | None:
    best: tuple[int, str] | None = None
    for idx in iter_keyword_occurrences(text, keyword):
        tail = text[idx + len(keyword):idx + len(keyword) + limit]
        value = find_first_valid_numeric(tail)
        if value is None:
            continue
        score = score_keyword_window(tail, keyword)
        score += idx // 200
        if best is None or score > best[0]:
            best = (score, value)
    return best[1] if best else None


def extract_value_from_same_line(text: str, keyword: str) -> str | None:
    best: tuple[int, str] | None = None
    for idx in iter_keyword_occurrences(text, keyword):
        tail = text[idx + len(keyword):]
        line = tail.splitlines()[0] if "\n" in tail else tail[:200]
        value = find_first_valid_numeric(line)
        if value is None:
            continue
        score = score_keyword_window(line, keyword)
        score += idx // 200
        if best is None or score > best[0]:
            best = (score, value)
    return best[1] if best else None


def extract_value_after_filtered_keyword(
    text: str,
    keyword: str,
    limit: int = 160,
    disallow_prev_chars: set[str] | None = None,
) -> str | None:
    best: tuple[int, str] | None = None
    for idx in iter_keyword_occurrences(text, keyword):
        if disallow_prev_chars and idx > 0 and text[idx - 1] in disallow_prev_chars:
            continue
        tail = text[idx + len(keyword):idx + len(keyword) + limit]
        value = find_first_valid_numeric(tail)
        if value is None:
            continue
        score = score_keyword_window(tail, keyword)
        score += idx // 200
        if best is None or score > best[0]:
            best = (score, value)
    return best[1] if best else None


def looks_like_ratio_value(token: str) -> bool:
    if "." not in token:
        return False
    try:
        value = float(token)
    except ValueError:
        return False
    return 0 <= value <= 1000


def extract_last_ratio_value_after_keyword(
    text: str,
    keyword: str,
    limit: int = 200,
    disallow_prev_chars: set[str] | None = None,
) -> str | None:
    matches: list[str] = []
    for idx in iter_keyword_occurrences(text, keyword):
        if disallow_prev_chars and idx > 0 and text[idx - 1] in disallow_prev_chars:
            continue
        tail = text[idx + len(keyword):idx + len(keyword) + limit]
        for token, start, _ in find_numeric_tokens(tail):
            if token_is_year(token):
                continue
            if looks_like_threshold(tail, start):
                continue
            if looks_like_ratio_value(token):
                matches.append(token)
                break
    return matches[-1] if matches else None


def extract_first_value_after_label(text: str, label: str, limit: int = 120) -> float | None:
    idx = text.find(label)
    if idx < 0:
        return None
    tail = text[idx + len(label):idx + len(label) + limit]
    for token, start, _ in find_numeric_tokens(tail):
        if token_is_year(token):
            continue
        if looks_like_threshold(tail, start):
            continue
        try:
            return float(token)
        except ValueError:
            return None
    return None


def format_ratio_value(value: float) -> str:
    return f"{value:.2f}"


def value_looks_suspicious(field: str, value: str | None) -> bool:
    if value is None:
        return True
    ratio_fields = {
        "capital_adequacy_ratio",
        "tier_1_capital_adequacy_ratio",
        "core_tier_1_capital_adequacy_ratio",
        "liquidity_ratio",
        "liquidity_matching_ratio",
        "liquidity_coverage_ratio",
        "single_largest_customer_loan_ratio",
        "top_ten_customer_loan_ratio",
        "single_group_credit_concentration_ratio",
        "provision_coverage_ratio",
        "provision_to_loan_ratio",
        "non_performing_loan_ratio",
    }
    if field in ratio_fields and "." not in value:
        return True
    return False


def extract_field_specific_value(field: str, snippet: str) -> str | None:
    regex_map = {
        "tier_1_capital_adequacy_ratio": [
            r"(?s)一[级級][资資]本充足率(?:\(\d+\)|（\d+）)?[\s\S]{0,20}?([0-9]+\.[0-9]+)",
        ],
        "core_tier_1_capital_adequacy_ratio": [
            r"(?s)核心一[级級][资資]本充足率(?:\(\d+\)|（\d+）)?[\s\S]{0,20}?([0-9]+\.[0-9]+)",
        ],
        "capital_adequacy_ratio": [
            r"(?s)资本充足率(?:\(\d+\)|（\d+）)?[\s\S]{0,20}?([0-9]+\.[0-9]+)",
            r"(?s)資本充足率(?:\(\d+\)|（\d+）)?[\s\S]{0,20}?([0-9]+\.[0-9]+)",
        ],
        "liquidity_ratio": [
            r"(?s)流动性比率\d*[\s\S]{0,40}?人民币[\s\S]{0,10}?[≥<=]+\s*25[\s\S]{0,10}?([0-9]+(?:\.[0-9]+)?)",
            r"(?s)流動性比率\d*[\s\S]{0,40}?人民幣[\s\S]{0,10}?[≥<=]+\s*25[\s\S]{0,10}?([0-9]+(?:\.[0-9]+)?)",
            r"(?s)流动性比例[\s\S]{0,40}?人民币[\s\S]{0,10}?[≥<=]+\s*25[\s\S]{0,10}?([0-9]+(?:\.[0-9]+)?)",
            r"(?s)流動性比例[\s\S]{0,40}?人民幣[\s\S]{0,10}?[≥<=]+\s*25[\s\S]{0,10}?([0-9]+(?:\.[0-9]+)?)",
        ],
        "single_largest_customer_loan_ratio": [
            r"(?s)最大单一客户贷款比例\d*[\s\S]{0,20}?(?:[≥<=]+\s*10[\s\S]{0,10}?)?([0-9]+\.[0-9]+)",
            r"(?s)最大單一客戶貸款比例[\s\S]{0,20}?([0-9]+\.[0-9]+)",
            r"(?s)单一最大客户贷款比例[\s\S]{0,20}?([0-9]+\.[0-9]+)",
            r"(?s)單一最大客戶貸款比例[\s\S]{0,20}?([0-9]+\.[0-9]+)",
        ],
        "top_ten_customer_loan_ratio": [
            r"(?s)最大十家客户贷款比例\d*[\s\S]{0,20}?([0-9]+\.[0-9]+)",
            r"(?s)最大十家客戶貸款比例[\s\S]{0,20}?([0-9]+\.[0-9]+)",
        ],
        "liquidity_coverage_ratio": [
            r"(?s)流[动動][\s\S]{0,3}性[\s\S]{0,6}[覆覆蓋盖]率日均值([0-9]+(?:\.[0-9]+)?)%",
            r"(?s)流动性覆盖率日均值([0-9]+(?:\.[0-9]+)?)%",
            r"(?s)流動性覆蓋率日均值([0-9]+(?:\.[0-9]+)?)%",
            r"(?s)流[动動][\s\S]{0,3}性[\s\S]{0,6}[覆蓋盖]率[\s\S]{0,20}?([0-9]+\.[0-9]+)",
            r"(?s)流动性覆盖率[\s\S]{0,20}?([0-9]+\.[0-9]+)",
            r"(?s)流動性覆蓋率[\s\S]{0,20}?([0-9]+\.[0-9]+)",
        ],
    }
    direct_keyword_map = {
        "non_performing_loan_ratio": ["不良贷款率"],
        "provision_coverage_ratio": ["拨备覆盖率"],
        "provision_to_loan_ratio": ["贷款拨备率", "拨贷比"],
        "liquidity_matching_ratio": ["流动性匹配率", "流動性匹配率"],
        "single_largest_customer_loan_ratio": [
            "单一最大客户贷款占资本净额比率",
            "單一最大客戶貸款占資本淨額比率",
            "单一客户贷款集中度",
            "單一客戶貸款集中度",
            "最大单一客户贷款比例",
            "最大單一客戶貸款比例",
            "单一最大客户贷款比例",
            "單一最大客戶貸款比例",
        ],
        "top_ten_customer_loan_ratio": [
            "最大十家客户贷款集中度",
            "最大十家客戶貸款集中度",
            "最大十家客户贷款占资本净额比率",
            "最大十家客戶貸款占資本淨額比率",
            "最大十家客户贷款比例",
            "最大十家客戶貸款比例",
        ],
        "single_group_credit_concentration_ratio": ["单一集团客户授信集中度", "单一集团客户授信集中度比率"],
        "capital_adequacy_ratio": ["资本充足率", "資本充足率"],
        "tier_1_capital_adequacy_ratio": ["一级资本充足率", "一級資本充足率"],
        "core_tier_1_capital_adequacy_ratio": ["核心一级资本充足率", "核心一級資本充足率"],
    }

    if field == "liquidity_coverage_ratio":
        day_avg_match = re.search(r"(?s)第.{0,8}?季度流[动動][\s\S]{0,3}性.{0,4}率日均值([0-9]+\.[0-9]+)%", snippet)
        if day_avg_match:
            return day_avg_match.group(1)

    for pattern in regex_map.get(field, []):
        matches = list(re.finditer(pattern, snippet))
        if matches:
            return matches[-1].group(1)

    if field == "capital_adequacy_ratio":
        for keyword in ["资本充足率（%）", "资本充足率"]:
            value = extract_last_ratio_value_after_keyword(snippet, keyword, disallow_prev_chars=set("一级核心"))
            if value and "." in value:
                return value
            value = extract_value_after_filtered_keyword(snippet, keyword, disallow_prev_chars=set("一级核心"))
            if value and "." in value:
                return value
        capital_net = extract_first_value_after_label(snippet, "资本净额")
        rwa = extract_first_value_after_label(snippet, "风险加权资产")
        if capital_net and rwa:
            return format_ratio_value(capital_net / rwa * 100)

    if field == "tier_1_capital_adequacy_ratio":
        for keyword in ["一级资本充足率（%）", "一级资本充足率"]:
            value = extract_value_after_filtered_keyword(snippet, keyword, disallow_prev_chars={"心"})
            if value:
                return value
        tier1_net = extract_first_value_after_label(snippet, "一级资本净额")
        rwa = extract_first_value_after_label(snippet, "风险加权资产")
        if tier1_net and rwa:
            return format_ratio_value(tier1_net / rwa * 100)

    if field == "core_tier_1_capital_adequacy_ratio":
        for keyword in ["核心一级资本充足率（%）", "核心一级资本充足率"]:
            value = extract_value_after_filtered_keyword(snippet, keyword)
            if value:
                return value
        core_tier1_net = extract_first_value_after_label(snippet, "核心一级资本净额")
        rwa = extract_first_value_after_label(snippet, "风险加权资产")
        if core_tier1_net and rwa:
            return format_ratio_value(core_tier1_net / rwa * 100)

    if field == "provision_coverage_ratio":
        for keyword in ["拨备覆盖率"]:
            value = extract_last_ratio_value_after_keyword(snippet, keyword)
            if value:
                return value
            value = extract_value_after_filtered_keyword(snippet, keyword)
            if value:
                return value

    if field == "provision_to_loan_ratio":
        for keyword in ["贷款拨备率", "拨贷比"]:
            value = extract_value_after_filtered_keyword(snippet, keyword)
            if value:
                return value

    if field == "liquidity_coverage_ratio":
        for keyword in ["流动性覆盖率（%）", "流动性覆盖率", "流動性覆蓋率", "流動性覆蓋比率"]:
            value = extract_value_after_keyword(snippet, keyword)
            if value:
                return value
        return None

    if field == "liquidity_ratio":
        for keyword in [
            "流动性比例（本外币）",
            "流动性比例（人民币）",
            "流动性比例（外币）",
            "流动性比例",
            "流動性比例",
            "流动性比率",
            "流動性比率",
        ]:
            value = extract_value_after_keyword(snippet, keyword)
            if value:
                return value
        return None

    for keyword in direct_keyword_map.get(field, []):
        value = extract_value_from_same_line(snippet, keyword)
        if value:
            return value
        value = extract_value_after_keyword(snippet, keyword)
        if value:
            return value

    return None


def extract_first_numeric_after_anchor(snippet: str, anchor: str, all_aliases: list[str]) -> ExtractionResult:
    row_segment = clean_row_segment(build_row_segment(snippet, anchor, all_aliases))
    anchor_info = choose_anchor(row_segment, [anchor])
    start = anchor_info[0] + len(anchor) if anchor_info else 0
    tail = row_segment[start:start + 240]

    for match in NUMBER_RE.finditer(tail):
        token = match.group(0)
        if token_is_year(token):
            continue
        if looks_like_threshold(tail, match.start()):
            continue
        value = token.replace(",", "")
        return ExtractionResult(
            value=value,
            unit_or_percent="%",
            confidence="medium",
            review_status="needs_check",
            review_note="Auto-extracted first numeric token from the isolated field row; manual review still recommended.",
        )

    return ExtractionResult(
        value=None,
        unit_or_percent="%",
        confidence="low",
        review_status="needs_check",
        review_note="No numeric token found after the matched field anchor.",
    )


def extract_value(
    row: dict[str, str],
    aliases: list[str],
    all_aliases: list[str],
    full_text_cache: dict[tuple[str, str, str], str],
) -> ExtractionResult:
    snippet = row["raw_snippet_text"]
    normalized = normalize_text(snippet)
    anchor_info = choose_anchor(normalized, aliases)
    field = row["field_name_english"]
    local_code = local_code_from_source_file(row["source_file"])
    cache_key = (local_code, row["report_year"], row["extraction_method"])
    if cache_key not in full_text_cache:
        full_path = resolve_full_text_path(local_code, row["report_year"], row["extraction_method"])
        full_text_cache[cache_key] = full_path.read_text(encoding="utf-8", errors="ignore") if full_path.exists() else ""
    full_text = normalize_text(full_text_cache[cache_key])

    result: ExtractionResult | None = None
    field_specific_value = extract_field_specific_value(field, normalized)
    if field_specific_value is not None:
        result = ExtractionResult(
            value=field_specific_value,
            unit_or_percent="%",
            confidence="medium",
            review_status="needs_check",
            review_note="Auto-extracted using field-specific keyword proximity rules; manual review still recommended.",
        )
    elif anchor_info:
        _, anchor = anchor_info
        result = extract_first_numeric_after_anchor(normalized, anchor, all_aliases)

    if result is None or value_looks_suspicious(field, result.value):
        full_text_value = extract_field_specific_value(field, full_text)
        if full_text_value is not None and not value_looks_suspicious(field, full_text_value):
            return ExtractionResult(
                value=full_text_value,
                unit_or_percent="%",
                confidence="medium",
                review_status="needs_check",
                review_note="Auto-extracted from full annual-report text after candidate snippet did not yield a valid value; manual review still recommended.",
            )

    if result is None:
        return ExtractionResult(
            value=None,
            unit_or_percent="%",
            confidence="low",
            review_status="needs_check",
            review_note="No alias anchor found in candidate snippet.",
        )

    if result.value is None:
        return result

    if field == "liquidity_coverage_ratio" and result.value == "1":
        return ExtractionResult(
            value=None,
            unit_or_percent="%",
            confidence="low",
            review_status="needs_check",
            review_note="Only a suspicious integer token was found for liquidity coverage ratio; no reliable decimal ratio was recovered from snippet or full text.",
        )

    threshold = (row.get("standard_threshold") or "").strip()
    if threshold and result.value == threshold.lstrip("<>≤≥=") and anchor_info:
        _, anchor = anchor_info
        second_pass_tail = clean_row_segment(build_row_segment(normalized, anchor, all_aliases))
        second_pass_tail = second_pass_tail[second_pass_tail.rfind(anchor) + len(anchor):]
        seen = False
        for match in NUMBER_RE.finditer(second_pass_tail):
            token = match.group(0).replace(",", "")
            if token_is_year(token):
                continue
            if not seen and token == result.value:
                seen = True
                continue
            if looks_like_threshold(second_pass_tail, match.start()):
                continue
            result.value = token
            result.review_note = "Auto-extracted value after skipping threshold token near field anchor; manual review still recommended."
            break

    if field in {
        "capital_adequacy_ratio",
        "tier_1_capital_adequacy_ratio",
        "core_tier_1_capital_adequacy_ratio",
        "liquidity_coverage_ratio",
        "liquidity_matching_ratio",
        "liquidity_ratio",
        "single_largest_customer_loan_ratio",
        "top_ten_customer_loan_ratio",
        "single_group_credit_concentration_ratio",
        "provision_coverage_ratio",
        "provision_to_loan_ratio",
        "non_performing_loan_ratio",
    }:
        result.unit_or_percent = "%"

    if row["extraction_method"] == "windows_ocr_normalized":
        result.confidence = "medium" if result.value is not None else "low"
        result.review_note = f"{result.review_note} Source snippet came from Windows OCR normalization."

    return result


def load_full_coverage_keys(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for row in rows:
        if row["matched_field_count"] == row["total_field_count"]:
            keys.add((row["local_code"], row["report_year"]))
    return keys


def main() -> None:
    alias_map = load_alias_map(ALIASES_PATH)
    all_aliases = sorted({alias for aliases in alias_map.values() for alias in aliases}, key=len, reverse=True)
    coverage_rows = load_rows(COVERAGE_PATH)
    candidate_rows = load_rows(CANDIDATE_QUEUE_PATH)
    full_coverage_keys = load_full_coverage_keys(coverage_rows)
    full_text_cache: dict[tuple[str, str, str], str] = {}

    extracted_rows: list[dict[str, str]] = []
    missing_rows: list[dict[str, str]] = []

    for row in candidate_rows:
        local_code = row["source_file"].replace("_annual_report.pdf", "")
        local_code = "_".join(local_code.split("_")[:2])
        key = (local_code, row["report_year"])
        is_full_coverage = key in full_coverage_keys

        if not is_full_coverage:
            missing_rows.append(
                {
                    "code": row["code"],
                    "bank_name": row["bank_name"],
                    "report_year": row["report_year"],
                    "field_name_english": row["field_name_english"],
                    "field_name_chinese": row["field_name_chinese"],
                    "source_file": row["source_file"],
                    "reason": "fallback_source_required",
                    "detail": "This report did not achieve full candidate coverage and should be completed from a backup source.",
                    "raw_snippet_reference": row["raw_snippet_reference"],
                    "extraction_method": row["extraction_method"],
                }
            )
            continue

        aliases = alias_map.get(row["field_name_english"], [row["field_name_chinese"]])
        result = extract_value(row, aliases, all_aliases, full_text_cache)
        if result.value is None:
            missing_rows.append(
                {
                    "code": row["code"],
                    "bank_name": row["bank_name"],
                    "report_year": row["report_year"],
                    "field_name_english": row["field_name_english"],
                    "field_name_chinese": row["field_name_chinese"],
                    "source_file": row["source_file"],
                    "reason": "numeric_value_not_found",
                    "detail": result.review_note,
                    "raw_snippet_reference": row["raw_snippet_reference"],
                    "extraction_method": row["extraction_method"],
                }
            )
            continue

        output_row = dict(row)
        output_row["value"] = result.value
        output_row["unit_or_percent"] = result.unit_or_percent
        output_row["confidence"] = result.confidence
        output_row["review_status"] = result.review_status
        output_row["review_note"] = result.review_note
        extracted_rows.append(output_row)

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
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
            "value",
            "unit_or_percent",
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
        writer.writerows(extracted_rows)

    with MISSING_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = [
            "code",
            "bank_name",
            "report_year",
            "field_name_english",
            "field_name_chinese",
            "source_file",
            "reason",
            "detail",
            "raw_snippet_reference",
            "extraction_method",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(missing_rows)

    full_report_count = len(full_coverage_keys)
    extracted_report_count = len({(row["code"], row["report_year"]) for row in extracted_rows})
    fallback_count = sum(1 for row in missing_rows if row["reason"] == "fallback_source_required")
    numeric_missing_count = sum(1 for row in missing_rows if row["reason"] == "numeric_value_not_found")
    summary = "\n".join(
        [
            "# Eastmoney 银行专项指标数值抽取进度（2026-06-17）",
            "",
            f"- 候选全覆盖报告数：`{full_report_count}`",
            f"- 已输出结构化数值行数：`{len(extracted_rows)}`",
            f"- 已覆盖报告数：`{extracted_report_count}`",
            f"- 备用源待补条目数：`{fallback_count}`",
            f"- 数值未自动识别条目数：`{numeric_missing_count}`",
            "",
            "当前规则：",
            "- 只对 `12/12` 全覆盖报告进入正式数值抽取",
            "- `601328_XSHG 2025` 整份报告单独记入备用源待补",
            "- 自动抽取结果默认标记为 `needs_check`，后续可继续用 DeepSeek 或人工批量复核",
            "",
            "输出文件：",
            f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
            f"- [{MISSING_PATH.name}]({MISSING_PATH})",
        ]
    )
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    print(f"extracted_rows={len(extracted_rows)}")
    print(f"missing_rows={len(missing_rows)}")
    print(OUTPUT_PATH)
    print(MISSING_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
