from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_weak_down_exit_rolling_validation_v1 as base
import build_weak_down_exit_signal_refinement_v1 as refine

SCRIPT_DIR = Path(__file__).resolve().parent
DETERIORATION_PATH = SCRIPT_DIR / "fundamental_deterioration_date_panel_v1.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "fundamental_conditioned_momentum_threshold_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "fundamental_conditioned_momentum_threshold_validation_v1.md"


def load_deterioration_panel() -> pd.DataFrame:
    df = pd.read_csv(DETERIORATION_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["deterioration_state_raw"] = (
        -pd.to_numeric(df["deterioration_ratio"], errors="coerce")
        + pd.to_numeric(df["score_delta_mean"], errors="coerce")
        + pd.to_numeric(df["score_delta_bottom_quartile_mean"], errors="coerce")
    )
    return df[["rebalance_date", "deterioration_state_raw"]].copy()


def classify_deterioration_regime(value: float, low_cut: float, high_cut: float) -> str:
    if pd.isna(value):
        return "neutral"
    if value <= low_cut:
        return "deteriorating"
    if value >= high_cut:
        return "improving"
    return "neutral"


def get_conditioned_release_cut(
    base_cut_q50: float,
    base_cut_q67: float,
    regime: str,
) -> float:
    if regime == "deteriorating":
        return base_cut_q67
    if regime == "improving":
        return base_cut_q50
    return 0.5 * (base_cut_q50 + base_cut_q67)


def build_detail_rows(
    monthly_bridge_df: pd.DataFrame,
    annual_state_df: pd.DataFrame,
    release_df: pd.DataFrame,
    deterioration_df: pd.DataFrame,
    folds: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    release_map = release_df.set_index("rebalance_date")["mom6_positive_ratio"].to_dict()
    deterioration_map = deterioration_df.set_index("rebalance_date")["deterioration_state_raw"].to_dict()

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
        train_release = release_df[
            (release_df["rebalance_date"] >= train_start) & (release_df["rebalance_date"] < validation_start)
        ].copy()
        train_det = deterioration_df[
            (deterioration_df["rebalance_date"] >= train_start) & (deterioration_df["rebalance_date"] < validation_start)
        ].copy()
        if train_annual.empty or train_release.empty or train_det.empty:
            continue

        annual_low_cut = float(train_annual["breadth_state_score"].quantile(0.33))
        annual_high_cut = float(train_annual["breadth_state_score"].quantile(0.67))
        release_q50 = float(pd.to_numeric(train_release["mom6_positive_ratio"], errors="coerce").dropna().quantile(0.50))
        release_q67 = float(pd.to_numeric(train_release["mom6_positive_ratio"], errors="coerce").dropna().quantile(0.67))
        det_low_cut = float(pd.to_numeric(train_det["deterioration_state_raw"], errors="coerce").dropna().quantile(0.33))
        det_high_cut = float(pd.to_numeric(train_det["deterioration_state_raw"], errors="coerce").dropna().quantile(0.67))

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
            det_value = deterioration_map.get(month_date, pd.NA)
            det_regime = classify_deterioration_regime(float(det_value), det_low_cut, det_high_cut) if pd.notna(det_value) else "neutral"
            conditioned_cut = get_conditioned_release_cut(release_q50, release_q67, det_regime)

            if annual_bucket == "weak_down" and pd.notna(release_value) and float(release_value) >= conditioned_cut:
                final_state_bucket = "neutral_flat"
            else:
                final_state_bucket = annual_bucket

            fundamental_budget, momentum_budget = base.get_budgets(final_state_bucket)
            evaluated = base.evaluate_monthly_group(group, fundamental_budget, momentum_budget)
            rows.append(
                {
                    "fold_id": fold["fold_id"],
                    "rebalance_date": month_date.strftime("%Y-%m-%d"),
                    "annual_anchor_date": annual_anchor.strftime("%Y-%m-%d"),
                    "annual_state_score": round(annual_score, 6),
                    "annual_state_bucket": annual_bucket,
                    "deterioration_state_raw": round(float(det_value), 6) if pd.notna(det_value) else pd.NA,
                    "deterioration_regime": det_regime,
                    "release_signal_value": round(float(release_value), 6) if pd.notna(release_value) else pd.NA,
                    "release_cut_q50": round(release_q50, 6),
                    "release_cut_q67": round(release_q67, 6),
                    "conditioned_release_cut": round(conditioned_cut, 6),
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
        "# Fundamental Conditioned Momentum Threshold Validation V1",
        "",
        "Objective:",
        "- test whether the monthly momentum release threshold should be conditioned on fundamental deterioration regime",
        "- fixed release backbone = `mom6_positive_ratio`",
        "- deteriorating regime = require stronger momentum confirmation",
        "- improving regime = allow easier momentum release",
        "",
        "Rule:",
        "- if deterioration regime = `deteriorating`, release cut = train `q67`",
        "- if deterioration regime = `improving`, release cut = train `q50`",
        "- if deterioration regime = `neutral`, release cut = midpoint between `q50` and `q67`",
        "",
        f"- fold count: `{len(folds)}`",
    ]

    if not df.empty:
        cum_return = float((1.0 + pd.to_numeric(df["portfolio_return"], errors="coerce")).prod() - 1.0)
        mean_return = pd.to_numeric(df["portfolio_return"], errors="coerce").mean()
        mean_cash = pd.to_numeric(df["cash_weight"], errors="coerce").mean()
        lines.extend(
            [
                "",
                "Conditioned-threshold summary:",
                f"- snapshots=`{len(df)}`",
                f"- mean_return=`{base.format_float(mean_return)}`",
                f"- cum_return=`{base.format_float(cum_return)}`",
                f"- mean_cash=`{base.format_float(mean_cash)}`",
            ]
        )

        regime_summary = (
            df.groupby("deterioration_regime", dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_cut=("conditioned_release_cut", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_signal=("release_signal_value", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
        )
        lines.append("")
        lines.append("Regime summary:")
        for _, row in regime_summary.iterrows():
            lines.append(
                f"- `{row['deterioration_regime']}` | snapshots=`{int(row['snapshot_count'])}` | mean_return=`{base.format_float(row['mean_return'])}` | mean_cut=`{base.format_float(row['mean_cut'])}` | mean_signal=`{base.format_float(row['mean_signal'])}`"
            )

        weak_df = df[df["annual_state_bucket"] == "weak_down"].copy()
        if not weak_df.empty:
            released = weak_df[weak_df["final_state_bucket"] == "neutral_flat"].copy()
            held = weak_df[weak_df["final_state_bucket"] == "weak_down"].copy()
            lines.extend(
                [
                    "",
                    "Weak-down release behavior:",
                    f"- weak_down_snapshots=`{len(weak_df)}`",
                    f"- released_to_neutral=`{len(released)}`",
                    f"- held_in_weak_down=`{len(held)}`",
                ]
            )

        lines.extend(
            [
                "",
                "Compare against fixed references:",
                "- benchmark reference should be `mom6_positive_ratio_q50` from the weak-down exit refinement note",
                "- if conditioned thresholds do not beat that baseline, keep the simpler fixed-threshold rule",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    monthly_panel = refine.load_monthly_panel()
    folds = base.dual.load_folds()

    fundamental_panel = base.dual.load_fundamental_panel()
    fundamental_panel["rebalance_date"] = pd.to_datetime(fundamental_panel["rebalance_date"])
    fundamental_panel = fundamental_panel[fundamental_panel["rebalance_date"] < pd.Timestamp("2021-05-01")].copy()
    full_train_mask = fundamental_panel["rebalance_date"] < pd.Timestamp("2021-05-01")
    scored_quarterly_df = base.dual.build_fundamental_score_frame(fundamental_panel, full_train_mask)
    monthly_bridge_df = base.build_fundamental_monthly_bridge(scored_quarterly_df, monthly_panel)
    annual_state_df = base.load_annual_state_panel()
    release_df = refine.build_monthly_release_panel(monthly_panel)
    deterioration_df = load_deterioration_panel()

    rows = build_detail_rows(monthly_bridge_df, annual_state_df, release_df, deterioration_df, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
