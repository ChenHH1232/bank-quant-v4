from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PAIR_PATH = SCRIPT_DIR / "deterioration_weakdown_entry_validation_v1_detail.csv"
OUT_DETAIL_PATH = SCRIPT_DIR / "two_stage_weakdown_entry_validation_v1_detail.csv"
OUT_SUMMARY_PATH = SCRIPT_DIR / "two_stage_weakdown_entry_validation_v1.md"


def load_pair_df() -> pd.DataFrame:
    df = pd.read_csv(PAIR_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    for col in [
        "direct_mom12_return",
        "next_direct_mom12_return",
        "price_weak_down",
        "deterioration_weak_down",
        "next_mom_negative_flag",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values(["fold_id", "rebalance_date"]).reset_index(drop=True)


def build_detail(df: pd.DataFrame) -> pd.DataFrame:
    out_rows: list[dict[str, object]] = []
    for fold_id, group in df.groupby("fold_id", sort=True):
        group = group.sort_values("rebalance_date").reset_index(drop=True).copy()
        warning_active = 0
        for idx, row in group.iterrows():
            current_warning = int(row["deterioration_weak_down"] == 1)
            current_price = int(row["price_weak_down"] == 1)
            two_stage_confirm = int((warning_active == 1 or current_warning == 1) and current_price == 1)
            if current_warning == 1:
                warning_active = 1
            if two_stage_confirm == 1:
                warning_active = 0

            out_rows.append(
                {
                    "fold_id": fold_id,
                    "rebalance_date": row["rebalance_date"].strftime("%Y-%m-%d"),
                    "validation_start": row["validation_start"],
                    "validation_end": row["validation_end"],
                    "direct_mom12_return": row["direct_mom12_return"],
                    "next_direct_mom12_return": row["next_direct_mom12_return"],
                    "next_mom_negative_flag": row["next_mom_negative_flag"],
                    "price_weak_down": current_price,
                    "deterioration_weak_down": current_warning,
                    "warning_active_before_price_check": int((warning_active == 1) or (current_warning == 1)),
                    "two_stage_confirmed_weak_down": two_stage_confirm,
                }
            )
    return pd.DataFrame(out_rows)


def summarize_signal(detail_df: pd.DataFrame, signal_col: str, signal_name: str) -> dict[str, object]:
    eval_df = detail_df.dropna(subset=["next_direct_mom12_return"]).copy()
    on_df = eval_df[eval_df[signal_col] == 1].copy()
    off_df = eval_df[eval_df[signal_col] == 0].copy()
    return {
        "signal_name": signal_name,
        "count": int(len(on_df)),
        "total_eval_count": int(len(eval_df)),
        "next_mom_mean_on": pd.to_numeric(on_df["next_direct_mom12_return"], errors="coerce").mean(),
        "next_mom_mean_off": pd.to_numeric(off_df["next_direct_mom12_return"], errors="coerce").mean(),
        "next_mom_negative_rate_on": pd.to_numeric(on_df["next_mom_negative_flag"], errors="coerce").mean(),
        "next_mom_negative_rate_off": pd.to_numeric(off_df["next_mom_negative_flag"], errors="coerce").mean(),
    }


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


def write_summary(detail_df: pd.DataFrame) -> None:
    lines = [
        "# Two-Stage Weak-Down Entry Validation V1",
        "",
        "Objective:",
        "- test a minimal two-stage weak-down entry rule",
        "- stage 1 = deterioration proxy raises a warning",
        "- stage 2 = price-state proxy confirms the weak-down entry",
        "- compare this rule against pure price and pure deterioration entry signals",
        "",
        "Rule:",
        "- if deterioration proxy enters `weak_down`, a warning becomes active",
        "- if price proxy later enters `weak_down` while warning is active, confirm `weak_down`",
        "- warning resets after a confirmation event",
        "",
    ]

    summaries = [
        summarize_signal(detail_df, "price_weak_down", "price_only"),
        summarize_signal(detail_df, "deterioration_weak_down", "deterioration_only"),
        summarize_signal(detail_df, "two_stage_confirmed_weak_down", "two_stage_confirmed"),
    ]

    lines.append("Signal summary:")
    for row in summaries:
        lines.append(
            f"- `{row['signal_name']}` | count=`{int(row['count'])}` / `{int(row['total_eval_count'])}` | "
            f"next_mom_on=`{format_float(row['next_mom_mean_on'])}` vs off=`{format_float(row['next_mom_mean_off'])}` | "
            f"next_mom_negative_rate_on=`{format_float(row['next_mom_negative_rate_on'])}` vs off=`{format_float(row['next_mom_negative_rate_off'])}`"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "- if `two_stage_confirmed` keeps the downside precision of `price_only` while reducing false early triggers from `deterioration_only`, the two-stage rule is a better weak-down entry candidate",
            "- if `two_stage_confirmed` becomes too sparse or loses downside precision, pure price confirmation remains better for actual weak-down entry",
            "",
            "Output:",
            f"- [{OUT_DETAIL_PATH.name}]({OUT_DETAIL_PATH})",
        ]
    )
    OUT_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = load_pair_df()
    detail_df = build_detail(df)
    write_csv(OUT_DETAIL_PATH, detail_df)
    write_summary(detail_df)
    print(OUT_DETAIL_PATH)
    print(OUT_SUMMARY_PATH)


if __name__ == "__main__":
    main()
