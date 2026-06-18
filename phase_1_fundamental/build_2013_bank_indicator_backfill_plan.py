import csv
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
STANDARDIZED_ROOT = SCRIPT_DIR / "standardized_outputs"
OUTPUT_BANKS_PATH = SCRIPT_DIR / "bank_indicator_2013_backfill_banks.csv"
OUTPUT_FIELDS_PATH = SCRIPT_DIR / "bank_indicator_2013_backfill_fields.csv"
OUTPUT_DOWNLOAD_PS1 = SCRIPT_DIR / "run_2013_bank_indicator_backfill_download.ps1"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "bank_indicator_2013_backfill_plan.md"

CORE_BACKFILL_FIELDS = [
    ("capital_adequacy_ratio", "资本充足率", "bank_indicator__capital_adequacy_ratio"),
    ("core_level_capital_adequacy_ratio", "核心一级资本充足率", "bank_indicator__core_level_capital_adequacy_ratio"),
    ("cost_to_income_ratio", "成本收入比", "bank_indicator__cost_to_income_ratio"),
    ("deposit_loan_ratio", "存贷比", "bank_indicator__deposit_loan_ratio"),
    ("net_interest_margin", "净息差", "bank_indicator__net_interest_margin"),
    ("non_interest_income_ratio", "非利息收入占比", "bank_indicator__non_interest_income_ratio"),
    ("non_performing_loan_provision_coverage", "拨备覆盖率", "bank_indicator__non_performing_loan_provision_coverage"),
    ("Nonperforming_loan_rate", "不良贷款率", "bank_indicator__Nonperforming_loan_rate"),
]


def discover_legacy_bank_targets() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for code_dir in sorted(STANDARDIZED_ROOT.iterdir()):
        path = code_dir / "bank_indicator_standardized.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path, encoding="utf-8-sig", usecols=["code", "year_key", "pub_date"])
        years = pd.to_numeric(df["year_key"], errors="coerce").dropna().astype(int)
        if years.empty:
            continue
        min_year = int(years.min())
        max_year = int(years.max())
        has_2013 = int((years == 2013).any())
        has_2014 = int((years == 2014).any())
        if has_2013 == 0 and has_2014 == 1:
            sample_code = str(df["code"].dropna().iloc[0])
            earliest_pub = str(pd.to_datetime(df["pub_date"], errors="coerce").min().date())
            rows.append(
                {
                    "local_code": code_dir.name,
                    "code": sample_code,
                    "min_standardized_year": str(min_year),
                    "max_standardized_year": str(max_year),
                    "has_2013": str(has_2013),
                    "has_2014": str(has_2014),
                    "earliest_existing_pub_date": earliest_pub,
                    "backfill_report_year": "2013",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_fields_csv() -> None:
    rows = [
        {
            "field_name_english": english,
            "field_name_chinese": chinese,
            "panel_column": panel_column,
            "priority": "core_backfill_2013",
        }
        for english, chinese, panel_column in CORE_BACKFILL_FIELDS
    ]
    write_csv(OUTPUT_FIELDS_PATH, rows)


def write_download_script(bank_rows: list[dict[str, str]]) -> None:
    bank_args = " ".join(f'--bank-code {row["local_code"]}' for row in bank_rows)
    command = (
        "python .\\phase_1_fundamental\\download_eastmoney_annual_reports.py "
        "--start-year 2013 --end-year 2013 "
        f"{bank_args} "
        "--sleep-min 2.0 --sleep-max 4.0 --bank-sleep-min 5.0 --bank-sleep-max 9.0"
    ).strip()
    OUTPUT_DOWNLOAD_PS1.write_text(command + "\n", encoding="utf-8")


def write_summary(bank_rows: list[dict[str, str]]) -> None:
    lines = [
        "# 2013 Bank Indicator Backfill Plan",
        "",
        "Goal:",
        "- backfill the missing `2013` annual bank-indicator layer",
        "- unlock `2014q1` to `2014q3` valid-quarter eligibility where possible",
        "",
        "Why this exists:",
        "- current standardized `bank_indicator` coverage for legacy listed banks starts at `2014`",
        "- the valid-data rule requires at least one prior annual bank-indicator snapshot",
        "- therefore `2014q1` to `2014q3` currently fail with `no_prior_annual_bank_indicator`",
        "",
        f"- Legacy banks needing 2013 backfill: `{len(bank_rows)}`",
        "",
        "Core fields to backfill first:",
    ]
    for english, chinese, panel_column in CORE_BACKFILL_FIELDS:
        lines.append(f"- `{english}` / `{chinese}` -> `{panel_column}`")

    lines.extend(
        [
            "",
            "Outputs:",
            f"- [bank_indicator_2013_backfill_banks.csv]({OUTPUT_BANKS_PATH})",
            f"- [bank_indicator_2013_backfill_fields.csv]({OUTPUT_FIELDS_PATH})",
            f"- [run_2013_bank_indicator_backfill_download.ps1]({OUTPUT_DOWNLOAD_PS1})",
            "",
            "Suggested next step:",
            "- download the 2013 Eastmoney annual reports for the legacy-bank subset",
            "- then build a 2013-only candidate queue and extraction pass for the eight core fields",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    bank_rows = discover_legacy_bank_targets()
    write_csv(OUTPUT_BANKS_PATH, bank_rows)
    write_fields_csv()
    write_download_script(bank_rows)
    write_summary(bank_rows)
    print(OUTPUT_BANKS_PATH)
    print(OUTPUT_FIELDS_PATH)
    print(OUTPUT_DOWNLOAD_PS1)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
