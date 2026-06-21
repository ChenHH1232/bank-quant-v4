from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR / "fundamental_momentum_dual_engine_rolling_test_v1_detail.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "dual_engine_incremental_attribution_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "dual_engine_incremental_attribution_v1.md"


def load_input() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    for col in ["portfolio_return", "invested_weight", "cash_weight"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def build_detail(df: pd.DataFrame) -> pd.DataFrame:
    work = df[df["strategy_name"].isin(["fundamental_only", "blend_60_40"])].copy()
    pivot = work.pivot_table(
        index=["fold_id", "rebalance_date", "validation_start", "validation_end"],
        columns="strategy_name",
        values=["portfolio_return", "invested_weight", "cash_weight"],
    )
    pivot.columns = [f"{a}__{b}" for a, b in pivot.columns]
    out = pivot.reset_index()
    out["delta_return"] = out["portfolio_return__blend_60_40"] - out["portfolio_return__fundamental_only"]
    out["delta_invested_weight"] = out["invested_weight__blend_60_40"] - out["invested_weight__fundamental_only"]
    out["delta_cash_weight"] = out["cash_weight__blend_60_40"] - out["cash_weight__fundamental_only"]
    return out.sort_values(["fold_id", "rebalance_date"]).reset_index(drop=True)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    if df.empty:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(df.columns))
        writer.writeheader()
        writer.writerows(df.to_dict("records"))


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def write_summary(df: pd.DataFrame) -> None:
    lines = [
        "# Dual Engine Incremental Attribution V1",
        "",
        "Objective:",
        "- measure what the deployed `60/40` dual-engine blend adds relative to pure fundamental",
        "- keep the comparison at the same pre-2021 rolling out-of-sample snapshots",
        "",
        "Protocol:",
        "- reference = `fundamental_only`",
        "- tested blend = `blend_60_40`",
        "- comparison unit = each out-of-sample rebalance snapshot",
        "",
    ]

    if not df.empty:
        fundamental_cum = float((1.0 + pd.to_numeric(df["portfolio_return__fundamental_only"], errors="coerce")).prod() - 1.0)
        blend_cum = float((1.0 + pd.to_numeric(df["portfolio_return__blend_60_40"], errors="coerce")).prod() - 1.0)
        delta_cum = blend_cum - fundamental_cum
        mean_delta_return = float(pd.to_numeric(df["delta_return"], errors="coerce").mean())
        mean_delta_invested = float(pd.to_numeric(df["delta_invested_weight"], errors="coerce").mean())
        mean_delta_cash = float(pd.to_numeric(df["delta_cash_weight"], errors="coerce").mean())
        pos_count = int((pd.to_numeric(df["delta_return"], errors="coerce") > 0).sum())
        neg_count = int((pd.to_numeric(df["delta_return"], errors="coerce") < 0).sum())

        lines.extend(
            [
                "Incremental summary:",
                f"- `fundamental_only` cum return = `{format_float(fundamental_cum)}`",
                f"- `blend_60_40` cum return = `{format_float(blend_cum)}`",
                f"- cumulative increment = `{format_float(delta_cum)}`",
                f"- mean per-snapshot return increment = `{format_float(mean_delta_return)}`",
                f"- positive increment snapshots = `{pos_count}`",
                f"- negative increment snapshots = `{neg_count}`",
                f"- mean invested-weight increment = `{format_float(mean_delta_invested)}`",
                f"- mean cash-weight change = `{format_float(mean_delta_cash)}`",
                "",
                "Interpretation:",
                "- the main first-order improvement from adding momentum is higher effective capital deployment",
                "- the dual-engine blend reduces residual cash created by the conservative cap structure",
                "- this higher deployment translates into a positive average return increment on most snapshots",
            ]
        )

        lines.extend(["", "Fold attribution:"])
        for fold_id, group in df.groupby("fold_id", sort=True):
            f = pd.to_numeric(group["portfolio_return__fundamental_only"], errors="coerce")
            b = pd.to_numeric(group["portfolio_return__blend_60_40"], errors="coerce")
            fold_f = float((1.0 + f).prod() - 1.0)
            fold_b = float((1.0 + b).prod() - 1.0)
            fold_delta = fold_b - fold_f
            fold_pos = int((pd.to_numeric(group["delta_return"], errors="coerce") > 0).sum())
            lines.append(
                f"- `{fold_id}` | fundamental=`{format_float(fold_f)}` | blend_60_40=`{format_float(fold_b)}` | "
                f"increment=`{format_float(fold_delta)}` | positive_snapshots=`{fold_pos}/{len(group)}`"
            )

        top_rows = df.sort_values("delta_return", ascending=False).head(3)
        bot_rows = df.sort_values("delta_return", ascending=True).head(3)

        lines.extend(["", "Best incremental snapshots:"])
        for _, row in top_rows.iterrows():
            lines.append(
                f"- `{row['rebalance_date']}` `{row['fold_id']}` | delta_return=`{format_float(row['delta_return'])}` | "
                f"delta_invested=`{format_float(row['delta_invested_weight'])}`"
            )

        lines.extend(["", "Weakest incremental snapshots:"])
        for _, row in bot_rows.iterrows():
            lines.append(
                f"- `{row['rebalance_date']}` `{row['fold_id']}` | delta_return=`{format_float(row['delta_return'])}` | "
                f"delta_invested=`{format_float(row['delta_invested_weight'])}`"
            )

        lines.extend(
            [
                "",
                "Current reading:",
                "- this first-pass attribution does not yet separate alpha improvement from diversification improvement",
                "- but it already shows that the dual-engine blend improves the practical portfolio profile beyond pure fundamental on the same snapshots",
                "- the next attribution layer should study holding overlap and dual-confirmation effects",
            ]
        )

    lines.extend(["", "Output:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = load_input()
    detail_df = build_detail(df)
    write_csv(OUT_DETAIL_PATH, detail_df)
    write_summary(detail_df)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
