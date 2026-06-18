import csv
from pathlib import Path

import pandas as pd

from build_single_factor_test_results import (
    build_results,
    load_manifest,
    load_panel,
)


SCRIPT_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = SCRIPT_DIR / "single_factor_manifest_core_v2.csv"
CORE_POOL_PATH = SCRIPT_DIR / "final_core_factor_pool_v2.csv"
OUTPUT_PATH = SCRIPT_DIR / "single_factor_test_results_core_v2.csv"
SUMMARY_PATH = SCRIPT_DIR / "single_factor_test_results_core_v2.md"


def load_core_pool(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["factor_name"]: row for row in csv.DictReader(handle)}


def write_results(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_PATH.write_text("", encoding="utf-8")
        return
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, object]], core_pool: dict[str, dict[str, str]]) -> None:
    df = pd.DataFrame(rows)
    if df.empty:
        SUMMARY_PATH.write_text("# Single-Factor Test Results Core V2\n\n- no rows", encoding="utf-8")
        return

    df["pool_status"] = df["factor_name"].map(lambda name: core_pool[name]["status"])
    status_counts = df["final_status"].value_counts().to_dict()

    lines = [
        "# Single-Factor Test Results Core V2",
        "",
        "Scope:",
        "- only `final_core_factor_pool_v2` factors",
        "- includes `core_keep`, `secondary_candidate`, and `watch_only`",
        "",
        f"- Tested factors: `{len(df)}`",
        f"- A: `{status_counts.get('A', 0)}`",
        f"- B: `{status_counts.get('B', 0)}`",
        f"- C: `{status_counts.get('C', 0)}`",
        f"- D: `{status_counts.get('D', 0)}`",
        "",
    ]

    for pool_status in ["core_keep", "secondary_candidate", "watch_only"]:
        subset = df[df["pool_status"] == pool_status].copy()
        if subset.empty:
            continue
        subset = subset.sort_values(["final_status", "validation_rank_ic_mean"], ascending=[True, False])
        lines.append(f"## {pool_status}")
        for _, row in subset.iterrows():
            lines.append(
                f"- `{row['factor_name']}` | status=`{row['final_status']}` | val_ic=`{row['validation_rank_ic_mean']}` | target=`{row['target_label']}`"
            )
        lines.append("")

    lines.extend(
        [
            "Output:",
            f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_df = load_panel(SCRIPT_DIR / "phase1_training_panel.csv")
    manifest_rows = load_manifest(MANIFEST_PATH)
    core_pool = load_core_pool(CORE_POOL_PATH)
    results = build_results(panel_df, manifest_rows)
    write_results(results)
    write_summary(results, core_pool)
    print(f"factors={len(results)}")
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
