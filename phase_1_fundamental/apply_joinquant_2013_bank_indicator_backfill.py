from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
BACKFILL_PATH = SCRIPT_DIR / "backfill_2013_joinquant" / "joinquant_bank_indicator_2013_backfill.csv"
STANDARDIZED_ROOT = SCRIPT_DIR / "standardized_outputs"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "apply_joinquant_2013_bank_indicator_backfill.md"


def main() -> None:
    backfill_df = pd.read_csv(BACKFILL_PATH, encoding="utf-8-sig")
    applied_rows: list[dict[str, object]] = []

    for local_code, group in backfill_df.groupby("local_code"):
        standardized_path = STANDARDIZED_ROOT / local_code / "bank_indicator_standardized.csv"
        if not standardized_path.exists():
            continue

        standardized_df = pd.read_csv(standardized_path, encoding="utf-8-sig")
        code = str(group["code"].iloc[0])
        stat_date = str(pd.to_datetime(group["statDate"].iloc[0]).date())
        pub_date = str(pd.to_datetime(group["pubDate"].iloc[0]).date())
        year_key = str(pd.to_datetime(group["statDate"].iloc[0]).year)

        existing_years = set(pd.to_numeric(standardized_df["year_key"], errors="coerce").dropna().astype(int).tolist())
        if int(year_key) in existing_years:
            applied_rows.append(
                {
                    "local_code": local_code,
                    "code": code,
                    "status": "already_present",
                    "year_key": year_key,
                    "rows_added": 0,
                }
            )
            continue

        raw_row = group.iloc[0]
        candidate_fields = [
            col for col in group.columns
            if col not in {"id", "code", "pubDate", "statDate", "local_code", "requested_year"}
        ]

        new_rows: list[dict[str, object]] = []
        for field_name in candidate_fields:
            value = raw_row.get(field_name)
            missing_reason = ""
            standard_value = value
            if pd.isna(value):
                standard_value = ""
                missing_reason = "missing_raw_value"
            new_rows.append(
                {
                    "code": code,
                    "statement_family": "bank_indicator",
                    "report_period_end": stat_date,
                    "quarter_key": None,
                    "year_key": year_key,
                    "pub_date": pub_date,
                    "standard_field_name": field_name,
                    "standard_value": standard_value,
                    "source_table": "joinquant_bank_indicator_2013_backfill.csv",
                    "source_field": field_name,
                    "period_basis": "annual_direct",
                    "transformation_rule": "joinquant_2013_backfill_identity",
                    "missing_reason": missing_reason,
                }
            )

        merged_df = pd.concat([standardized_df, pd.DataFrame(new_rows)], ignore_index=True)
        merged_df = merged_df.sort_values(
            ["report_period_end", "year_key", "standard_field_name", "pub_date"],
            na_position="last",
        )
        merged_df.to_csv(standardized_path, index=False, encoding="utf-8-sig")

        applied_rows.append(
            {
                "local_code": local_code,
                "code": code,
                "status": "applied",
                "year_key": year_key,
                "rows_added": len(new_rows),
            }
        )

    summary_df = pd.DataFrame(applied_rows)
    summary_csv = SCRIPT_DIR / "apply_joinquant_2013_bank_indicator_backfill_status.csv"
    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")

    applied_count = int((summary_df["status"] == "applied").sum()) if not summary_df.empty else 0
    lines = [
        "# Apply JoinQuant 2013 Bank Indicator Backfill",
        "",
        f"- Target bank files processed: `{len(summary_df)}`",
        f"- Newly applied bank files: `{applied_count}`",
        "",
        "Outputs:",
        f"- [apply_joinquant_2013_bank_indicator_backfill_status.csv]({summary_csv})",
    ]
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(summary_csv)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
