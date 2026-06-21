from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "momentum_first_fundamental_tiebreak_grid_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "momentum_first_fundamental_tiebreak_grid_v1.md"

MONTHLY_TARGET_COL = "y_month_avg_daily_return_close"

GRID_SPECS = [
    {"strategy_name": "direct_mom12_top6", "mode": "direct", "momentum_col": "score__mom12", "stage1_count": None, "hold_count": 6},
    {"strategy_name": "quarterly_top20_mom12_top6", "mode": "quarterly_gate", "momentum_col": "score__mom12", "stage1_count": None, "hold_count": 6, "pool_size": 20},
    {"strategy_name": "mom12_top8_then_fundamental_top6", "mode": "tiebreak", "momentum_col": "score__mom12", "stage1_count": 8, "hold_count": 6},
    {"strategy_name": "mom12_top10_then_fundamental_top6", "mode": "tiebreak", "momentum_col": "score__mom12", "stage1_count": 10, "hold_count": 6},
    {"strategy_name": "mom12_top12_then_fundamental_top6", "mode": "tiebreak", "momentum_col": "score__mom12", "stage1_count": 12, "hold_count": 6},
    {"strategy_name": "mom6_top8_then_fundamental_top6", "mode": "tiebreak", "momentum_col": "score__mom6", "stage1_count": 8, "hold_count": 6},
    {"strategy_name": "mom6_top10_then_fundamental_top6", "mode": "tiebreak", "momentum_col": "score__mom6", "stage1_count": 10, "hold_count": 6},
    {"strategy_name": "mom6_top12_then_fundamental_top6", "mode": "tiebreak", "momentum_col": "score__mom6", "stage1_count": 12, "hold_count": 6},
    {"strategy_name": "mom12_top10_then_fundamental_top4", "mode": "tiebreak", "momentum_col": "score__mom12", "stage1_count": 10, "hold_count": 4},
    {"strategy_name": "mom12_top10_then_fundamental_top8", "mode": "tiebreak", "momentum_col": "score__mom12", "stage1_count": 10, "hold_count": 8},
]


def load_monthly_panel() -> pd.DataFrame:
    df = pd.read_csv(dual.MOMENTUM_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    df = df[df["rebalance_stock_pool_flag_v2"] == 1].copy()
    for col in ["mom_12_1", "mom_6_1", MONTHLY_TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["rebalance_date", "code", "mom_12_1", "mom_6_1", MONTHLY_TARGET_COL]].copy()


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
        monthly_scored_df["score__mom12"] = dual.preprocess_momentum_factor(monthly_scored_df.rename(columns={"mom_12_1": dual.MOMENTUM_FACTOR_COL}), monthly_train_mask)
        monthly_scored_df["score__mom6"] = preprocess_alt_momentum_factor(monthly_scored_df, monthly_train_mask, "mom_6_1")

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
        fundamental_frame = scored_quarterly_df[["rebalance_date", "code", dual.FUNDAMENTAL_COMBO]].copy()

        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[MONTHLY_TARGET_COL]).copy()
            month_date = pd.Timestamp(rebalance_date)
            quarter_anchor = month_anchor_map.get(month_date)
            if quarter_anchor is None:
                continue

            current_fundamental = fundamental_frame[fundamental_frame["rebalance_date"] == quarter_anchor][["code", dual.FUNDAMENTAL_COMBO]].copy()
            merged = group.merge(current_fundamental, on="code", how="left")
            merged[dual.FUNDAMENTAL_COMBO] = pd.to_numeric(merged[dual.FUNDAMENTAL_COMBO], errors="coerce")

            for spec in GRID_SPECS:
                momentum_col = str(spec["momentum_col"])
                stage1_count = spec["stage1_count"]
                hold_count = int(spec["hold_count"])
                mode = str(spec["mode"])
                usable = merged.dropna(subset=[momentum_col]).copy()
                if len(usable) < hold_count:
                    continue

                if mode == "direct":
                    selected = select_top_n(usable, momentum_col, hold_count)
                    stage1_actual_count = int(len(usable))
                    candidate_count = int(len(usable))
                elif mode == "quarterly_gate":
                    allowed_codes = pool_map_20.get(quarter_anchor, set())
                    candidate_pool = usable[usable["code"].isin(allowed_codes)].copy()
                    if len(candidate_pool) < hold_count:
                        continue
                    selected = select_top_n(candidate_pool, momentum_col, hold_count)
                    stage1_actual_count = int(len(candidate_pool))
                    candidate_count = int(len(candidate_pool))
                else:
                    stage1_pool = select_top_n(usable, momentum_col, int(stage1_count))
                    stage1_actual_count = int(len(stage1_pool))
                    if len(stage1_pool) < hold_count:
                        continue
                    selected = select_top_n(stage1_pool, dual.FUNDAMENTAL_COMBO, hold_count)
                    candidate_count = int(len(usable))

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
                        "momentum_col": momentum_col,
                        "stage1_count": stage1_count if stage1_count is not None else "",
                        "hold_count": hold_count,
                        "universe_count": int(len(usable)),
                        "stage1_actual_count": stage1_actual_count,
                        "candidate_count": candidate_count,
                        "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                        "holding_count": int(evaluated["holding_count"]),
                    }
                )
    return rows


