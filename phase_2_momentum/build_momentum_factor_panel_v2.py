from __future__ import annotations

from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR / "momentum_factor_panel_v1.csv"
OUTPUT_PATH = SCRIPT_DIR / "momentum_factor_panel_v2.csv"
SUMMARY_PATH = SCRIPT_DIR / "momentum_factor_panel_v2.md"

TRADING_DAYS_1M = 20
TRADING_DAYS_3M = 60
TRADING_DAYS_6M = 120
TRADING_DAYS_12M = 240


def build_panel() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["code", "date"]).reset_index(drop=True)

    out_frames: list[pd.DataFrame] = []
    for _, group in df.groupby("code", sort=False):
        one = group.copy()
        close = pd.to_numeric(one["close"], errors="coerce")
        one["mom_3_1"] = close.shift(TRADING_DAYS_1M).div(close.shift(TRADING_DAYS_3M)) - 1.0
        one["mom_6_1"] = close.shift(TRADING_DAYS_1M).div(close.shift(TRADING_DAYS_6M)) - 1.0
        one["mom_12_1"] = close.shift(TRADING_DAYS_1M).div(close.shift(TRADING_DAYS_12M)) - 1.0
        one["price_history_3_1_ready"] = one["mom_3_1"].notna().astype(int)
        one["price_history_6_1_ready"] = one["mom_6_1"].notna().astype(int)
        one["price_history_12_1_ready_v2"] = one["mom_12_1"].notna().astype(int)
        one["momentum_monthly_ready_v2"] = (
            one["mom_3_1"].notna()
            & one["mom_6_1"].notna()
            & one["mom_12_1"].notna()
            & pd.to_numeric(one["liq_money_1m"], errors="coerce").notna()
            & pd.to_numeric(one["market_cap"], errors="coerce").notna()
        ).astype(int)
        out_frames.append(one)

    out = pd.concat(out_frames, ignore_index=True)
    out = out.sort_values(["date", "code"]).reset_index(drop=True)
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    return out


def write_summary(df: pd.DataFrame) -> None:
    lines = [
        "# Momentum Factor Panel V2",
        "",
        "Definition:",
        "- extends `momentum_factor_panel_v1.csv` with monthly-rebalance research fields",
        "- adds `mom_3_1` so monthly momentum can compare `3-1`, `6-1`, and `12-1` on one panel",
        "",
        f"- rows: `{len(df)}`",
        f"- stocks: `{df['code'].nunique()}`",
        f"- date span: `{df['date'].min()}` to `{df['date'].max()}`",
        f"- monthly-ready rows: `{int(df['momentum_monthly_ready_v2'].sum())}`",
        "",
        "Non-null coverage:",
        f"- `mom_3_1`: `{int(df['mom_3_1'].notna().sum())}`",
        f"- `mom_6_1`: `{int(df['mom_6_1'].notna().sum())}`",
        f"- `mom_12_1`: `{int(df['mom_12_1'].notna().sum())}`",
        "",
        "Output:",
        f"- [{OUTPUT_PATH.name}]({OUTPUT_PATH})",
    ]
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    out = build_panel()
    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    write_summary(out)
    print(OUTPUT_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
