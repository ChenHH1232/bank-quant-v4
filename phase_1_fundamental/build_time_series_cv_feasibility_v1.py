from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
OUTPUT_CSV_PATH = SCRIPT_DIR / "time_series_cv_feasibility_v1.csv"
OUTPUT_MD_PATH = SCRIPT_DIR / "time_series_cv_feasibility_v1.md"

RESEARCH_END = pd.Timestamp("2021-05-01")
TRAIN_YEARS = 5
TEST_YEARS = 2


def load_rebalance_dates() -> list[pd.Timestamp]:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig", usecols=["rebalance_date"])
    dates = sorted(pd.to_datetime(df["rebalance_date"]).unique())
    return [pd.Timestamp(d) for d in dates if pd.Timestamp(d) < RESEARCH_END]


def build_rows(dates: list[pd.Timestamp]) -> list[dict[str, object]]:
    if not dates:
        return []

    earliest = min(dates)
    latest = max(dates)
    full_required_end = earliest + pd.DateOffset(years=TRAIN_YEARS + TEST_YEARS)

    row = {
        "earliest_rebalance_date": earliest.strftime("%Y-%m-%d"),
        "latest_rebalance_date": latest.strftime("%Y-%m-%d"),
        "rebalance_date_count": len(dates),
        "required_window_years": TRAIN_YEARS + TEST_YEARS,
        "required_window_end_if_start_at_earliest": full_required_end.strftime("%Y-%m-%d"),
        "research_end_limit": RESEARCH_END.strftime("%Y-%m-%d"),
        "full_5y_train_2y_test_cv_feasible": int(full_required_end <= RESEARCH_END),
        "note": (
            "feasible"
            if full_required_end <= RESEARCH_END
            else "not feasible because usable pre-2021 rebalance dates span less than 7 full years"
        ),
    }
    return [row]


def write_outputs(rows: list[dict[str, object]], dates: list[pd.Timestamp]) -> None:
    pd.DataFrame(rows).to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")

    if dates:
        earliest = min(dates).strftime("%Y-%m-%d")
        latest = max(dates).strftime("%Y-%m-%d")
        full_required_end = (min(dates) + pd.DateOffset(years=TRAIN_YEARS + TEST_YEARS)).strftime("%Y-%m-%d")
        feasible = rows[0]["full_5y_train_2y_test_cv_feasible"] == 1
    else:
        earliest = ""
        latest = ""
        full_required_end = ""
        feasible = False

    lines = [
        "# Time-Series CV Feasibility V1",
        "",
        "Requested protocol:",
        f"- training window: `{TRAIN_YEARS}` years",
        f"- test window: `{TEST_YEARS}` years",
        f"- research must end before: `{RESEARCH_END.strftime('%Y-%m-%d')}`",
        "",
        "Observed usable pre-2021 rebalance sample:",
        f"- earliest rebalance date: `{earliest}`",
        f"- latest rebalance date: `{latest}`",
        f"- rebalance date count: `{len(dates)}`",
        "",
        "Feasibility check:",
        f"- if the first fold starts at `{earliest}`, a full 5y+2y window would end at `{full_required_end}`",
        f"- strict 5y-train / 2y-test pre-2021 CV feasible: `{feasible}`",
        "",
        "Conclusion:",
    ]

    if feasible:
        lines.append("- full pre-2021 time-series CV is feasible under the requested 5y/2y rule")
    else:
        lines.append("- full pre-2021 time-series CV is not feasible with the current panel because the usable rebalance history starts too late")
        lines.append("- this means we cannot build multiple strict 5y-train / 2y-test folds without either")
        lines.append("  using post-2021 data for research, or relaxing the window definition")

    lines.extend(
        [
            "",
            "Output:",
            f"- [{OUTPUT_CSV_PATH.name}]({OUTPUT_CSV_PATH})",
        ]
    )
    OUTPUT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    dates = load_rebalance_dates()
    rows = build_rows(dates)
    write_outputs(rows, dates)
    print(OUTPUT_CSV_PATH)
    print(OUTPUT_MD_PATH)


if __name__ == "__main__":
    main()
