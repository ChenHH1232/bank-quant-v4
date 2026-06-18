from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parent
NAV_INPUT_PATH = ROOT / "joinquant_v4_daily_nav_input_from_results_v1.csv"
PRIMARY_ATTRIBUTION_PATH = ROOT / "joinquant_v4_annual_attribution_v1.csv"
YEARLY_METRICS_OUTPUT_PATH = ROOT / "joinquant_v4_yearly_return_drawdown_split_v1.csv"
YEARLY_COMPARISON_OUTPUT_PATH = ROOT / "joinquant_v4_yearly_return_drawdown_comparison_v1.csv"
YEARLY_SUMMARY_MD_OUTPUT_PATH = ROOT / "joinquant_v4_yearly_return_drawdown_report_v1.md"


@dataclass
class StrategyWindow:
    year_label: str
    start_date: pd.Timestamp
    end_date: pd.Timestamp


def main() -> None:
    nav_df = load_nav_input(NAV_INPUT_PATH)
    windows = build_strategy_windows(PRIMARY_ATTRIBUTION_PATH, nav_df)
    yearly_metrics = build_yearly_metrics(nav_df, windows)
    yearly_metrics.to_csv(YEARLY_METRICS_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    comparison_df = build_yearly_comparison(yearly_metrics)
    comparison_df.to_csv(YEARLY_COMPARISON_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    summary_md = build_summary_markdown(yearly_metrics, comparison_df, windows)
    YEARLY_SUMMARY_MD_OUTPUT_PATH.write_text(summary_md, encoding="utf-8")

    print(f"wrote {YEARLY_METRICS_OUTPUT_PATH}")
    print(f"wrote {YEARLY_COMPARISON_OUTPUT_PATH}")
    print(f"wrote {YEARLY_SUMMARY_MD_OUTPUT_PATH}")


def load_nav_input(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing nav input: {path}")

    df = pd.read_csv(path)
    required = {"date", "line", "nav"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"nav input missing columns: {sorted(missing)}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["line"] = df["line"].astype(str).str.strip().str.lower()
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date", "line", "nav"]).sort_values(["line", "date"]).reset_index(drop=True)
    if df.empty:
        raise ValueError("nav input is empty after cleaning")
    return df


def build_strategy_windows(attribution_path: Path, nav_df: pd.DataFrame) -> list[StrategyWindow]:
    attribution_df = pd.read_csv(attribution_path)
    attribution_df["current_date"] = pd.to_datetime(attribution_df["current_date"])
    may_rebalances = attribution_df.loc[
        attribution_df["current_date"].dt.month.eq(5),
        "current_date",
    ].drop_duplicates().sort_values().tolist()
    if not may_rebalances:
        raise ValueError("no May rebalances found in attribution file")

    max_nav_date = pd.Timestamp(nav_df["date"].max()).normalize()
    windows: list[StrategyWindow] = []

    for idx, start_date in enumerate(may_rebalances):
        start_ts = pd.Timestamp(start_date).normalize()
        if idx + 1 < len(may_rebalances):
            end_ts = pd.Timestamp(may_rebalances[idx + 1]).normalize() - pd.Timedelta(days=1)
        else:
            end_ts = max_nav_date
        year_label = str(start_ts.year)
        windows.append(
            StrategyWindow(
                year_label=year_label,
                start_date=start_ts,
                end_date=end_ts,
            )
        )
    return windows


def build_yearly_metrics(nav_df: pd.DataFrame, windows: Iterable[StrategyWindow]) -> pd.DataFrame:
    rows: list[dict] = []
    for line_name, line_df in nav_df.groupby("line"):
        line_df = line_df.sort_values("date").reset_index(drop=True)
        for window in windows:
            slice_df = line_df.loc[
                line_df["date"].between(window.start_date, window.end_date)
            ].copy()
            if slice_df.empty:
                continue

            slice_df["running_peak"] = slice_df["nav"].cummax()
            slice_df["drawdown"] = slice_df["nav"] / slice_df["running_peak"] - 1.0

            worst_idx = slice_df["drawdown"].idxmin()
            worst_row = slice_df.loc[worst_idx]
            peak_date = locate_peak_date(slice_df, worst_row["running_peak"])

            start_nav = float(slice_df.iloc[0]["nav"])
            end_nav = float(slice_df.iloc[-1]["nav"])
            yearly_return = end_nav / start_nav - 1.0 if start_nav else None

            rows.append(
                {
                    "line": line_name,
                    "year_label": window.year_label,
                    "window_start": window.start_date.date().isoformat(),
                    "window_end": window.end_date.date().isoformat(),
                    "first_trade_date": pd.Timestamp(slice_df.iloc[0]["date"]).date().isoformat(),
                    "last_trade_date": pd.Timestamp(slice_df.iloc[-1]["date"]).date().isoformat(),
                    "obs_count": int(len(slice_df)),
                    "start_nav": start_nav,
                    "end_nav": end_nav,
                    "yearly_return_pct": pct(yearly_return),
                    "max_drawdown_pct": pct(float(worst_row["drawdown"])),
                    "max_drawdown_start": peak_date,
                    "max_drawdown_end": pd.Timestamp(worst_row["date"]).date().isoformat(),
                }
            )
    return pd.DataFrame(rows)


def locate_peak_date(slice_df: pd.DataFrame, running_peak: float) -> str:
    peak_row = slice_df.loc[slice_df["nav"].eq(running_peak)].iloc[0]
    return pd.Timestamp(peak_row["date"]).date().isoformat()


def build_yearly_comparison(yearly_metrics: pd.DataFrame) -> pd.DataFrame:
    if yearly_metrics.empty:
        return pd.DataFrame()

    pivot = yearly_metrics.pivot(index="year_label", columns="line")
    rows: list[dict] = []
    if ("yearly_return_pct", "primary") not in pivot.columns or ("yearly_return_pct", "benchmark") not in pivot.columns:
        return pd.DataFrame()

    for year_label in pivot.index:
        primary_return = pivot.loc[year_label, ("yearly_return_pct", "primary")]
        benchmark_return = pivot.loc[year_label, ("yearly_return_pct", "benchmark")]
        primary_drawdown = pivot.loc[year_label, ("max_drawdown_pct", "primary")]
        benchmark_drawdown = pivot.loc[year_label, ("max_drawdown_pct", "benchmark")]
        rows.append(
            {
                "year_label": year_label,
                "primary_return_pct": primary_return,
                "benchmark_return_pct": benchmark_return,
                "return_gap_pct": primary_return - benchmark_return,
                "primary_max_drawdown_pct": primary_drawdown,
                "benchmark_max_drawdown_pct": benchmark_drawdown,
                "drawdown_gap_pct": primary_drawdown - benchmark_drawdown,
            }
        )
    return pd.DataFrame(rows).sort_values("year_label").reset_index(drop=True)


def build_summary_markdown(
    yearly_metrics: pd.DataFrame,
    comparison_df: pd.DataFrame,
    windows: list[StrategyWindow],
) -> str:
    lines: list[str] = []
    lines.append("# JoinQuant V4 Yearly Return Drawdown Split V1")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Input file: `{NAV_INPUT_PATH.name}`")
    lines.append(f"- Window source: `{PRIMARY_ATTRIBUTION_PATH.name}`")
    lines.append("- Annual windows are defined from each May rebalance date to the day before the next May rebalance date.")
    lines.append("")
    lines.append("## Strategy Windows")
    lines.append("")
    for window in windows:
        lines.append(f"- {window.year_label}: {window.start_date.date().isoformat()} to {window.end_date.date().isoformat()}")
    lines.append("")
    lines.append("## Output Files")
    lines.append("")
    lines.append(f"- `{YEARLY_METRICS_OUTPUT_PATH.name}`")
    lines.append(f"- `{YEARLY_COMPARISON_OUTPUT_PATH.name}`")
    lines.append("")

    if yearly_metrics.empty:
        lines.append("## Result")
        lines.append("")
        lines.append("- No valid yearly metrics were produced.")
        return "\n".join(lines)

    lines.append("## Per-Line Metrics")
    lines.append("")
    for line_name, line_df in yearly_metrics.groupby("line"):
        lines.append(f"### {line_name}")
        lines.append("")
        for _, row in line_df.sort_values("year_label").iterrows():
            lines.append(
                "- {year_label}: return={yearly_return_pct:.2f}% max_drawdown={max_drawdown_pct:.2f}% window={window_start} to {window_end}".format(
                    **row
                )
            )
        lines.append("")

    if not comparison_df.empty:
        lines.append("## Primary vs Benchmark")
        lines.append("")
        for _, row in comparison_df.iterrows():
            lines.append(
                "- {year_label}: return_gap={return_gap_pct:.2f}% drawdown_gap={drawdown_gap_pct:.2f}%".format(
                    **row
                )
            )
        lines.append("")

    return "\n".join(lines)


def pct(value: float | None) -> float | None:
    if value is None or pd.isna(value):
        return None
    return value * 100.0


if __name__ == "__main__":
    main()
