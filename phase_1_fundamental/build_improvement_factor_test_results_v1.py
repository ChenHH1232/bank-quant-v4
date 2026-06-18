import csv
from pathlib import Path

import numpy as np
import pandas as pd

from build_single_factor_test_results import (
    TRAIN_END,
    TRAIN_START,
    VALIDATION_END,
    VALIDATION_START,
    build_results,
    load_manifest,
)


SCRIPT_DIR = Path(__file__).resolve().parent
BASE_PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
MANIFEST_PATH = SCRIPT_DIR / "improvement_factor_manifest_v1.csv"
OUTPUT_PANEL_PATH = SCRIPT_DIR / "improvement_factor_panel_v1.csv"
OUTPUT_PATH = SCRIPT_DIR / "improvement_factor_test_results_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "improvement_factor_test_results_v1.md"


def load_base_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_stock_pool_flag"].astype(str) == "1"].copy()
    return df


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def season_bucket(rebalance_date: pd.Timestamp) -> str:
    month = int(rebalance_date.month)
    if month <= 4:
        return "annual"
    if month <= 8:
        return "interim"
    return "q3"


def add_snapshot_delta(df: pd.DataFrame, base_factor: str, output_col: str) -> None:
    values = pd.to_numeric(df[base_factor], errors="coerce")
    previous = values.groupby(df["code"]).shift(1)
    df[output_col] = values - previous


def add_season_yoy_delta(df: pd.DataFrame, base_factor: str, output_col: str) -> None:
    values = pd.to_numeric(df[base_factor], errors="coerce")
    work = df[["code", "rebalance_date"]].copy()
    work["_value"] = values
    work["_season_bucket"] = work["rebalance_date"].map(season_bucket)
    work["_year"] = work["rebalance_date"].dt.year

    prior = work[["code", "_season_bucket", "_year", "_value"]].copy()
    prior["_year"] = prior["_year"] + 1
    prior = prior.rename(columns={"_value": "_prior_year_same_season"})

    merged = work.merge(
        prior,
        how="left",
        on=["code", "_season_bucket", "_year"],
    )
    df[output_col] = merged["_value"] - merged["_prior_year_same_season"]


def add_annual_delta(df: pd.DataFrame, base_factor: str, output_col: str) -> None:
    source_col = f"{base_factor}__source_year"
    values = pd.to_numeric(df[base_factor], errors="coerce")
    years = pd.to_numeric(df[source_col], errors="coerce")

    annual = df[["code"]].copy()
    annual["_value"] = values
    annual["_source_year"] = years
    annual = annual.dropna(subset=["_value", "_source_year"])
    annual["_source_year"] = annual["_source_year"].astype(int)
    annual = annual.drop_duplicates(subset=["code", "_source_year"], keep="last")

    annual = annual.sort_values(["code", "_source_year"]).copy()
    annual["_prev_value"] = annual.groupby("code")["_value"].shift(1)
    annual["_annual_delta"] = annual["_value"] - annual["_prev_value"]

    mapping = annual.set_index(["code", "_source_year"])["_annual_delta"]
    df[output_col] = [
        mapping.get((code, int(source_year)), np.nan) if pd.notna(source_year) else np.nan
        for code, source_year in zip(df["code"], years)
    ]


def build_improvement_panel(base_df: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> pd.DataFrame:
    df = base_df.copy()
    for row in manifest_rows:
        factor_name = row["factor_name"]
        base_factor = row["base_factor_name"]
        variant = row["improvement_variant"]

        if variant == "snapshot_delta":
            add_snapshot_delta(df, base_factor, factor_name)
        elif variant == "season_yoy_delta":
            add_season_yoy_delta(df, base_factor, factor_name)
        elif variant == "annual_delta":
            add_annual_delta(df, base_factor, factor_name)
        else:
            raise ValueError(f"Unsupported improvement variant: {variant}")
    return df


def write_improvement_panel(df: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    keep_cols = [
        "rebalance_date",
        "code",
        "y_quarter_avg_daily_return_close",
        "y_year_avg_daily_return_close",
    ]
    factor_cols = [row["factor_name"] for row in manifest_rows]
    out = df[keep_cols + factor_cols].copy()
    out.to_csv(OUTPUT_PANEL_PATH, index=False, encoding="utf-8-sig")


def write_results(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_PATH.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_custom_summary(results_df: pd.DataFrame) -> None:
    summary_lines = [
        "# Improvement Factor Test Results V1",
        "",
        f"- Train window: `{TRAIN_START.date()}` to `{TRAIN_END.date()}`",
        f"- Validation window: `{VALIDATION_START.date()}` to `{VALIDATION_END.date()}`",
        f"- Total improvement factors tested: `{len(results_df)}`",
        "",
        "Status count:",
    ]
    status_counts = results_df["final_status"].value_counts().to_dict()
    for status in ["A", "B", "C", "D"]:
        summary_lines.append(f"- `{status}`: `{status_counts.get(status, 0)}`")

    top_rows = results_df.sort_values(
        ["final_status", "validation_rank_ic_mean", "train_rank_ic_mean"],
        ascending=[True, False, False],
    ).head(10)
    summary_lines.extend(
        [
            "",
            "Top reviewed rows:",
        ]
    )
    for _, row in top_rows.iterrows():
        summary_lines.append(
            f"- `{row['factor_name']}` | status=`{row['final_status']}` | "
            f"val_ic=`{row['validation_rank_ic_mean']}` | train_ic=`{row['train_rank_ic_mean']}`"
        )
    summary_lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
            f"- [{OUTPUT_PANEL_PATH.name}]({OUTPUT_PANEL_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(summary_lines), encoding="utf-8")


def main() -> None:
    base_df = load_base_panel(BASE_PANEL_PATH)
    manifest_rows = load_manifest(MANIFEST_PATH)
    improvement_df = build_improvement_panel(base_df, manifest_rows)
    write_improvement_panel(improvement_df, manifest_rows)

    results = build_results(improvement_df, manifest_rows)
    write_results(results)
    results_df = pd.DataFrame(results)
    write_custom_summary(results_df)

    print(f"tested_improvement_factors={len(results)}")
    print(OUTPUT_PANEL_PATH)
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
