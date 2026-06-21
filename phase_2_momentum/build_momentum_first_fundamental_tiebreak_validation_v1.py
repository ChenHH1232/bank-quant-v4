from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "momentum_first_fundamental_tiebreak_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "momentum_first_fundamental_tiebreak_validation_v1.md"

MONTHLY_TARGET_COL = "y_month_avg_daily_return_close"

STRATEGY_SPECS = [
    {
        "strategy_name": "direct_mom12_top6",
        "mode": "direct_momentum",
        "momentum_candidate_count": None,
        "hold_count": 6,
    },
    {
        "strategy_name": "quarterly_top20_mom12_top6",
        "mode": "quarterly_gated_momentum",
        "momentum_candidate_count": None,
        "hold_count": 6,
        "candidate_pool_size": 20,
    },
    {
        "strategy_name": "mom12_top10_then_fundamental_top6",
        "mode": "momentum_first_fundamental_tiebreak",
        "momentum_candidate_count": 10,
        "hold_count": 6,
    },
    {
        "strategy_name": "mom12_top12_then_fundamental_top6",
        "mode": "momentum_first_fundamental_tiebreak",
        "momentum_candidate_count": 12,
        "hold_count": 6,
    },
]


def load_monthly_panel() -> pd.DataFrame:
    df = pd.read_csv(dual.MOMENTUM_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    df = df[df["rebalance_stock_pool_flag_v2"] == 1].copy()
    for col in ["mom_12_1", MONTHLY_TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["rebalance_date", "code", "mom_12_1", MONTHLY_TARGET_COL]].copy()


def select_top_n(group: pd.DataFrame, sort_col: str, top_n: int | None) -> pd.DataFrame:
    work = group.dropna(subset=[sort_col]).sort_values([sort_col, "code"], ascending=[False, True]).copy()
    if top_n is None:
        return work
    return work.head(int(top_n)).copy()


def equal_weight_return(group: pd.DataFrame, target_col: str) -> dict[str, object]:
    work = group.dropna(subset=[target_col]).copy()
    if work.empty:
        return {"portfolio_return": pd.NA, "holding_count": 0}
    return {
        "portfolio_return": float(pd.to_numeric(work[target_col], errors="coerce").fillna(0.0).mean()),
        "holding_count": int(len(work)),
    }


def build_quarterly_fundamental_pool_map(scored_quarterly_df: pd.DataFrame, pool_size: int) -> dict[pd.Timestamp, set[str]]:
    pool_map: dict[pd.Timestamp, set[str]] = {}
    for rebalance_date, group in scored_quarterly_df.groupby("rebalance_date", sort=True):
        picked = select_top_n(group, dual.FUNDAMENTAL_COMBO, pool_size)
        pool_map[pd.Timestamp(rebalance_date)] = set(picked["code"].tolist())
    return pool_map


def map_month_to_quarter_anchor(monthly_dates: list[pd.Timestamp], quarterly_dates: list[pd.Timestamp]) -> dict[pd.Timestamp, pd.Timestamp | None]:
    mapping: dict[pd.Timestamp, pd.Timestamp | None] = {}
    quarter_idx = 0
    last_quarter: pd.Timestamp | None = None
    for month_date in monthly_dates:
        while quarter_idx < len(quarterly_dates) and quarterly_dates[quarter_idx] <= month_date:
            last_quarter = quarterly_dates[quarter_idx]
            quarter_idx += 1
        mapping[month_date] = last_quarter
    return mapping


def build_detail_rows(monthly_panel: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    quarterly_panel = dual.load_fundamental_panel()
    quarterly_panel["rebalance_date"] = pd.to_datetime(quarterly_panel["rebalance_date"])
    quarterly_panel = quarterly_panel[quarterly_panel["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()

    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        quarterly_train_mask = (quarterly_panel["rebalance_date"] >= train_start) & (quarterly_panel["rebalance_date"] < validation_start)
        scored_quarterly_df = dual.build_fundamental_score_frame(quarterly_panel, quarterly_train_mask)

        monthly_train_mask = (monthly_panel["rebalance_date"] >= train_start) & (monthly_panel["rebalance_date"] < validation_start)
        monthly_scored_df = monthly_panel.copy()
        monthly_scored_df["score__mom12"] = dual.preprocess_momentum_factor(monthly_scored_df, monthly_train_mask)

        validation_df = monthly_scored_df[
            (monthly_scored_df["rebalance_date"] >= validation_start)
            & (monthly_scored_df["rebalance_date"] <= validation_end)
        ].copy()
        if validation_df.empty:
            continue

        quarterly_dates = sorted(pd.to_datetime(scored_quarterly_df["rebalance_date"].drop_duplicates()))
        monthly_dates = sorted(pd.to_datetime(validation_df["rebalance_date"].drop_duplicates()))
        month_anchor_map = map_month_to_quarter_anchor(monthly_dates, quarterly_dates)
        pool_map_20 = build_quarterly_fundamental_pool_map(scored_quarterly_df, 20)

        # carry forward latest visible fundamental score to each monthly date
        fundamental_frame = scored_quarterly_df[["rebalance_date", "code", dual.FUNDAMENTAL_COMBO]].copy()

        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=["score__mom12", MONTHLY_TARGET_COL]).copy()
            if len(group) < 6:
                continue
            month_date = pd.Timestamp(rebalance_date)
            quarter_anchor = month_anchor_map.get(month_date)
            if quarter_anchor is None:
                continue

            current_fundamental = fundamental_frame[fundamental_frame["rebalance_date"] == quarter_anchor][["code", dual.FUNDAMENTAL_COMBO]].copy()
            merged = group.merge(current_fundamental, on="code", how="left")
            merged[dual.FUNDAMENTAL_COMBO] = pd.to_numeric(merged[dual.FUNDAMENTAL_COMBO], errors="coerce")

            for spec in STRATEGY_SPECS:
                mode = str(spec["mode"])
                hold_count = int(spec["hold_count"])
                momentum_candidate_count = spec["momentum_candidate_count"]

                if mode == "direct_momentum":
                    selected = select_top_n(merged, "score__mom12", hold_count)
                    candidate_count = int(len(merged))
                    stage1_count = candidate_count
                elif mode == "quarterly_gated_momentum":
                    allowed_codes = pool_map_20.get(quarter_anchor, set())
                    candidate_pool = merged[merged["code"].isin(allowed_codes)].copy()
                    candidate_count = int(len(candidate_pool))
                    stage1_count = candidate_count
                    selected = select_top_n(candidate_pool, "score__mom12", hold_count)
                else:
                    stage1_pool = select_top_n(merged, "score__mom12", int(momentum_candidate_count))
                    stage1_count = int(len(stage1_pool))
                    candidate_count = int(len(merged))
                    selected = select_top_n(stage1_pool, dual.FUNDAMENTAL_COMBO, hold_count)

                evaluated = equal_weight_return(selected, MONTHLY_TARGET_COL)
                if pd.isna(evaluated["portfolio_return"]):
                    continue

                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "strategy_name": spec["strategy_name"],
                        "rebalance_date": month_date.strftime("%Y-%m-%d"),
                        "train_start": fold["train_start"],
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "quarter_anchor_date": quarter_anchor.strftime("%Y-%m-%d"),
                        "mode": mode,
                        "momentum_candidate_count": momentum_candidate_count if momentum_candidate_count is not None else "",
                        "hold_count": hold_count,
                        "universe_count": int(len(merged)),
                        "stage1_count": stage1_count,
                        "candidate_count": candidate_count,
                        "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                        "holding_count": int(evaluated["holding_count"]),
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


def write_summary(rows: list[dict[str, object]], folds: list[dict[str, object]]) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# Momentum First Fundamental Tiebreak Validation V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- momentum remains the primary monthly selector",
        "- fundamental score uses the latest visible quarterly snapshot only",
        "- new structure = momentum first, fundamental second-stage ranking",
        "",
        "Compared structures:",
        "- `direct_mom12_top6`",
        "- `quarterly_top20_mom12_top6`",
        "- `mom12_top10_then_fundamental_top6`",
        "- `mom12_top12_then_fundamental_top6`",
        "",
        f"- fold count: `{len(folds)}`",
        f"- strategy snapshots: `{df[['fold_id', 'strategy_name', 'rebalance_date']].drop_duplicates().shape[0] if not df.empty else 0}`",
        "",
    ]
    if not df.empty:
        summary_df = (
            df.groupby("strategy_name", dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_stage1_count=("stage1_count", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_holding_count=("holding_count", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        lines.append("Strategy summary:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{format_float(row['mean_return'])}` | cum_return=`{format_float(row['cumulative_return'])}` | "
                f"mean_stage1_count=`{format_float(row['mean_stage1_count'], 2)}` | mean_holding_count=`{format_float(row['mean_holding_count'], 2)}`"
            )

        lines.extend(
            [
                "",
                "Interpretation target:",
                "- if the momentum-first fundamental-second-stage variants beat direct momentum, basic fundamentals add value as a tie-break quality layer without taking over the fast signal",
                "- if they also challenge or beat the quarterly gate structure, then momentum-first plus slow fundamental ranking becomes a meaningful new active branch",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    monthly_panel = load_monthly_panel()
    folds = dual.load_folds()
    rows = build_detail_rows(monthly_panel, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
