from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_weak_down_exit_rolling_validation_v1 as base

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "weak_down_exit_signal_refinement_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "weak_down_exit_signal_refinement_v1.md"

RELEASE_SIGNAL_SPECS = [
    {"signal_name": "mom6_positive_ratio_q67", "signal_col": "mom6_positive_ratio", "threshold_q": 0.67},
    {"signal_name": "mom6_positive_ratio_q50", "signal_col": "mom6_positive_ratio", "threshold_q": 0.50},
    {"signal_name": "mom3_positive_ratio_q67", "signal_col": "mom3_positive_ratio", "threshold_q": 0.67},
    {"signal_name": "mom3_positive_ratio_q50", "signal_col": "mom3_positive_ratio", "threshold_q": 0.50},
    {"signal_name": "mom36_combo_q67", "signal_col": "mom36_combo", "threshold_q": 0.67},
    {"signal_name": "mom36_combo_q50", "signal_col": "mom36_combo", "threshold_q": 0.50},
]


def load_monthly_panel() -> pd.DataFrame:
    df = pd.read_csv(base.dual.MOMENTUM_PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    df = df[df["rebalance_stock_pool_flag_v2"] == 1].copy()
    for col in ["mom_3_1", "mom_6_1", "mom_12_1", base.MONTHLY_TARGET_COL]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[
        [
            "rebalance_date",
            "code",
            "mom_3_1",
            "mom_6_1",
            "mom_12_1",
            base.MONTHLY_TARGET_COL,
        ]
    ].copy()


def build_monthly_release_panel(monthly_panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rebalance_date, group in monthly_panel.groupby("rebalance_date", sort=True):
        mom3 = pd.to_numeric(group["mom_3_1"], errors="coerce")
        mom6 = pd.to_numeric(group["mom_6_1"], errors="coerce")
        valid3 = mom3.dropna()
        valid6 = mom6.dropna()
        if valid3.empty and valid6.empty:
            continue
        row = {"rebalance_date": pd.Timestamp(rebalance_date)}
        row["mom3_positive_ratio"] = float((valid3 > 0).mean()) if not valid3.empty else pd.NA
        row["mom6_positive_ratio"] = float((valid6 > 0).mean()) if not valid6.empty else pd.NA
        if not valid3.empty and not valid6.empty:
            row["mom36_combo"] = 0.4 * float((valid3 > 0).mean()) + 0.6 * float((valid6 > 0).mean())
        else:
            row["mom36_combo"] = pd.NA
        row["month_stock_count"] = int(max(len(valid3), len(valid6)))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)


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
        monthly_scored_df["score__mom12"] = base.dual.preprocess_momentum_factor(monthly_scored_df, train_mask)

        train_annual = annual_state_df[
            (annual_state_df["rebalance_date"] >= train_start) & (annual_state_df["rebalance_date"] < validation_start)
        ].copy()
        if train_annual.empty:
            continue
        annual_low_cut = float(train_annual["breadth_state_score"].quantile(0.33))
        annual_high_cut = float(train_annual["breadth_state_score"].quantile(0.67))

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
                "state_bucket": base.classify_state(score_value, annual_low_cut, annual_high_cut),
            }

        date_to_annual_anchor: dict[pd.Timestamp, pd.Timestamp | None] = {}
        annual_idx = 0
        last_annual_date: pd.Timestamp | None = None
        for month_date in validation_dates:
            while annual_idx < len(annual_dates) and annual_dates[annual_idx] <= month_date:
                last_annual_date = annual_dates[annual_idx]
                annual_idx += 1
            date_to_annual_anchor[month_date] = last_annual_date

        for signal_spec in RELEASE_SIGNAL_SPECS:
            signal_name = signal_spec["signal_name"]
            signal_col = signal_spec["signal_col"]
            threshold_q = float(signal_spec["threshold_q"])

            train_release = release_df[
                (release_df["rebalance_date"] >= train_start)
                & (release_df["rebalance_date"] < validation_start)
            ].copy()
            train_signal = pd.to_numeric(train_release[signal_col], errors="coerce").dropna()
            if train_signal.empty:
                continue
            release_cut = float(train_signal.quantile(threshold_q))
            release_map = release_df.set_index("rebalance_date")[signal_col].to_dict()

            for rebalance_date, group in validation_df.groupby("rebalance_date", sort=True):
                group = group.dropna(subset=[base.dual.FUNDAMENTAL_COMBO, "score__mom12", base.MONTHLY_TARGET_COL]).copy()
                if len(group) < 5:
                    continue

                month_date = pd.Timestamp(rebalance_date)
                annual_anchor = date_to_annual_anchor.get(month_date)
                if annual_anchor is None or annual_anchor not in annual_state_map:
                    continue
                annual_bucket = str(annual_state_map[annual_anchor]["state_bucket"])
                annual_score = float(annual_state_map[annual_anchor]["score_value"])
                release_value = release_map.get(month_date, pd.NA)

                if annual_bucket == "weak_down" and pd.notna(release_value) and float(release_value) >= release_cut:
                    final_state_bucket = "neutral_flat"
                else:
                    final_state_bucket = annual_bucket

                fundamental_budget, momentum_budget = base.get_budgets(final_state_bucket)
                evaluated = base.evaluate_monthly_group(group, fundamental_budget, momentum_budget)
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "signal_name": signal_name,
                        "signal_col": signal_col,
                        "threshold_q": threshold_q,
                        "rebalance_date": month_date.strftime("%Y-%m-%d"),
                        "annual_anchor_date": annual_anchor.strftime("%Y-%m-%d"),
                        "annual_state_score": round(annual_score, 6),
                        "annual_state_bucket": annual_bucket,
                        "release_signal_value": round(float(release_value), 6) if pd.notna(release_value) else pd.NA,
                        "release_signal_cut": round(release_cut, 6),
                        "final_state_bucket": final_state_bucket,
                        "fundamental_budget": fundamental_budget,
                        "momentum_budget": momentum_budget,
                        "universe_count": int(len(group)),
                        "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                        "invested_weight": round(float(evaluated["invested_weight"]), 6),
                        "cash_weight": round(float(evaluated["cash_weight"]), 6),
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


