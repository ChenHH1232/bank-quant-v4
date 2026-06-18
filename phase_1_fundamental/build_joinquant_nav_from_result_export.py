from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
PRIMARY_RESULT_EXPORT_PATH = Path(r"C:\Users\Administrator\Downloads\result_1.csv")
BENCHMARK_RESULT_EXPORT_PATH = Path(r"C:\Users\Administrator\Downloads\result_1 (1).csv")
PRIMARY_NAV_OUTPUT_PATH = ROOT / "joinquant_v4_primary_daily_nav_from_result_v1.csv"
BENCHMARK_NAV_OUTPUT_PATH = ROOT / "joinquant_v4_benchmark_daily_nav_from_result_v1.csv"
COMBINED_NAV_OUTPUT_PATH = ROOT / "joinquant_v4_daily_nav_input_from_results_v1.csv"


def main() -> None:
    primary_df = load_nav_from_result_export(PRIMARY_RESULT_EXPORT_PATH, line_name="primary")
    benchmark_df = load_nav_from_result_export(BENCHMARK_RESULT_EXPORT_PATH, line_name="benchmark")

    primary_df.to_csv(PRIMARY_NAV_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    benchmark_df.to_csv(BENCHMARK_NAV_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    combined_df = pd.concat(
        [
            primary_df[["date", "line", "nav"]],
            benchmark_df[["date", "line", "nav"]],
        ],
        ignore_index=True,
    ).sort_values(["line", "date"]).reset_index(drop=True)
    combined_df.to_csv(COMBINED_NAV_OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"wrote {PRIMARY_NAV_OUTPUT_PATH}")
    print(f"wrote {BENCHMARK_NAV_OUTPUT_PATH}")
    print(f"wrote {COMBINED_NAV_OUTPUT_PATH}")
    print(f"primary rows={len(primary_df)} first_date={primary_df.iloc[0]['date']} last_date={primary_df.iloc[-1]['date']}")
    print(f"benchmark rows={len(benchmark_df)} first_date={benchmark_df.iloc[0]['date']} last_date={benchmark_df.iloc[-1]['date']}")


def load_nav_from_result_export(path: Path, line_name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing result export: {path}")

    df = pd.read_csv(path, encoding="gbk")
    required = {"时间", "策略收益", "基准收益", "超额收益(%)"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"result export missing columns: {sorted(missing)}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["时间"]).dt.normalize()
    df["strategy_return_pct"] = pd.to_numeric(df["策略收益"], errors="coerce")
    df["benchmark_return_pct"] = pd.to_numeric(df["基准收益"], errors="coerce")
    df["excess_return_pct"] = pd.to_numeric(df["超额收益(%)"], errors="coerce")
    df = df.dropna(subset=["date", "strategy_return_pct"]).sort_values("date").reset_index(drop=True)
    if df.empty:
        raise ValueError("result export is empty after cleaning")

    df["line"] = line_name
    df["nav"] = 1.0 + df["strategy_return_pct"] / 100.0
    df["benchmark_nav"] = 1.0 + df["benchmark_return_pct"] / 100.0
    df["excess_nav"] = 1.0 + df["excess_return_pct"] / 100.0
    return df[["date", "line", "nav", "benchmark_nav", "excess_nav", "strategy_return_pct", "benchmark_return_pct", "excess_return_pct"]]


if __name__ == "__main__":
    main()
