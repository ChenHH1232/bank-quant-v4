from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
FUNDAMENTAL_DIR = ROOT_DIR / "phase_1_fundamental"

if str(FUNDAMENTAL_DIR) not in sys.path:
    sys.path.insert(0, str(FUNDAMENTAL_DIR))

from build_pre2021_rolling_validation_v1 import (  # type: ignore
    add_combo_scores,
    build_scored_panel,
    load_panel,
    prepare_factor_metadata,
)

RESEARCH_END = pd.Timestamp("2021-05-01")
SCENARIO_NAME = "base_plus_top2_9"
COMBO_NAME = "combo__equal_weight"
REFERENCE_LAG_DATES = 1

OUT_STOCK_PATH = SCRIPT_DIR / "fundamental_deterioration_stock_panel_v1.csv"
OUT_DATE_PATH = SCRIPT_DIR / "fundamental_deterioration_date_panel_v1.csv"
OUT_MD_PATH = SCRIPT_DIR / "fundamental_deterioration_feature_panel_v1.md"


def load_enhanced_metadata() -> list[dict[str, str]]:
    _, enhanced_rows = prepare_factor_metadata()
    return enhanced_rows


def build_global_scored_panel() -> pd.DataFrame:
    panel_df = load_panel()
    panel_df["rebalance_date"] = pd.to_datetime(panel_df["rebalance_date"])
    panel_df = panel_df[panel_df["rebalance_date"] < RESEARCH_END].copy()

    metadata_rows = load_enhanced_metadata()
    # Use all pre-2021 rows as the normalization fit for this feature-construction layer.
    # This is acceptable because this panel is only a raw observable-feature source;
    # later rolling validation can still re-standardize or threshold inside each train fold.
    train_mask = panel_df["rebalance_date"] < RESEARCH_END
    scored_df, train_ic_weight_map, factor_groups = build_scored_panel(panel_df, metadata_rows, train_mask)
    scored_df = add_combo_scores(scored_df, train_ic_weight_map, factor_groups)
    scored_df["composite_score"] = pd.to_numeric(scored_df[COMBO_NAME], errors="coerce")
    scored_df = scored_df.dropna(subset=["composite_score"]).copy()
    return scored_df


def assign_reference_dates(dates: list[pd.Timestamp], lag_dates: int) -> dict[pd.Timestamp, pd.Timestamp | None]:
    mapping: dict[pd.Timestamp, pd.Timestamp | None] = {}
    for idx, date_value in enumerate(dates):
        ref_idx = idx - lag_dates
        mapping[date_value] = dates[ref_idx] if ref_idx >= 0 else None
    return mapping


def build_stock_level_delta_panel(scored_df: pd.DataFrame) -> pd.DataFrame:
    dates = sorted(pd.to_datetime(scored_df["rebalance_date"].drop_duplicates()))
    ref_map = assign_reference_dates(dates, REFERENCE_LAG_DATES)

    current_df = scored_df[["rebalance_date", "code", "composite_score"]].copy()
    current_df = current_df.rename(columns={"composite_score": "current_composite_score"})
    current_df["reference_rebalance_date"] = current_df["rebalance_date"].map(ref_map)

    reference_df = scored_df[["rebalance_date", "code", "composite_score"]].copy()
    reference_df = reference_df.rename(
        columns={
            "rebalance_date": "reference_rebalance_date",
            "composite_score": "reference_composite_score",
        }
    )

    merged = current_df.merge(reference_df, how="left", on=["reference_rebalance_date", "code"])
    merged["score_delta"] = (
        pd.to_numeric(merged["current_composite_score"], errors="coerce")
        - pd.to_numeric(merged["reference_composite_score"], errors="coerce")
    )
    merged["deterioration_flag"] = (
        pd.to_numeric(merged["score_delta"], errors="coerce") < 0
    ).astype("float64")
    return merged.sort_values(["rebalance_date", "code"]).reset_index(drop=True)


def safe_quantile(series: pd.Series, q: float) -> float | None:
    valid = pd.to_numeric(series, errors="coerce").dropna()
    if valid.empty:
        return None
    return float(valid.quantile(q))


