import argparse
from pathlib import Path

import pandas as pd

from standardize_single_bank_statements import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_RAW_ROOT,
    UNIVERSE_PATH,
    SOURCE_CONFIGS,
    code_to_dir_name,
    load_listing_date,
    standardize_statement_family,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run standardized statement generation for all banks and build missingness summaries."
    )
    parser.add_argument("--raw-root", default=str(DEFAULT_RAW_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--limit", type=int, default=0, help="Optional test limit. 0 means all banks.")
    return parser


def load_universe_codes(limit: int) -> list[str]:
    universe = pd.read_csv(UNIVERSE_PATH)
    codes = universe["code"].tolist()
    if limit and limit > 0:
        codes = codes[:limit]
    return codes


def build_missingness_summary(output_root: Path, codes: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    bank_level_rows: list[dict[str, object]] = []
    missing_reason_rows: list[dict[str, object]] = []

    for code in codes:
        bank_dir = output_root / code_to_dir_name(code)
        summary_path = bank_dir / "standardization_summary.csv"
        if summary_path.exists():
            summary_df = pd.read_csv(summary_path)
            for _, row in summary_df.iterrows():
                bank_level_rows.append(
                    {
                        "code": code,
                        "statement_family": row["statement_family"],
                        "standardized_rows": row["standardized_rows"],
                        "audit_rows": row["audit_rows"],
                        "missing_rows": row["missing_rows"],
                    }
                )

        for config in SOURCE_CONFIGS:
            std_path = bank_dir / f"{config.statement_family}_standardized.csv"
            if not std_path.exists():
                continue
            df = pd.read_csv(std_path)
            reason_counts = df["missing_reason"].fillna("").value_counts()
            for reason, count in reason_counts.items():
                missing_reason_rows.append(
                    {
                        "code": code,
                        "statement_family": config.statement_family,
                        "missing_reason": reason,
                        "row_count": int(count),
                    }
                )

    return pd.DataFrame(bank_level_rows), pd.DataFrame(missing_reason_rows)


def main() -> None:
    args = build_parser().parse_args()
    raw_root = Path(args.raw_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    codes = load_universe_codes(args.limit)
    overall_rows: list[dict[str, object]] = []

    for code in codes:
        listing_date = load_listing_date(code)
        bank_dir = output_root / code_to_dir_name(code)
        bank_dir.mkdir(parents=True, exist_ok=True)
        summary_rows: list[dict[str, object]] = []

        for config in SOURCE_CONFIGS:
            standardized_df, audit_df = standardize_statement_family(
                code=code,
                config=config,
                raw_root=raw_root,
                output_root=output_root,
                listing_date=listing_date,
            )
            row = {
                "statement_family": config.statement_family,
                "standardized_rows": len(standardized_df),
                "audit_rows": len(audit_df),
                "missing_rows": int(standardized_df["missing_reason"].fillna("").ne("").sum()),
            }
            summary_rows.append(row)
            overall_rows.append({"code": code, **row})

        pd.DataFrame(summary_rows).to_csv(bank_dir / "standardization_summary.csv", index=False, encoding="utf-8-sig")
        print(f"Completed {code}")

    overall_df = pd.DataFrame(overall_rows)
    overall_df.to_csv(output_root / "all_banks_standardization_summary.csv", index=False, encoding="utf-8-sig")

    bank_level_df, missing_reason_df = build_missingness_summary(output_root, codes)
    bank_level_df.to_csv(output_root / "all_banks_bank_level_summary.csv", index=False, encoding="utf-8-sig")
    missing_reason_df.to_csv(output_root / "all_banks_missing_reason_summary.csv", index=False, encoding="utf-8-sig")

    if not missing_reason_df.empty:
        pivot = (
            missing_reason_df.groupby(["statement_family", "missing_reason"], as_index=False)["row_count"]
            .sum()
            .sort_values(["statement_family", "row_count"], ascending=[True, False])
        )
        pivot.to_csv(output_root / "all_banks_missing_reason_pivot.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