def write_summary(rows: list[dict[str, object]], folds: list[dict[str, object]]) -> None:
    df = pd.DataFrame(rows)
    lines = [
        "# Weak Down Exit Signal Refinement V1",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- annual weak-state entry stays fixed at `breadth_only`",
        "- release destination stays fixed at `neutral_flat`",
        "- only the monthly release trigger is refined here",
        "",
        f"- fold count: `{len(folds)}`",
        "",
    ]
    if not df.empty:
        summary_df = (
            df.groupby(["signal_name", "signal_col", "threshold_q"], dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_cash=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )
        lines.append("Signal ranking:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['signal_name']}` | col=`{row['signal_col']}` | q=`{row['threshold_q']:.2f}` | "
                f"snapshots=`{int(row['snapshot_count'])}` | mean_return=`{base.format_float(row['mean_return'])}` | "
                f"cum_return=`{base.format_float(row['cumulative_return'])}` | mean_cash=`{base.format_float(row['mean_cash'])}`"
            )

        top_name = summary_df.iloc[0]["signal_name"]
        top_df = df[df["signal_name"] == top_name].copy()
        weak_df = top_df[top_df["annual_state_bucket"] == "weak_down"].copy()
        if not weak_df.empty:
            released = weak_df[weak_df["final_state_bucket"] == "neutral_flat"].copy()
            held = weak_df[weak_df["final_state_bucket"] == "weak_down"].copy()
            lines.extend(["", "Top signal exit behavior:"])
            lines.append(f"- top_signal=`{top_name}`")
            lines.append(f"- weak_down_snapshots=`{len(weak_df)}`")
            lines.append(f"- released_to_neutral=`{len(released)}`")
            lines.append(f"- held_in_weak_down=`{len(held)}`")

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    monthly_panel = load_monthly_panel()
    folds = base.dual.load_folds()

    fundamental_panel = base.dual.load_fundamental_panel()
    fundamental_panel["rebalance_date"] = pd.to_datetime(fundamental_panel["rebalance_date"])
    fundamental_panel = fundamental_panel[fundamental_panel["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    full_train_mask = fundamental_panel["rebalance_date"] < pd.Timestamp("2021-05-01")
    scored_quarterly_df = base.dual.build_fundamental_score_frame(fundamental_panel, full_train_mask)
    monthly_bridge_df = base.build_fundamental_monthly_bridge(scored_quarterly_df, monthly_panel)
    annual_state_df = base.load_annual_state_panel()
    release_df = build_monthly_release_panel(monthly_panel)

    rows = build_detail_rows(monthly_bridge_df, annual_state_df, release_df, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
