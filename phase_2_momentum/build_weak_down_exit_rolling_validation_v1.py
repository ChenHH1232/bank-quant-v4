from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual

SCRIPT_DIR = Path(__file__).resolve().parent
DETERIORATION_PANEL_PATH = SCRIPT_DIR / "fundamental_deterioration_date_panel_v1.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "weak_down_exit_rolling_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "weak_down_exit_rolling_validation_v1.md"

MONTHLY_TARGET_COL = "y_month_avg_daily_return_close"
MONTHLY_RELEASE_COL = "mom6_positive_ratio"

STRATEGY_SPECS = [
    {"strategy_name": "fixed_60_40", "mode": "fixed"},
    {"strategy_name": "annual_breadth_only", "mode": "annual_only"},
    {"strategy_name": "annual_breadth_with_monthly_exit", "mode": "annual_with_exit"},
]


def load_monthly_panel() -> pd.DataFrame:
    df = pd.read_csv(dual.MOMENTUM_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    df = df[df["rebalance_stock_pool_flag_v2"] == 1].copy()
    for col in ["mom_12_1", "mom_6_1", MONTHLY_TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[
        [
            "rebalance_date",
            "code",
            "mom_12_1",
            "mom_6_1",
            MONTHLY_TARGET_COL,
        ]
    ].copy()


def load_annual_state_panel() -> pd.DataFrame:
    df = pd.read_csv(DETERIORATION_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    df["deterioration_ratio"] = pd.to_numeric(df["deterioration_ratio"], errors="coerce")
    df["breadth_state_score"] = -df["deterioration_ratio"]
    df = df[df["rebalance_date"].dt.month == 5].copy()
    return df[["rebalance_date", "breadth_state_score", "deterioration_ratio"]].copy()


def build_fundamental_monthly_bridge(scored_quarterly_df: pd.DataFrame, monthly_panel: pd.DataFrame) -> pd.DataFrame:
    monthly_dates = sorted(pd.to_datetime(monthly_panel["rebalance_date"].drop_duplicates()))
    quarterly_dates = sorted(pd.to_datetime(scored_quarterly_df["rebalance_date"].drop_duplicates()))
    date_map: dict[pd.Timestamp, pd.Timestamp | None] = {}
    quarter_idx = 0
    last_quarter_date: pd.Timestamp | None = None
    for month_date in monthly_dates:
        while quarter_idx < len(quarterly_dates) and quarterly_dates[quarter_idx] <= month_date:
            last_quarter_date = quarterly_dates[quarter_idx]
            quarter_idx += 1
        date_map[month_date] = last_quarter_date

    bridge = monthly_panel.copy()
    bridge["fundamental_snapshot_date"] = bridge["rebalance_date"].map(date_map)
    fundamental_slice = scored_quarterly_df[
        ["rebalance_date", "code", dual.FUNDAMENTAL_COMBO]
    ].rename(columns={"rebalance_date": "fundamental_snapshot_date"})
    bridge = bridge.merge(fundamental_slice, on=["fundamental_snapshot_date", "code"], how="left")
    bridge = bridge.dropna(subset=["fundamental_snapshot_date"]).copy()
    return bridge


def build_monthly_release_panel(monthly_panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rebalance_date, group in monthly_panel.groupby("rebalance_date", sort=True):
        mom6 = pd.to_numeric(group["mom_6_1"], errors="coerce")
        valid = mom6.dropna()
        if valid.empty:
            continue
        rows.append(
            {
                "rebalance_date": pd.Timestamp(rebalance_date),
                MONTHLY_RELEASE_COL: float((valid > 0).mean()),
                "month_stock_count": int(len(valid)),
            }
        )
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


def classify_state(score_value: float, low_cut: float, high_cut: float) -> str:
    if pd.isna(score_value):
        return "neutral_flat"
    if score_value >= high_cut:
        return "strong_up"
    if score_value <= low_cut:
        return "weak_down"
    return "neutral_flat"


def get_budgets(state_bucket: str) -> tuple[float, float]:
    if state_bucket == "strong_up":
        return 0.6, 0.4
    if state_bucket == "weak_down":
        return 1.0, 0.0
    return 0.8, 0.2


def build_detail_rows(
    monthly_bridge_df: pd.DataFrame,
    annual_state_df: pd.DataFrame,
    release_df: pd.DataFrame,
    folds: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fold in folds:
        train_start = pd.Timestamp(fold["train_start"])
        validation_start = pd.Timestamp(fold["validation_start"])
        validation_end = pd.Timestamp(fold["validation_end"])

        train_mask = (monthly_bridge_df["rebalance_date"] >= train_start) & (monthly_bridge_df["rebalance_date"] < validation_start)
        validation_mask = (monthly_bridge_df["rebalance_date"] >= validation_start) & (monthly_bridge_df["rebalance_date"] <= validation_end)

        monthly_scored_df = monthly_bridge_df.copy()
        monthly_scored_df["score__mom12"] = dual.preprocess_momentum_factor(monthly_scored_df, train_mask)

        train_annual = annual_state_df[
            (annual_state_df["rebalance_date"] >= train_start) & (annual_state_df["rebalance_date"] < validation_start)
        ].copy()
        if train_annual.empty:
            continue
        annual_low_cut = float(train_annual["breadth_state_score"].quantile(0.33))
        annual_high_cut = float(train_annual["breadth_state_score"].quantile(0.67))

        train_release = release_df[
            (release_df["rebalance_date"] >= train_start) & (release_df["rebalance_date"] < validation_start)
        ].copy()
        if train_release.empty:
            continue
        release_cut = float(train_release[MONTHLY_RELEASE_COL].quantile(0.67))

        validation_df = monthly_scored_df[validation_mask].copy()
        if validation_df.empty:
            continue

        validation_dates = sorted(pd.to_datetime(validation_df["rebalance_date"].drop_duplicates()))
        annual_dates = sorted(pd.to_datetime(annual_state_df["rebalance_date"].drop_duplicates()))
        annual_state_map: dict[pd.Timestamp, dict[str, object]] = {}
        for annual_date, group in annual_state_df.groupby("rebalance_date", sort=True):
            score_value = float(group["breadth_state_score"].iloc[0])
            annual_state_map[pd.Timestamp(annual_date)] = {
                "score_value": score_value,
                "state_bucket": classify_state(score_value, annual_low_cut, annual_high_cut),
            }

        date_to_annual_anchor: dict[pd.Timestamp, pd.Timestamp | None] = {}
        annual_idx = 0
        last_annual_date: pd.Timestamp | None = None
        for month_date in validation_dates:
            while annual_idx < len(annual_dates) and annual_dates[annual_idx] <= month_date:
                last_annual_date = annual_dates[annual_idx]
                annual_idx += 1
            date_to_annual_anchor[month_date] = last_annual_date

        release_map = release_df.set_index("rebalance_date")[MONTHLY_RELEASE_COL].to_dict()

        for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
            group = group.dropna(subset=[dual.FUNDAMENTAL_COMBO, "score__mom12", MONTHLY_TARGET_COL]).copy()
            if len(group) < 5:
                continue

            month_date = pd.Timestamp(rebalance_date)
            annual_anchor = date_to_annual_anchor.get(month_date)
            if annual_anchor is None or annual_anchor not in annual_state_map:
                continue
            annual_bucket = str(annual_state_map[annual_anchor]["state_bucket"])
            annual_score = float(annual_state_map[annual_anchor]["score_value"])
            release_value = release_map.get(month_date, np.nan)

            for spec in STRATEGY_SPECS:
                if spec["mode"] == "fixed":
                    state_bucket = "fixed"
                    fundamental_budget, momentum_budget = (0.6, 0.4)
                elif spec["mode"] == "annual_only":
                    state_bucket = annual_bucket
                    fundamental_budget, momentum_budget = get_budgets(state_bucket)
                else:
                    state_bucket = annual_bucket
                    if annual_bucket == "weak_down" and pd.notna(release_value) and float(release_value) >= release_cut:
                        state_bucket = "neutral_flat"
                    fundamental_budget, momentum_budget = get_budgets(state_bucket)

                evaluated = evaluate_monthly_group(group, fundamental_budget, momentum_budget)
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "strategy_name": spec["strategy_name"],
                        "rebalance_date": month_date.strftime("%Y-%m-%d"),
                        "train_start": fold["train_start"],
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "annual_anchor_date": annual_anchor.strftime("%Y-%m-%d"),
                        "annual_state_score": round(annual_score, 6),
                        "annual_low_cut": round(annual_low_cut, 6),
                        "annual_high_cut": round(annual_high_cut, 6),
                        "annual_state_bucket": annual_bucket,
                        "release_signal_value": round(float(release_value), 6) if pd.notna(release_value) else np.nan,
                        "release_signal_cut": round(release_cut, 6),
                        "final_state_bucket": state_bucket,
                        "fundamental_budget": fundamental_budget,
                        "momentum_budget": momentum_budget,
                        "universe_count": int(len(group)),
                        "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                        "invested_weight": round(float(evaluated["invested_weight"]), 6),
                        "cash_weight": round(float(evaluated["cash_weight"]), 6),
                        "fundamental_stock_count": int(evaluated["fundamental_stock_count"]),
                        "momentum_stock_count": int(evaluated["momentum_stock_count"]),
                        "final_stock_count": int(evaluated["final_stock_count"]),
                        "overlap_stock_count": int(evaluated["overlap_stock_count"]),
                    }
                )
    return rows


def evaluate_monthly_group(group: pd.DataFrame, fundamental_budget: float, momentum_budget: float) -> dict[str, object]:
    work = group.copy()
    work["fundamental_weight"] = dual.build_engine_weights(work, dual.FUNDAMENTAL_COMBO, fundamental_budget, dual.ENGINE_STOCK_CAP)
    work["momentum_weight"] = dual.build_engine_weights(work, "score__mom12", momentum_budget, dual.ENGINE_STOCK_CAP)
    work["raw_final_weight"] = work["fundamental_weight"] + work["momentum_weight"]
    work["final_weight"] = dual.cap_final_weights(work["raw_final_weight"], dual.FINAL_STOCK_CAP)
    work["weighted_return"] = work["final_weight"] * pd.to_numeric(work[MONTHLY_TARGET_COL], errors="coerce").fillna(0.0)
    return {
        "portfolio_return": float(work["weighted_return"].sum()),
        "invested_weight": float(work["final_weight"].sum()),
        "cash_weight": float(max(0.0, 1.0 - work["final_weight"].sum())),
        "fundamental_stock_count": int((work["fundamental_weight"] > 0).sum()),
        "momentum_stock_count": int((work["momentum_weight"] > 0).sum()),
        "final_stock_count": int((work["final_weight"] > 0).sum()),
        "overlap_stock_count": int(((work["fundamental_weight"] > 0) & (work["momentum_weight"] > 0)).sum()),
    }


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
        "# Weak Down Exit Rolling Validation V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- annual weak-state trigger = `breadth_only`",
        "- monthly exit signal = cross-sectional `mom_6_1` positive ratio on the monthly bank pool",
        "- monthly exit rule only upgrades `weak_down` to `neutral_flat`",
        "- shared budget mapping:",
        "- `strong_up` => `60%` fundamental + `40%` momentum",
        "- `neutral_flat` => `80%` fundamental + `20%` momentum",
        "- `weak_down` => `100%` fundamental + `0%` momentum",
        "",
        f"- fold count: `{len(folds)}`",
        f"- strategy snapshots: `{df[['fold_id', 'strategy_name', 'rebalance_date']].drop_duplicates().shape[0] if not df.empty else 0}`",
        "",
    ]
    if not df.empty:
        lines.append("Strategy summary:")
        summary_df = (
            df.groupby("strategy_name", dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_cash_weight=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{format_float(row['mean_return'])}` | "
                f"cum_return=`{format_float(row['cumulative_return'])}` | "
                f"mean_cash=`{format_float(row['mean_cash_weight'])}`"
            )

        release_subset = df[df["strategy_name"] == "annual_breadth_with_monthly_exit"].copy()
        if not release_subset.empty:
            lines.extend(["", "Exit behavior summary:"])
            weak_annual = release_subset[release_subset["annual_state_bucket"] == "weak_down"].copy()
            if not weak_annual.empty:
                released = weak_annual[weak_annual["final_state_bucket"] == "neutral_flat"].copy()
                held = weak_annual[weak_annual["final_state_bucket"] == "weak_down"].copy()
                lines.append(f"- weak-down monthly snapshots=`{len(weak_annual)}`")
                lines.append(f"- released_to_neutral=`{len(released)}`")
                lines.append(f"- held_in_weak_down=`{len(held)}`")
                if len(released) > 0:
                    lines.append(
                        f"- released mean return=`{format_float(pd.to_numeric(released['portfolio_return'], errors='coerce').mean())}`"
                    )
                if len(held) > 0:
                    lines.append(
                        f"- held mean return=`{format_float(pd.to_numeric(held['portfolio_return'], errors='coerce').mean())}`"
                    )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    monthly_panel = load_monthly_panel()
    folds = dual.load_folds()

    fundamental_panel = dual.load_fundamental_panel()
    fundamental_panel["rebalance_date"] = pd.to_datetime(fundamental_panel["rebalance_date"])
    fundamental_panel = fundamental_panel[fundamental_panel["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()

    # Fit the quarterly fundamental score layer on the full pre-2021 sample.
    # The rolling protocol still re-fits momentum and annual/monthly thresholds inside each fold.
    full_train_mask = fundamental_panel["rebalance_date"] < pd.Timestamp("2021-05-01")
    scored_quarterly_df = dual.build_fundamental_score_frame(fundamental_panel, full_train_mask)
    monthly_bridge_df = build_fundamental_monthly_bridge(scored_quarterly_df, monthly_panel)
    annual_state_df = load_annual_state_panel()
    release_df = build_monthly_release_panel(monthly_panel)

    rows = build_detail_rows(monthly_bridge_df, annual_state_df, release_df, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
