import argparse
from pathlib import Path

import pandas as pd

from standardize_single_bank_statements import DEFAULT_OUTPUT_ROOT


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_STANDARDIZED_ROOT = SCRIPT_DIR / "standardized_outputs"
DEFAULT_WHITELIST_PATH = SCRIPT_DIR / "model_field_whitelist_v1.csv"
DEFAULT_PANEL_ROOT = SCRIPT_DIR / "model_panel_v1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a first-round model panel from standardized statement outputs and the V1 whitelist."
    )
    parser.add_argument("--standardized-root", default=str(DEFAULT_STANDARDIZED_ROOT))
    parser.add_argument("--whitelist-path", default=str(DEFAULT_WHITELIST_PATH))
    parser.add_argument("--output-root", default=str(DEFAULT_PANEL_ROOT))
    parser.add_argument("--limit", type=int, default=0, help="Optional bank limit for testing.")
    return parser


def load_whitelist(path: Path) -> pd.DataFrame:
    whitelist = pd.read_csv(path)
    whitelist["field_key"] = whitelist["statement_family"] + "::" + whitelist["field_name"]
    return whitelist


def iter_bank_dirs(root: Path, limit: int) -> list[Path]:
    dirs = sorted([p for p in root.iterdir() if p.is_dir()])
    if limit and limit > 0:
        dirs = dirs[:limit]
    return dirs


def build_long_panel(standardized_root: Path, whitelist: pd.DataFrame, limit: int) -> pd.DataFrame:
    selected_keys = set(whitelist["field_key"])
    rows: list[pd.DataFrame] = []

    for bank_dir in iter_bank_dirs(standardized_root, limit):
        for standardized_file in bank_dir.glob("*_standardized.csv"):
            df = pd.read_csv(standardized_file)
            if df.empty or "statement_family" not in df.columns:
                continue
            df["field_key"] = df["statement_family"] + "::" + df["standard_field_name"]
            df = df[df["field_key"].isin(selected_keys)].copy()
            if df.empty:
                continue
            df["bank_dir"] = bank_dir.name
            rows.append(df)

    if not rows:
        return pd.DataFrame()

    long_df = pd.concat(rows, ignore_index=True)
    long_df = long_df.merge(
        whitelist[["statement_family", "field_name", "tier", "reason"]],
        left_on=["statement_family", "standard_field_name"],
        right_on=["statement_family", "field_name"],
        how="left",
    )
    long_df = long_df.drop(columns=["field_name", "field_key"], errors="ignore")
    long_df["is_missing"] = long_df["missing_reason"].fillna("").ne("")
    return long_df


def build_wide_panel(long_df: pd.DataFrame) -> pd.DataFrame:
    usable = long_df[~long_df["is_missing"]].copy()
    usable["column_name"] = usable["statement_family"] + "__" + usable["standard_field_name"]
    usable["period_key"] = usable["quarter_key"].fillna(usable["year_key"])
    wide_df = usable.pivot_table(
        index=["code", "report_period_end", "period_key", "pub_date"],
        columns="column_name",
        values="standard_value",
        aggfunc="last",
    ).reset_index()
    wide_df.columns.name = None
    return wide_df


def build_coverage_summary(long_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    field_summary = (
        long_df.groupby(["statement_family", "standard_field_name", "tier"], as_index=False)
        .agg(
            row_count=("standard_value", "size"),
            missing_count=("is_missing", "sum"),
        )
    )
    field_summary["available_count"] = field_summary["row_count"] - field_summary["missing_count"]
    field_summary["missing_ratio"] = field_summary["missing_count"] / field_summary["row_count"]

    bank_summary = (
        long_df.groupby(["code", "statement_family"], as_index=False)
        .agg(
            row_count=("standard_value", "size"),
            missing_count=("is_missing", "sum"),
        )
    )
    bank_summary["available_count"] = bank_summary["row_count"] - bank_summary["missing_count"]
    bank_summary["missing_ratio"] = bank_summary["missing_count"] / bank_summary["row_count"]
    return field_summary, bank_summary


def main() -> None:
    args = build_parser().parse_args()
    standardized_root = Path(args.standardized_root)
    whitelist_path = Path(args.whitelist_path)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    whitelist = load_whitelist(whitelist_path)
    long_df = build_long_panel(standardized_root, whitelist, args.limit)
    if long_df.empty:
        raise RuntimeError("No panel rows were built. Check standardized outputs and whitelist.")

    long_path = output_root / "model_panel_v1_long.csv"
    long_df.to_csv(long_path, index=False, encoding="utf-8-sig")

    wide_df = build_wide_panel(long_df)
    wide_path = output_root / "model_panel_v1_wide.csv"
    wide_df.to_csv(wide_path, index=False, encoding="utf-8-sig")

    field_summary, bank_summary = build_coverage_summary(long_df)
    field_summary.to_csv(output_root / "model_panel_v1_field_coverage.csv", index=False, encoding="utf-8-sig")
    bank_summary.to_csv(output_root / "model_panel_v1_bank_coverage.csv", index=False, encoding="utf-8-sig")

    top_summary = (
        field_summary.sort_values(["missing_ratio", "statement_family", "standard_field_name"])
        .reset_index(drop=True)
    )
    print(top_summary.head(40).to_string(index=False))
    print()
    print(f"Long panel rows: {len(long_df)}")
    print(f"Wide panel rows: {len(wide_df)}")


if __name__ == "__main__":
    main()