def build_date_level_panel(stock_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for rebalance_date, group in stock_df.groupby("rebalance_date", sort=True):
        work = group.copy()
        delta = pd.to_numeric(work["score_delta"], errors="coerce")
        current_score = pd.to_numeric(work["current_composite_score"], errors="coerce")
        ref_score = pd.to_numeric(work["reference_composite_score"], errors="coerce")

        valid_mask = delta.notna() & current_score.notna() & ref_score.notna()
        valid = work[valid_mask].copy()
        valid_delta = pd.to_numeric(valid["score_delta"], errors="coerce")
        if valid.empty:
            continue

        q25 = safe_quantile(valid_delta, 0.25)
        severe_flag = valid_delta <= q25 if q25 is not None else pd.Series(index=valid.index, dtype="bool")

        rows.append(
            {
                "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                "reference_rebalance_date": pd.Timestamp(valid["reference_rebalance_date"].iloc[0]).strftime("%Y-%m-%d")
                if pd.notna(valid["reference_rebalance_date"].iloc[0]) else "",
                "stock_count": int(len(valid)),
                "deterioration_ratio": round(float((valid_delta < 0).mean()), 10),
                "severe_deterioration_ratio": round(float(severe_flag.mean()), 10) if len(valid) > 0 and q25 is not None else np.nan,
                "score_delta_mean": round(float(valid_delta.mean()), 10),
                "score_delta_median": round(float(valid_delta.median()), 10),
                "score_delta_std": round(float(valid_delta.std(ddof=0)), 10) if len(valid_delta) > 1 else 0.0,
                "score_delta_bottom_quartile_mean": round(float(valid_delta[valid_delta <= q25].mean()), 10)
                if q25 is not None and (valid_delta <= q25).any() else np.nan,
                "score_delta_top_quartile_mean": round(float(valid_delta[valid_delta >= safe_quantile(valid_delta, 0.75)].mean()), 10)
                if safe_quantile(valid_delta, 0.75) is not None and (valid_delta >= safe_quantile(valid_delta, 0.75)).any() else np.nan,
                "score_delta_top_bottom_spread": round(
                    float(
                        valid_delta[valid_delta >= safe_quantile(valid_delta, 0.75)].mean()
                        - valid_delta[valid_delta <= q25].mean()
                    ),
                    10,
                )
                if q25 is not None and safe_quantile(valid_delta, 0.75) is not None
                and (valid_delta <= q25).any() and (valid_delta >= safe_quantile(valid_delta, 0.75)).any() else np.nan,
                "current_score_mean": round(float(current_score[valid_mask].mean()), 10),
                "reference_score_mean": round(float(ref_score[valid_mask].mean()), 10),
            }
        )
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def write_csv(path: Path, rows: list[dict[str, object]] | pd.DataFrame) -> None:
    if isinstance(rows, pd.DataFrame):
        rows.to_csv(path, index=False, encoding="utf-8-sig")
        return
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(stock_df: pd.DataFrame, date_df: pd.DataFrame) -> None:
    lines = [
        "# Fundamental Deterioration Feature Panel V1",
        "",
        "Definition:",
        f"- scenario backbone = `{SCENARIO_NAME}`",
        f"- composite score = `{COMBO_NAME}`",
        f"- reference lag = previous `{REFERENCE_LAG_DATES}` rebalance date",
        "- score delta = current composite score minus reference composite score",
        "- deterioration = score delta < 0",
        "",
        f"- stock panel rows: `{len(stock_df)}`",
        f"- date panel rows: `{len(date_df)}`",
    ]
    if not date_df.empty:
        lines.extend(
            [
                f"- first rebalance date: `{date_df['rebalance_date'].min()}`",
                f"- last rebalance date: `{date_df['rebalance_date'].max()}`",
                f"- mean deterioration ratio: `{float(pd.to_numeric(date_df['deterioration_ratio'], errors='coerce').mean()):.10f}`",
                f"- mean score delta: `{float(pd.to_numeric(date_df['score_delta_mean'], errors='coerce').mean()):.10f}`",
                "",
                "Candidate date-level observable fields:",
                "- `deterioration_ratio`",
                "- `severe_deterioration_ratio`",
                "- `score_delta_mean`",
                "- `score_delta_median`",
                "- `score_delta_std`",
                "- `score_delta_bottom_quartile_mean`",
                "- `score_delta_top_bottom_spread`",
                "",
                "Outputs:",
                f"- [{OUT_STOCK_PATH.name}]({OUT_STOCK_PATH})",
                f"- [{OUT_DATE_PATH.name}]({OUT_DATE_PATH})",
            ]
        )
    OUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scored_df = build_global_scored_panel()
    stock_df = build_stock_level_delta_panel(scored_df)
    stock_df = stock_df.dropna(subset=["reference_rebalance_date", "score_delta"]).copy()
    date_df = build_date_level_panel(stock_df)

    write_csv(OUT_STOCK_PATH, stock_df)
    write_csv(OUT_DATE_PATH, date_df)
    write_summary(stock_df, date_df)

    print(OUT_STOCK_PATH)
    print(OUT_DATE_PATH)
    print(OUT_MD_PATH)


if __name__ == "__main__":
    main()
