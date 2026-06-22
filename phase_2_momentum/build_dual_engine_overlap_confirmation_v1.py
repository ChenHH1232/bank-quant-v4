from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "dual_engine_overlap_confirmation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "dual_engine_overlap_confirmation_v1.md"

TARGET_F_BUDGET = 0.6
TARGET_M_BUDGET = 0.4


def build_stock_level_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        train_mask = (panel_df["rebalance_date"] >= train_start) & (panel_df["rebalance_date"] < validation_start)
        validation_mask = (panel_df["rebalance_date"] >= validation_start) & (panel_df["rebalance_date"] <= validation_end)

        scored_df = dual.build_fundamental_score_frame(panel_df, train_mask)
        scored_df["score__mom12"] = dual.preprocess_momentum_factor(scored_df, train_mask)

        validation_df = scored_df[validation_mask].copy()
        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[dual.FUNDAMENTAL_COMBO, "score__mom12", dual.FUNDAMENTAL_TARGET_COL]).copy()
            if len(group) < 5:
                continue

            work = group.copy()
            work["fundamental_weight"] = dual.build_engine_weights(work, dual.FUNDAMENTAL_COMBO, TARGET_F_BUDGET, dual.ENGINE_STOCK_CAP)
            work["momentum_weight"] = dual.build_engine_weights(work, "score__mom12", TARGET_M_BUDGET, dual.ENGINE_STOCK_CAP)
            work["selected_f"] = (pd.to_numeric(work["fundamental_weight"], errors="coerce").fillna(0.0) > 1e-12).astype(int)
            work["selected_m"] = (pd.to_numeric(work["momentum_weight"], errors="coerce").fillna(0.0) > 1e-12).astype(int)

            def classify(row: pd.Series) -> str:
                if int(row["selected_f"]) == 1 and int(row["selected_m"]) == 1:
                    return "both_selected"
                if int(row["selected_f"]) == 1:
                    return "fundamental_only_selected"
                if int(row["selected_m"]) == 1:
                    return "momentum_only_selected"
                return "neither_selected"

            work["selection_bucket"] = work.apply(classify, axis=1)
            work[dual.FUNDAMENTAL_TARGET_COL] = pd.to_numeric(work[dual.FUNDAMENTAL_TARGET_COL], errors="coerce")

            for _, row in work.iterrows():
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "code": row["code"],
                        "fundamental_score": row[dual.FUNDAMENTAL_COMBO],
                        "momentum_score": row["score__mom12"],
                        "fundamental_weight": row["fundamental_weight"],
                        "momentum_weight": row["momentum_weight"],
                        "selected_f": int(row["selected_f"]),
                        "selected_m": int(row["selected_m"]),
                        "selection_bucket": row["selection_bucket"],
                        "forward_return": row[dual.FUNDAMENTAL_TARGET_COL],
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(rows: list[dict[str, object]]) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# Dual Engine Overlap Confirmation V1",
        "",
        "Objective:",
        "- test whether the current dual-engine blend derives value from different stock selection or from different weighting on the same stock set",
        "- inspect whether `dual confirmation` stocks are actually a distinct bucket under the current implementation",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- stock-level inspection uses the deployed `60/40` blend",
        "- selection is defined by positive engine weight under the frozen `5%` engine cap",
        "",
    ]

    if not df.empty:
        total_rows = int(len(df))
        bucket_summary = (
            df.groupby("selection_bucket", dropna=False)
            .agg(
                stock_count=("code", "count"),
                mean_forward_return=("forward_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values("stock_count", ascending=False)
        )

        lines.append("Selection-bucket summary:")
        for _, row in bucket_summary.iterrows():
            ratio = float(row["stock_count"]) / float(total_rows) if total_rows > 0 else float("nan")
            lines.append(
                f"- `{row['selection_bucket']}` | stock_rows=`{int(row['stock_count'])}` | ratio=`{format_float(ratio)}` | "
                f"mean_forward_return=`{format_float(row['mean_forward_return'])}`"
            )

        date_summary = (
            df.groupby(["fold_id", "rebalance_date"], dropna=False)
            .agg(
                universe_count=("code", "count"),
                f_count=("selected_f", "sum"),
                m_count=("selected_m", "sum"),
                both_count=("selection_bucket", lambda s: int((s == "both_selected").sum())),
                only_f_count=("selection_bucket", lambda s: int((s == "fundamental_only_selected").sum())),
                only_m_count=("selection_bucket", lambda s: int((s == "momentum_only_selected").sum())),
            )
            .reset_index()
        )
        date_summary["overlap_ratio_jaccard"] = date_summary["both_count"] / (
            date_summary["f_count"] + date_summary["m_count"] - date_summary["both_count"]
        )

        lines.extend(
            [
                "",
                "Overlap summary:",
                f"- mean_jaccard_overlap=`{format_float(pd.to_numeric(date_summary['overlap_ratio_jaccard'], errors='coerce').mean())}`",
                f"- min_jaccard_overlap=`{format_float(pd.to_numeric(date_summary['overlap_ratio_jaccard'], errors='coerce').min())}`",
                f"- max_jaccard_overlap=`{format_float(pd.to_numeric(date_summary['overlap_ratio_jaccard'], errors='coerce').max())}`",
            ]
        )

        both_only = int((bucket_summary["selection_bucket"] == "both_selected").any())
        only_f_rows = int((df["selection_bucket"] == "fundamental_only_selected").sum())
        only_m_rows = int((df["selection_bucket"] == "momentum_only_selected").sum())

        lines.extend(
            [
                "",
                "Interpretation:",
            ]
        )

        if only_f_rows == 0 and only_m_rows == 0:
            lines.append("- under the current bank universe and cap structure, the two engines effectively select the same stock set on every tested snapshot")
            lines.append("- therefore the current dual-engine edge does not come from low-overlap stock picking")
            lines.append("- it comes from different weighting on a nearly identical stock universe")
            lines.append("- this also means `dual confirmation` is not a distinct stock bucket yet; it is almost the full investable set")
        else:
            lines.append("- the engines do create distinct stock buckets under the current implementation")
            lines.append("- later attribution should compare `both_selected`, `fundamental_only_selected`, and `momentum_only_selected` more directly")

        lines.extend(
            [
                "",
                "Current reading:",
                "- this result strengthens the earlier attribution conclusion that current dual-engine gains are mainly a weighting and deployment effect",
                "- if the project later wants true `selection-layer` interaction evidence, the engine construction would need a narrower stock-selection rule rather than full-universe positive weights",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = dual.build_joint_panel()
    folds = dual.load_folds()
    rows = build_stock_level_rows(panel_df, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
