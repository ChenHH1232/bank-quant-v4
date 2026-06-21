from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual
import build_weak_down_exit_rolling_validation_v1 as bridge_base

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "fundamental_gated_momentum_rolling_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "fundamental_gated_momentum_rolling_validation_v1.md"

MONTHLY_TARGET_COL = "y_month_avg_daily_return_close"

STRATEGY_SPECS = [
    {
        "strategy_name": "direct_mom12_top6",
        "mode": "direct_momentum",
        "candidate_pool_size": None,
        "hold_count": 6,
    },
    {
        "strategy_name": "fundamental_top16_equal",
        "mode": "fundamental_equal",
        "candidate_pool_size": 16,
        "hold_count": 16,
    },
    {
        "strategy_name": "gated_top16_mom12_top6",
        "mode": "gated_momentum",
        "candidate_pool_size": 16,
        "hold_count": 6,
    },
    {
        "strategy_name": "fundamental_top20_equal",
        "mode": "fundamental_equal",
        "candidate_pool_size": 20,
        "hold_count": 20,
    },
    {
        "strategy_name": "gated_top20_mom12_top6",
        "mode": "gated_momentum",
        "candidate_pool_size": 20,
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
    return df[
        [
            "rebalance_date",
            "code",
            "mom_12_1",
            MONTHLY_TARGET_COL,
        ]
    ].copy()


def select_top_n(group: pd.DataFrame, sort_col: str, top_n: int) -> pd.DataFrame:
    work = group.dropna(subset=[sort_col]).sort_values([sort_col, "code"], ascending=[False, True]).copy()
    if top_n is None or top_n <= 0:
        return work
    return work.head(int(top_n)).copy()


def equal_weight_return(group: pd.DataFrame, target_col: str) -> dict[str, object]:
    work = group.dropna(subset=[target_col]).copy()
    if work.empty:
        return {
            "portfolio_return": np.nan,
            "invested_weight": 0.0,
            "cash_weight": 1.0,
            "holding_count": 0,
        }
    hold_count = len(work)
    weight = 1.0 / float(hold_count)
    portfolio_return = float(pd.to_numeric(work[target_col], errors="coerce").fillna(0.0).mean())
    return {
        "portfolio_return": portfolio_return,
        "invested_weight": 1.0,
        "cash_weight": 0.0,
        "holding_count": hold_count,
    }


def evaluate_strategy_group(group: pd.DataFrame, spec: dict[str, object]) -> dict[str, object]:
    mode = str(spec["mode"])
    candidate_pool_size = spec["candidate_pool_size"]
    hold_count = int(spec["hold_count"])

    if mode == "direct_momentum":
        picked = select_top_n(group, "score__mom12", hold_count)
        result = equal_weight_return(picked, MONTHLY_TARGET_COL)
        result["candidate_count"] = int(len(group.dropna(subset=["score__mom12"])))
        return result

    candidate_pool = select_top_n(group, dual.FUNDAMENTAL_COMBO, int(candidate_pool_size))
    if mode == "fundamental_equal":
        result = equal_weight_return(candidate_pool, MONTHLY_TARGET_COL)
        result["candidate_count"] = int(len(candidate_pool))
        return result

    picked = select_top_n(candidate_pool, "score__mom12", hold_count)
    result = equal_weight_return(picked, MONTHLY_TARGET_COL)
    result["candidate_count"] = int(len(candidate_pool))
    return result


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
        monthly_bridge_df = bridge_base.build_fundamental_monthly_bridge(scored_quarterly_df, monthly_panel)

        monthly_train_mask = (monthly_bridge_df["rebalance_date"] >= train_start) & (monthly_bridge_df["rebalance_date"] < validation_start)
        monthly_bridge_df["score__mom12"] = dual.preprocess_momentum_factor(monthly_bridge_df, monthly_train_mask)

        validation_df = monthly_bridge_df[
            (monthly_bridge_df["rebalance_date"] >= validation_start)
            & (monthly_bridge_df["rebalance_date"] <= validation_end)
        ].copy()

        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[dual.FUNDAMENTAL_COMBO, "score__mom12", MONTHLY_TARGET_COL]).copy()
            if len(group) < 6:
                continue

            for spec in STRATEGY_SPECS:
                evaluated = evaluate_strategy_group(group, spec)
                if pd.isna(evaluated["portfolio_return"]):
                    continue
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "strategy_name": spec["strategy_name"],
                        "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                        "train_start": fold["train_start"],
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "mode": spec["mode"],
                        "candidate_pool_size": spec["candidate_pool_size"] if spec["candidate_pool_size"] is not None else "",
                        "hold_count": spec["hold_count"],
                        "universe_count": int(len(group)),
                        "candidate_count": int(evaluated["candidate_count"]),
                        "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                        "invested_weight": round(float(evaluated["invested_weight"]), 6),
                        "cash_weight": round(float(evaluated["cash_weight"]), 6),
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
        "# Fundamental Gated Momentum Rolling Validation V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- objective = test whether fundamentals should act as a candidate gate while momentum ranks inside the approved pool",
        "- monthly momentum rank uses deployment-safe `mom_12_1` only in this first pass",
        "- fundamental score source = quarterly `combo__equal_weight` carried forward to monthly rebalance dates",
        "- final holdings are equal-weight within each selected set",
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
                mean_candidate_count=("candidate_count", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_holding_count=("holding_count", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        lines.append("Strategy summary:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{format_float(row['mean_return'])}` | "
                f"cum_return=`{format_float(row['cumulative_return'])}` | "
                f"mean_candidate_count=`{format_float(row['mean_candidate_count'], 2)}` | "
                f"mean_holding_count=`{format_float(row['mean_holding_count'], 2)}`"
            )

        lines.extend(
            [
                "",
                "Interpretation targets:",
                "- compare `gated_top16_mom12_top6` and `gated_top20_mom12_top6` against direct momentum to test whether fundamental admission improves momentum selection",
                "- compare the gated versions against `fundamental_top16_equal` and `fundamental_top20_equal` to test whether momentum adds value after fundamental admission",
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
