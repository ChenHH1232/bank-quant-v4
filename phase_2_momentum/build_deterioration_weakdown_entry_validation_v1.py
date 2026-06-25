from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DETAIL_PATH = SCRIPT_DIR / "state_proxy_comparison_rolling_validation_v1_detail.csv"
QUARTERLY_DETAIL_PATH = SCRIPT_DIR / "quarterly_fundamental_monthly_momentum_rolling_validation_v1_detail.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "deterioration_weakdown_entry_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "deterioration_weakdown_entry_validation_v1.md"


def load_state_signals() -> pd.DataFrame:
    df = pd.read_csv(STATE_DETAIL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_name"].isin(["price_state_proxy", "deterioration_state_proxy", "combined_state_proxy"])].copy()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["portfolio_return"] = pd.to_numeric(df["portfolio_return"], errors="coerce")
    return df


def load_monthly_return_proxy() -> pd.DataFrame:
    df = pd.read_csv(QUARTERLY_DETAIL_PATH, encoding="utf-8-sig")
    df = df[df["strategy_name"] == "direct_mom12_top6"].copy()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["portfolio_return"] = pd.to_numeric(df["portfolio_return"], errors="coerce")
    df = df.rename(columns={"portfolio_return": "direct_mom12_return"})
    return df[["fold_id", "rebalance_date", "direct_mom12_return"]].copy()


def build_signal_frame() -> pd.DataFrame:
    state_df = load_state_signals()
    monthly_df = load_monthly_return_proxy()

    work = state_df.merge(monthly_df, on=["fold_id", "rebalance_date"], how="inner")
    work = work.sort_values(["fold_id", "strategy_name", "rebalance_date"]).reset_index(drop=True)
    work["next_direct_mom12_return"] = work.groupby(["fold_id"])["direct_mom12_return"].shift(-1)
    work["next_proxy_return"] = work.groupby(["fold_id", "strategy_name"])["portfolio_return"].shift(-1)
    work["weak_down_flag"] = (work["state_bucket"] == "weak_down").astype(int)
    work["next_mom_negative_flag"] = (pd.to_numeric(work["next_direct_mom12_return"], errors="coerce") < 0).astype("float64")
    work["next_proxy_negative_flag"] = (pd.to_numeric(work["next_proxy_return"], errors="coerce") < 0).astype("float64")
    return work


def build_pair_frame(signal_df: pd.DataFrame) -> pd.DataFrame:
    wide = (
        signal_df.pivot_table(
            index=["fold_id", "rebalance_date", "validation_start", "validation_end", "direct_mom12_return", "next_direct_mom12_return"],
            columns="strategy_name",
            values="state_bucket",
            aggfunc="first",
        )
        .reset_index()
    )
    wide.columns.name = None
    for col in ["price_state_proxy", "deterioration_state_proxy", "combined_state_proxy"]:
        if col not in wide.columns:
            wide[col] = pd.NA
    wide["price_weak_down"] = (wide["price_state_proxy"] == "weak_down").astype(int)
    wide["deterioration_weak_down"] = (wide["deterioration_state_proxy"] == "weak_down").astype(int)
    wide["combined_weak_down"] = (wide["combined_state_proxy"] == "weak_down").astype(int)
    wide["deterioration_only_weak_down"] = ((wide["deterioration_weak_down"] == 1) & (wide["price_weak_down"] == 0)).astype(int)
    wide["price_only_weak_down"] = ((wide["price_weak_down"] == 1) & (wide["deterioration_weak_down"] == 0)).astype(int)
    wide["both_weak_down"] = ((wide["price_weak_down"] == 1) & (wide["deterioration_weak_down"] == 1)).astype(int)
    wide["next_mom_negative_flag"] = (pd.to_numeric(wide["next_direct_mom12_return"], errors="coerce") < 0).astype("float64")
    return wide.sort_values(["fold_id", "rebalance_date"]).reset_index(drop=True)


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


def build_proxy_summary(signal_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for strategy_name, group in signal_df.groupby("strategy_name", sort=True):
        eval_df = group.dropna(subset=["next_direct_mom12_return", "next_proxy_return"]).copy()
        weak_df = eval_df[eval_df["weak_down_flag"] == 1].copy()
        non_weak_df = eval_df[eval_df["weak_down_flag"] == 0].copy()
        rows.append(
            {
                "strategy_name": strategy_name,
                "signal_count": int(len(eval_df)),
                "weak_down_count": int(len(weak_df)),
                "weak_down_ratio": float(weak_df.shape[0] / eval_df.shape[0]) if len(eval_df) > 0 else pd.NA,
                "next_mom_mean_after_weak": pd.to_numeric(weak_df["next_direct_mom12_return"], errors="coerce").mean(),
                "next_mom_mean_after_nonweak": pd.to_numeric(non_weak_df["next_direct_mom12_return"], errors="coerce").mean(),
                "next_mom_negative_rate_after_weak": pd.to_numeric(weak_df["next_mom_negative_flag"], errors="coerce").mean(),
                "next_mom_negative_rate_after_nonweak": pd.to_numeric(non_weak_df["next_mom_negative_flag"], errors="coerce").mean(),
                "next_proxy_mean_after_weak": pd.to_numeric(weak_df["next_proxy_return"], errors="coerce").mean(),
                "next_proxy_mean_after_nonweak": pd.to_numeric(non_weak_df["next_proxy_return"], errors="coerce").mean(),
                "next_proxy_negative_rate_after_weak": pd.to_numeric(weak_df["next_proxy_negative_flag"], errors="coerce").mean(),
                "next_proxy_negative_rate_after_nonweak": pd.to_numeric(non_weak_df["next_proxy_negative_flag"], errors="coerce").mean(),
            }
        )
    return pd.DataFrame(rows)


def write_summary(signal_df: pd.DataFrame, pair_df: pd.DataFrame) -> None:
    lines = [
        "# Deterioration Weak-Down Entry Validation V1",
        "",
        "Objective:",
        "- test whether deterioration-based fundamental weakening is usable as a `weak_down` entry signal",
        "- compare it directly against the current price-state proxy",
        "- focus on entry recognition, not full strategy replacement",
        "",
        "Protocol:",
        "- research scope = pre-2021 rolling validation only",
        "- state buckets are reused from the existing rolling proxy framework",
        "- evaluation target = next-month direct momentum environment proxy `direct_mom12_top6` return",
        "- secondary check = next-period return of each proxy's own routed portfolio",
        "",
    ]

    proxy_summary = build_proxy_summary(signal_df)
    if not proxy_summary.empty:
        lines.append("Proxy summary:")
        for _, row in proxy_summary.iterrows():
            lines.append(
                f"- `{row['strategy_name']}` | weak_down_count=`{int(row['weak_down_count'])}` / `{int(row['signal_count'])}` | "
                f"next_mom_after_weak=`{format_float(row['next_mom_mean_after_weak'])}` vs nonweak=`{format_float(row['next_mom_mean_after_nonweak'])}` | "
                f"next_mom_negative_rate_after_weak=`{format_float(row['next_mom_negative_rate_after_weak'])}` vs nonweak=`{format_float(row['next_mom_negative_rate_after_nonweak'])}` | "
                f"next_proxy_after_weak=`{format_float(row['next_proxy_mean_after_weak'])}` vs nonweak=`{format_float(row['next_proxy_mean_after_nonweak'])}`"
            )

    eval_pair_df = pair_df.dropna(subset=["next_direct_mom12_return"]).copy()
    lines.extend(["", "Price vs deterioration pair check:"])
    if not eval_pair_df.empty:
        det_only = eval_pair_df[eval_pair_df["deterioration_only_weak_down"] == 1].copy()
        price_only = eval_pair_df[eval_pair_df["price_only_weak_down"] == 1].copy()
        both = eval_pair_df[eval_pair_df["both_weak_down"] == 1].copy()

        lines.append(
            f"- `deterioration_only_weak_down` count=`{len(det_only)}` | next_mom_mean=`{format_float(pd.to_numeric(det_only['next_direct_mom12_return'], errors='coerce').mean())}` | next_mom_negative_rate=`{format_float(pd.to_numeric(det_only['next_mom_negative_flag'], errors='coerce').mean())}`"
        )
        lines.append(
            f"- `price_only_weak_down` count=`{len(price_only)}` | next_mom_mean=`{format_float(pd.to_numeric(price_only['next_direct_mom12_return'], errors='coerce').mean())}` | next_mom_negative_rate=`{format_float(pd.to_numeric(price_only['next_mom_negative_flag'], errors='coerce').mean())}`"
        )
        lines.append(
            f"- `both_weak_down` count=`{len(both)}` | next_mom_mean=`{format_float(pd.to_numeric(both['next_direct_mom12_return'], errors='coerce').mean())}` | next_mom_negative_rate=`{format_float(pd.to_numeric(both['next_mom_negative_flag'], errors='coerce').mean())}`"
        )

        lines.extend(
            [
                "",
                "Interpretation:",
                "- if deterioration weak-down months are followed by worse next-month momentum conditions than non-weak months, the deterioration signal is usable as a down-entry warning candidate",
                "- if deterioration-only weak-down months are already weak on the next step, that supports the idea that fundamental worsening can warn before price-state confirmation",
                "- if price-only weak-down months are weaker instead, price-state is still the faster entry sensor",
            ]
        )

    lines.extend(["", "Outputs:", f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})"])
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    signal_df = build_signal_frame()
    pair_df = build_pair_frame(signal_df)
    write_csv(OUT_DETAIL_PATH, pair_df)
    write_summary(signal_df, pair_df)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
