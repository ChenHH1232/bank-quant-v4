from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import build_fundamental_momentum_dual_engine_rolling_test_v1 as dual

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DETAIL_PATH = SCRIPT_DIR / "dual_engine_weight_stability_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "dual_engine_weight_stability_validation_v1.md"

STABILITY_SPECS = [
    {"strategy_name": "fundamental_only", "fundamental_budget": 1.0, "momentum_budget": 0.0},
    {"strategy_name": "blend_50_50", "fundamental_budget": 0.5, "momentum_budget": 0.5},
    {"strategy_name": "blend_60_40", "fundamental_budget": 0.6, "momentum_budget": 0.4},
    {"strategy_name": "blend_70_30", "fundamental_budget": 0.7, "momentum_budget": 0.3},
]


def build_detail_rows(panel_df: pd.DataFrame, folds: list[dict[str, object]]) -> list[dict[str, object]]:
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
            for spec in STABILITY_SPECS:
                evaluated = dual.evaluate_group(
                    group,
                    fundamental_budget=float(spec["fundamental_budget"]),
                    momentum_budget=float(spec["momentum_budget"]),
                )
                rows.append(
                    {
                        "fold_id": fold["fold_id"],
                        "strategy_name": spec["strategy_name"],
                        "rebalance_date": pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
                        "train_start": fold["train_start"],
                        "train_end": fold["train_end"],
                        "validation_start": fold["validation_start"],
                        "validation_end": fold["validation_end"],
                        "universe_count": int(len(group)),
                        "fundamental_budget": spec["fundamental_budget"],
                        "momentum_budget": spec["momentum_budget"],
                        "portfolio_return": round(float(evaluated["portfolio_return"]), 10),
                        "invested_weight": round(float(evaluated["invested_weight"]), 6),
                        "cash_weight": round(float(evaluated["cash_weight"]), 6),
                        "fundamental_stock_count": int(evaluated["fundamental_stock_count"]),
                        "momentum_stock_count": int(evaluated["momentum_stock_count"]),
                        "final_stock_count": int(evaluated["final_stock_count"]),
                        "overlap_stock_count": int(evaluated["overlap_stock_count"]),
                        "max_final_weight": round(float(evaluated["max_final_weight"]), 6),
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
        "# Dual Engine Weight Stability Validation V1",
        "",
        "Objective:",
        "- test whether the current dual-engine result depends on one fragile weight point",
        "- compare the local neighborhood around the deployed `60/40` blend",
        "",
        "Protocol:",
        "- research scope = pre-2021 only",
        "- common rebalance dates = intersection of fundamental and momentum panels",
        "- folds reuse the fundamental pre-2021 rolling framework",
        "- fixed candidate neighborhood = `50/50`, `60/40`, `70/30`",
        "- pure fundamental kept as the reference base line",
        "- factor structure remains frozen",
        "- engine stock cap = `5%`",
        "- final stock cap = `8%`",
        "",
        f"- fold count: `{len(folds)}`",
        f"- rebalance snapshots: `{df[['fold_id', 'strategy_name', 'rebalance_date']].drop_duplicates().shape[0] if not df.empty else 0}`",
        "",
    ]

    if not df.empty:
        summary_df = (
            df.groupby("strategy_name", dropna=False)
            .agg(
                snapshot_count=("rebalance_date", "count"),
                mean_return=("portfolio_return", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                cumulative_return=("portfolio_return", lambda s: float((1.0 + pd.to_numeric(s, errors="coerce")).prod() - 1.0)),
                mean_invested_weight=("invested_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_cash_weight=("cash_weight", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                mean_overlap=("overlap_stock_count", lambda s: pd.to_numeric(s, errors="coerce").mean()),
            )
            .reset_index()
            .sort_values(["cumulative_return", "mean_return"], ascending=[False, False])
        )

        lines.append("Strategy summary:")
        for _, row in summary_df.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | snapshots=`{int(row['snapshot_count'])}` | "
                f"mean_return=`{dual.format_float(row['mean_return'])}` | "
                f"cum_return=`{dual.format_float(row['cumulative_return'])}` | "
                f"mean_invested_weight=`{dual.format_float(row['mean_invested_weight'])}` | "
                f"mean_cash_weight=`{dual.format_float(row['mean_cash_weight'])}` | "
                f"mean_overlap=`{dual.format_float(row['mean_overlap'], 2)}`"
            )

        lines.extend(["", "Fold summary:"])
        for fold_id in sorted(df["fold_id"].unique()):
            fold_df = df[df["fold_id"] == fold_id].copy()
            lines.append(f"- `{fold_id}`")
            for strategy_name in ["fundamental_only", "blend_50_50", "blend_60_40", "blend_70_30"]:
                subset = fold_df[fold_df["strategy_name"] == strategy_name].copy()
                if subset.empty:
                    continue
                cum_return = float((1.0 + pd.to_numeric(subset["portfolio_return"], errors="coerce")).prod() - 1.0)
                mean_cash = pd.to_numeric(subset["cash_weight"], errors="coerce").mean()
                lines.append(
                    f"- `{fold_id}` `{strategy_name}` | validation=`{subset['validation_start'].iloc[0]}` to `{subset['validation_end'].iloc[0]}` | "
                    f"dates=`{len(subset)}` | cum_return=`{dual.format_float(cum_return)}` | mean_cash=`{dual.format_float(mean_cash)}`"
                )

        strategy_to_cum = {
            str(row["strategy_name"]): float(row["cumulative_return"])
            for _, row in summary_df.iterrows()
        }
        blend_values = [
            strategy_to_cum.get("blend_50_50"),
            strategy_to_cum.get("blend_60_40"),
            strategy_to_cum.get("blend_70_30"),
        ]
        valid_blends = [value for value in blend_values if value is not None]
        spread = max(valid_blends) - min(valid_blends) if valid_blends else float("nan")
        best_name = summary_df.iloc[0]["strategy_name"]

        lines.extend(
            [
                "",
                "Stability judgment:",
                f"- best_blend=`{best_name}`",
                f"- local_blend_spread=`{dual.format_float(spread)}`",
            ]
        )

        if all(strategy_to_cum.get(name) is not None for name in ["blend_50_50", "blend_60_40", "blend_70_30"]):
            if (
                strategy_to_cum["blend_50_50"] > strategy_to_cum.get("fundamental_only", float("-inf"))
                and strategy_to_cum["blend_60_40"] > strategy_to_cum.get("fundamental_only", float("-inf"))
                and strategy_to_cum["blend_70_30"] > strategy_to_cum.get("fundamental_only", float("-inf"))
            ):
                lines.append("- all three nearby blends beat the pure fundamental reference in cumulative return")
                lines.append("- this supports a `stable allocation neighborhood` reading rather than a single-point accident")
            else:
                lines.append("- not every nearby blend beats the pure fundamental reference")
                lines.append("- this weakens the argument that the dual-engine result comes from a broad stable neighborhood")

        lines.extend(
            [
                "",
                "Interpretation:",
                "- the goal here is not to prove one exact weight is universally optimal",
                "- the goal is to check whether the deployed `60/40` sits inside a sensible and stable allocation band",
                "- only after this test passes should later attribution work treat the dual-engine structure as robust",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_df = dual.build_joint_panel()
    folds = dual.load_folds()
    rows = build_detail_rows(panel_df, folds)
    write_csv(OUT_DETAIL_PATH, rows)
    write_summary(rows, folds)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