def preprocess_alt_momentum_factor(full_df: pd.DataFrame, train_mask: pd.Series, source_col: str) -> pd.Series:
    values = pd.to_numeric(full_df[source_col], errors="coerce")
    train_values = values[train_mask].dropna()
    if train_values.empty:
        return pd.Series(index=full_df.index, dtype="float64")
    lower = float(train_values.quantile(0.01))
    upper = float(train_values.quantile(0.99))
    clipped = values.clip(lower=lower, upper=upper)
    train_clipped = clipped[train_mask].dropna()
    mean_value = float(train_clipped.mean())
    std_value = float(train_clipped.std(ddof=0))
    if pd.isna(std_value) or std_value <= 1e-12:
        return pd.Series(index=full_df.index, dtype="float64")
    return (clipped - mean_value) / std_value


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
        "# Momentum First Fundamental Tiebreak Grid V1",
        "",
        "Objective:",
        "- perform a limited neighborhood expansion around the momentum-first fundamental-second-stage idea",
        "- keep the search deliberately narrow to avoid overfitting",
        "",
        "Search axes:",
        "- momentum backbone = `mom_12_1` vs `mom_6_1`",
        "- stage-1 momentum candidate count = `8 / 10 / 12`",
        "- final hold count = `4 / 6 / 8` in a very limited local extension",
        "- control references = `direct_mom12_top6` and `quarterly_top20_mom12_top6`",
        "",
        f"- fold count: `{len(folds)}`",
        f"- strategy snapshots: `{df[['fold_id', 'strategy_name', 'rebalance_date']].drop_duplicates().shape[0] if not df.empty else 0}`",
        "",
    ]
    if not df.empty:
        summary_df = (
            df.groupby(["strategy_name", "momentum_col", "stage1_count", "hold_count"], dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_stage1_actual_count=("stage1_actual_count", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        lines.append("Strategy ranking:")
        for _, row in summary_df.iterrows():
            stage1_label = row["stage1_count"] if not pd.isna(row["stage1_count"]) and row["stage1_count"] != "" else "all"
            lines.append(
                f"- `{row['strategy_name']}` | momentum=`{row['momentum_col']}` | stage1=`{stage1_label}` | hold=`{int(row['hold_count'])}` | "
                f"snapshots=`{int(row['snapshot_count'])}` | mean_return=`{format_float(row['mean_return'])}` | "
                f"cum_return=`{format_float(row['cumulative_return'])}` | mean_stage1_actual_count=`{format_float(row['mean_stage1_actual_count'], 2)}`"
            )

        top3 = summary_df.head(3).copy()
        lines.extend(["", "Recommended next-step shortlist:"])
        for _, row in top3.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | cum_return=`{format_float(row['cumulative_return'])}` | mean_return=`{format_float(row['mean_return'])}`"
            )

        lines.extend(
            [
                "",
                "Interpretation rule:",
                "- prefer a small cluster of nearby strong variants over a single isolated winner",
                "- only those shortlisted variants should move to the frozen post-2021 JoinQuant acceptance stage",
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
