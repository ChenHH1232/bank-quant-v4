import csv
from collections import Counter
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
SELECTION_PATH = SCRIPT_DIR / "annual_factor_refresh_5y2y1y_v1_factor_selection.csv"
POOL_PATH = SCRIPT_DIR / "final_core_factor_pool_v3.csv"
OUTPUT_PATH = SCRIPT_DIR / "annual_factor_refresh_selection_summary_v1.md"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_layer_map() -> dict[str, str]:
    return {row["factor_name"]: row["layer"] for row in load_rows(POOL_PATH)}


def format_factor_list(names: list[str], layer_map: dict[str, str]) -> list[str]:
    output: list[str] = []
    for name in names:
        layer = layer_map.get(name, "")
        output.append(f"- `{name}` | layer=`{layer}`")
    return output


def main() -> None:
    df = pd.read_csv(SELECTION_PATH, encoding="utf-8-sig")
    df["keep_flag"] = pd.to_numeric(df["keep_flag"], errors="coerce").fillna(0).astype(int)
    layer_map = build_layer_map()

    kept_df = df[df["keep_flag"] == 1].copy()
    fold_ids = list(dict.fromkeys(df["fold_id"].tolist()))
    kept_by_fold: dict[str, list[str]] = {
        fold_id: sorted(kept_df.loc[kept_df["fold_id"] == fold_id, "factor_name"].tolist())
        for fold_id in fold_ids
    }

    keep_count = Counter(kept_df["factor_name"].tolist())
    always_kept = sorted([name for name, count in keep_count.items() if count == len(fold_ids)])
    never_kept = sorted(
        set(df["factor_name"].tolist()) - set(kept_df["factor_name"].tolist())
    )

    lines = [
        "# Annual Factor Refresh Selection Summary V1",
        "",
        "This summary makes the annual 5y+2y+1y refresh easier to read by showing the kept factor set for each annual fold and the year-to-year changes.",
        "",
        f"- annual fold count: `{len(fold_ids)}`",
        f"- controlled factor universe size: `{df['factor_name'].nunique()}`",
        "",
        "## Annual Kept Sets",
    ]

    for fold_id in fold_ids:
        names = kept_by_fold[fold_id]
        lines.append("")
        lines.append(f"### {fold_id}")
        lines.append(f"- kept factor count: `{len(names)}`")
        lines.extend(format_factor_list(names, layer_map))

    lines.extend(["", "## Year-to-Year Changes"])
    previous_names: set[str] | None = None
    previous_fold_id = ""
    for fold_id in fold_ids:
        current_names = set(kept_by_fold[fold_id])
        if previous_names is None:
            previous_names = current_names
            previous_fold_id = fold_id
            continue
        added = sorted(current_names - previous_names)
        removed = sorted(previous_names - current_names)
        lines.append("")
        lines.append(f"### {previous_fold_id} -> {fold_id}")
        lines.append(f"- added count: `{len(added)}`")
        if added:
            lines.extend(format_factor_list(added, layer_map))
        else:
            lines.append("- none")
        lines.append(f"- removed count: `{len(removed)}`")
        if removed:
            lines.extend(format_factor_list(removed, layer_map))
        else:
            lines.append("- none")
        previous_names = current_names
        previous_fold_id = fold_id

    lines.extend(["", "## Stability Snapshot", ""])
    lines.append("### Always Kept")
    lines.append(f"- factor count: `{len(always_kept)}`")
    if always_kept:
        lines.extend(format_factor_list(always_kept, layer_map))
    else:
        lines.append("- none")

    lines.append("")
    lines.append("### Never Kept")
    lines.append(f"- factor count: `{len(never_kept)}`")
    if never_kept:
        lines.extend(format_factor_list(never_kept, layer_map))
    else:
        lines.append("- none")

    lines.append("")
    lines.append("### Keep Frequency")
    frequency_rows = sorted(
        keep_count.items(),
        key=lambda item: (-item[1], item[0]),
    )
    for factor_name, count in frequency_rows:
        lines.append(f"- `{factor_name}` | kept_folds=`{count}/{len(fold_ids)}` | layer=`{layer_map.get(factor_name, '')}`")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
