import csv
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "multifactor_core_v2_panel.csv"
OUTPUT_PANEL_PATH = SCRIPT_DIR / "multifactor_core_v2_backtest_groups.csv"
OUTPUT_SUMMARY_PATH = SCRIPT_DIR / "multifactor_core_v2_backtest_summary.md"

TRAIN_START = pd.Timestamp("2014-05-01")
TRAIN_END = pd.Timestamp("2019-05-01")
VALIDATION_START = pd.Timestamp("2019-05-01")
VALIDATION_END = pd.Timestamp("2021-05-01")

COMBO_COLUMNS = [
    "combo__equal_weight",
    "combo__ic_weight",
    "combo__quarterly_plus_annual",
]


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    for col in COMBO_COLUMNS + ["y_quarter_avg_daily_return_close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def build_group_rows(df: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for combo_col in COMBO_COLUMNS:
        for window_name, start, end in [
            ("train", TRAIN_START, TRAIN_END),
            ("validation", VALIDATION_START, VALIDATION_END),
        ]:
            window = df[(df["rebalance_date"] >= start) & (df["rebalance_date"] < end)].copy()
            for rebalance_date, group in window.groupby("rebalance_date"):
                group = group.dropna(subset=[combo_col, "y_quarter_avg_daily_return_close"]).copy()
                if len(group) < 5:
                    continue
                group["bucket"] = assign_groups(group[combo_col], 5)
                group = group.dropna(subset=["bucket"])
                if group.empty:
                    continue
                mean_map = group.groupby("bucket")["y_quarter_avg_daily_return_close"].mean().to_dict()
                for bucket, value in mean_map.items():
                    rows.append(
                        {
                            "combo_name": combo_col,
                            "window_name": window_name,
                            "rebalance_date": rebalance_date.date().isoformat(),
                            "bucket": int(bucket),
                            "avg_return": round(float(value), 10),
                        }
                    )
    return rows


def write_group_rows(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_PANEL_PATH.write_text("", encoding="utf-8")
        return
    with OUTPUT_PANEL_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, object]]) -> None:
    if not rows:
        OUTPUT_SUMMARY_PATH.write_text("# Multifactor Core V2 Backtest Summary\n\n- no rows", encoding="utf-8")
        return
    df = pd.DataFrame(rows)
    lines = [
        "# Multifactor Core V2 Backtest Summary",
        "",
        "5-group average return snapshots:",
    ]
    for combo_col in COMBO_COLUMNS:
        for window_name in ["train", "validation"]:
            subset = df[(df["combo_name"] == combo_col) & (df["window_name"] == window_name)]
            if subset.empty:
                continue
            mean_by_bucket = subset.groupby("bucket")["avg_return"].mean().to_dict()
            top_bottom = mean_by_bucket.get(5, 0.0) - mean_by_bucket.get(1, 0.0)
            lines.append(f"- `{combo_col}` `{window_name}`")
            for bucket in range(1, 6):
                value = mean_by_bucket.get(bucket, None)
                lines.append(f"  bucket_{bucket}: `{value}`")
            lines.append(f"  top_minus_bottom: `{round(float(top_bottom), 10)}`")
    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_PANEL_PATH.name}]({OUTPUT_PANEL_PATH})",
        ]
    )
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = load_panel(PANEL_PATH)
    rows = build_group_rows(df)
    write_group_rows(rows)
    write_summary(rows)
    print(f"rows={len(rows)}")
    print(OUTPUT_PANEL_PATH)
    print(OUTPUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
