from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "quarterly_fundamental_monthly_momentum_rolling_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "quarterly_fundamental_monthly_momentum_rolling_validation_v1.md"

MONTHLY_TARGET_COL = "y_month_avg_daily_return_close"

STRATEGY_SPECS = [
    {
        "strategy_name": "direct_mom12_top6",
        "mode": "direct_momentum",
        "candidate_pool_size": None,
        "hold_count": 6,
    },
    {
        "strategy_name": "quarterly_fundamental_top16_equal",
        "mode": "quarterly_fundamental_equal",
        "candidate_pool_size": 16,
        "hold_count": 16,
    },
    {
        "strategy_name": "quarterly_fundamental_top20_equal",
        "mode": "quarterly_fundamental_equal",
        "candidate_pool_size": 20,
        "hold_count": 20,
    },
    {
        "strategy_name": "quarterly_top16_mom12_top6",
        "mode": "quarterly_gated_momentum",
        "candidate_pool_size": 16,
        "hold_count": 6,
    },
    {
        "strategy_name": "quarterly_top20_mom12_top6",
        "mode": "quarterly_gated_momentum",
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
    return df[["rebalance_date", "code", "mom_12_1", MONTHLY_TARGET_COL]].copy()


def equal_weight_return(group: pd.DataFrame, target_col: str) -> dict[str, object]:
    work = group.dropna(subset=[target_col]).copy()
    if work.empty:
        return {
            "portfolio_return": pd.NA,
            "holding_count": 0,
        }
    return {
        "portfolio_return": float(pd.to_numeric(work[target_col], errors="coerce").fillna(0.0).mean()),
        "holding_count": int(len(work)),
    }


def select_top_n(group: pd.DataFrame, sort_col: str, top_n: int | None) -> pd.DataFrame:
    work = group.dropna(subset=[sort_col]).sort_values([sort_col, "code"], ascending=[False, True]).copy()
    if top_n is None:
        return work
    return work.head(int(top_n)).copy()


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

        pool_maps = {
            16: build_quarterly_fundamental_pool_map(scored_quarterly_df, 16),
            20: build_quarterly_fundamental_pool_map(scored_quarterly_df, 20),
        }

        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=["score__mom12", MONTHLY_TARGET_COL]).copy()
            if len(group) < 6:
                continue
            month_date = pd.Timestamp(rebalance_date)
            quarter_anchor = month_anchor_map.get(month_date)
            if quarter_anchor is None:
                continue

            for spec in STRATEGY_SPECS:
                mode = str(spec["mode"])
                pool_size = spec["candidate_pool_size"]
                hold_count = int(spec["hold_count"])

                if mode == "direct_momentum":
                    selected = select_top_n(group, "score__mom12", hold_count)
                    evaluated = equal_weight_return(selected, MONTHLY_TARGET_COL)
                    candidate_count = int(len(group))
                else:
                    allowed_codes = pool_maps[int(pool_size)].get(quarter_anchor, set())
                    candidate_pool = group[group["code"].isin(allowed_codes)].copy()
                    candidate_count = int(len(candidate_pool))
                    if mode == "quarterly_fundamental_equal":
                        selected = candidate_pool
                    else:
                        selected = select_top_n(candidate_pool, "score__mom12", hold_count)
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
                        "candidate_pool_size": pool_size if pool_size is not None else "",
                        "hold_count": hold_count,
                        "universe_count": int(len(group)),
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
        "# Quarterly Fundamental Monthly Momentum Rolling Validation V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- quarterly layer updates the fundamental candidate pool `F_t` using `combo__equal_weight`",
        "- monthly layer ranks only inside `F_t` using deployment-safe `mom_12_1`",
        "- final holdings are equal-weight within the selected monthly set",
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
                "- compare `quarterly_top16_mom12_top6` and `quarterly_top20_mom12_top6` against `direct_mom12_top6` to judge whether quarterly fundamental admission adds value",
                "- compare the gated strategies against `quarterly_fundamental_top16_equal` and `quarterly_fundamental_top20_equal` to judge whether monthly momentum adds value after quarterly fundamental admission",
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
