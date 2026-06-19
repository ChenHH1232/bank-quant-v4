from __future__ import annotations

from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_factor_panel_v2.csv"
OUT_CSV_PATH = SCRIPT_DIR / "mean_reversion_field_coverage_check_v1.csv"
OUT_MD_PATH = SCRIPT_DIR / "mean_reversion_field_coverage_check_v1.md"


FIELD_SPECS = [
    ("date", "base", "required", "raw field"),
    ("code", "base", "required", "raw field"),
    ("open", "base", "required", "raw field"),
    ("close", "base", "required", "raw field"),
    ("high", "base", "required", "raw field"),
    ("low", "base", "required", "raw field"),
    ("volume", "base", "required", "raw field"),
    ("money", "base", "required", "raw field"),
    ("turnover_ratio", "base", "required", "raw field"),
    ("market_cap", "base", "required", "raw field"),
    ("circulating_market_cap", "base", "recommended", "raw field"),
    ("pb_ratio", "base", "recommended", "raw field"),
    ("pe_ratio", "base", "recommended", "raw field"),
    ("listed_start", "base", "required", "raw field"),
    ("listed_trading_days", "base", "required", "raw field"),
    ("daily_return_close", "base", "recommended", "raw field"),
    ("rev_5d", "derived", "required", "derive from daily close"),
    ("rev_10d", "derived", "required", "derive from daily close"),
    ("rev_20d", "derived", "required", "derive from daily close"),
    ("excess_rev_5d", "derived", "recommended", "derive from rev_5d cross-section"),
    ("excess_rev_10d", "derived", "recommended", "derive from rev_10d cross-section"),
    ("close_to_ma20", "derived", "required", "derive from daily close"),
    ("intramonth_drawdown_20d", "derived", "recommended", "derive from close or high/close window"),
    ("avg_money_20d", "derived", "required", "derive from money"),
    ("avg_turnover_20d", "derived", "required", "derive from turnover_ratio"),
    ("avg_mcap_20d", "derived", "required", "derive from market_cap"),
    ("volatility_20d", "derived", "recommended", "derive from daily_return_close"),
    ("down_day_ratio_20d", "derived", "recommended", "derive from daily_return_close"),
    ("abnormal_volume_ratio", "derived", "optional", "derive from money or volume"),
    ("paused", "extra", "optional", "missing; only needed for stricter execution realism"),
    ("is_st", "extra", "optional", "missing; can be queried later"),
    ("high_limit", "extra", "optional", "missing; execution-layer enhancement"),
    ("low_limit", "extra", "optional", "missing; execution-layer enhancement"),
]


def load_columns() -> list[str]:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig", nrows=5)
    return df.columns.tolist()


def build_table(columns: list[str]) -> pd.DataFrame:
    rows = []
    column_set = set(columns)

    derivable_from_close = {"date", "code", "close"}
    derivable_from_money = {"date", "code", "money"}
    derivable_from_turnover = {"date", "code", "turnover_ratio"}
    derivable_from_mcap = {"date", "code", "market_cap"}
    derivable_from_return = {"date", "code", "daily_return_close"}
    derivable_from_high_low = {"date", "code", "high", "low", "close"}

    for field_name, field_group, priority, note in FIELD_SPECS:
        if field_group == "base":
            status = "present" if field_name in column_set else "missing"
        elif field_name in {"rev_5d", "rev_10d", "rev_20d", "close_to_ma20"}:
            status = "derivable" if derivable_from_close.issubset(column_set) else "missing"
        elif field_name in {"excess_rev_5d", "excess_rev_10d"}:
            status = "derivable" if derivable_from_close.issubset(column_set) else "missing"
        elif field_name in {"avg_money_20d", "abnormal_volume_ratio"}:
            status = "derivable" if derivable_from_money.issubset(column_set) else "missing"
        elif field_name == "avg_turnover_20d":
            status = "derivable" if derivable_from_turnover.issubset(column_set) else "missing"
        elif field_name == "avg_mcap_20d":
            status = "derivable" if derivable_from_mcap.issubset(column_set) else "missing"
        elif field_name in {"volatility_20d", "down_day_ratio_20d"}:
            status = "derivable" if derivable_from_return.issubset(column_set) else "missing"
        elif field_name == "intramonth_drawdown_20d":
            status = "derivable" if derivable_from_high_low.issubset(column_set) else "missing"
        else:
            status = "missing"

        rows.append(
            {
                "field_name": field_name,
                "field_group": field_group,
                "priority": priority,
                "status": status,
                "note": note,
            }
        )
    return pd.DataFrame(rows)


def write_summary(df: pd.DataFrame) -> None:
    present = int((df["status"] == "present").sum())
    derivable = int((df["status"] == "derivable").sum())
    missing_required = int(((df["priority"] == "required") & (df["status"] == "missing")).sum())

    lines = [
        "# Mean Reversion Field Coverage Check V1",
        "",
        "Scope:",
        "- source panel: `momentum_factor_panel_v2.csv`",
        "- data window target: keep the same research window as momentum, with formal pre-2021 research and later out-of-sample acceptance",
        "- purpose: determine whether the existing daily panel is already sufficient for first-pass mean-reversion research",
        "",
        "Coverage summary:",
        f"- present fields: `{present}`",
        f"- derivable fields: `{derivable}`",
        f"- missing required fields: `{missing_required}`",
        "",
        "Verdict:",
    ]

    if missing_required == 0:
        lines.append("- first-pass mean-reversion research can start without a new download")
        lines.append("- the current panel is already sufficient, because the required missing items are derivable from the existing daily price, return, liquidity, and size fields")
    else:
        lines.append("- there are still required field gaps before first-pass mean-reversion research can start")

    lines.extend(
        [
            "",
            "Still-missing but non-blocking fields:",
            "- `paused`, `is_st`, `high_limit`, `low_limit` are not in the current panel",
            "- these are execution-layer enhancements and should not block the first research pass",
            "",
            "Recommended next action:",
            "- build a mean-reversion factor panel directly from the current daily panel, without re-downloading data first",
            "",
            "Output:",
            f"- [{OUT_CSV_PATH.name}]({OUT_CSV_PATH})",
        ]
    )
    OUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    columns = load_columns()
    out = build_table(columns)
    out.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8-sig")
    write_summary(out)
    print(OUT_CSV_PATH)
    print(OUT_MD_PATH)


if __name__ == "__main__":
    main()
