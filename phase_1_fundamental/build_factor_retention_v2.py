import csv
import math
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
WHITELIST_PATH = SCRIPT_DIR / "model_field_whitelist_v1.csv"
PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
DECISION_PATH = SCRIPT_DIR / "factor_dedup_decision_v2.csv"
OUTPUT_RETAINED_PATH = SCRIPT_DIR / "retained_factor_shortlist_v2.csv"
OUTPUT_BACKLOG_PATH = SCRIPT_DIR / "derived_factor_backlog_v2.csv"
SUMMARY_PATH = SCRIPT_DIR / "retained_factor_shortlist_v2.md"


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_panel_header(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        return set(next(reader))


def build_decision_maps(rows: list[dict[str, str]]) -> tuple[set[str], set[str], list[dict[str, str]]]:
    drop_fields: set[str] = set()
    keep_fields: set[str] = set()
    derive_rows: list[dict[str, str]] = []
    for row in rows:
        decision_type = row["decision_type"]
        action = row["action"]
        name = row["factor_name_or_cluster"]
        if decision_type == "keep" and action == "keep_core":
            keep_fields.add(name)
        elif decision_type == "drop":
            drop_fields.add(name)
        elif decision_type == "derive":
            derive_rows.append(row)
    return keep_fields, drop_fields, derive_rows


def infer_panel_column(statement_family: str, field_name: str) -> str:
    return f"{statement_family}__{field_name}"


def build_retained_rows(
    whitelist_rows: list[dict[str, str]],
    panel_header: set[str],
    keep_fields: set[str],
    drop_fields: set[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in whitelist_rows:
        statement_family = row["statement_family"]
        field_name = row["field_name"]
        panel_column = infer_panel_column(statement_family, field_name)
        if panel_column not in panel_header:
            continue

        action = "keep"
        rationale = "not flagged by v2 dedup decisions"
        transformed_form = ""

        if panel_column in drop_fields:
            action = "drop"
            rationale = "explicitly removed by v2 dedup decision"
        elif panel_column in keep_fields:
            action = "keep_core"
            rationale = "explicitly retained by v2 dedup decision"
            if panel_column == "balance__total_assets":
                transformed_form = "log(balance__total_assets)"
        elif statement_family == "bank_indicator":
            action = "keep_core"
            rationale = "bank-specific annual field retained unless explicitly dropped"

        rows.append(
            {
                "statement_family": statement_family,
                "field_name": field_name,
                "panel_column": panel_column,
                "tier_v1": row["tier"],
                "v2_action": action,
                "transformed_form": transformed_form,
                "rationale": rationale,
            }
        )
    return rows


def capability_status(expression: str, panel_header: set[str]) -> tuple[str, str]:
    if expression == "cash_flow__staff_behalf_paid / income__operating_revenue":
        required = ["cash_flow__staff_behalf_paid", "income__operating_revenue"]
    elif expression == "cash_flow__staff_behalf_paid / average_total_assets":
        required = ["cash_flow__staff_behalf_paid", "balance__total_assets"]
    elif expression == "income__investment_income / average_investment_assets":
        required = ["income__investment_income"]
    elif expression == "income__investment_income / income__operating_revenue":
        required = ["income__investment_income", "income__operating_revenue"]
    else:
        required = []

    missing = [name for name in required if name not in panel_header]
    if missing:
        return "blocked_missing_inputs", ", ".join(missing)

    if expression == "income__investment_income / average_investment_assets":
        return (
            "blocked_need_new_denominator",
            "investment asset denominator not present in current panel header; needs new source/definition",
        )
    if expression == "cash_flow__staff_behalf_paid / average_total_assets":
        return (
            "ready_with_construction_rule",
            "requires lag/average total-assets construction from panel history",
        )
    return "ready_now", ""


def build_backlog_rows(derive_rows: list[dict[str, str]], panel_header: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in derive_rows:
        expression = row["factor_name_or_cluster"]
        status, note = capability_status(expression, panel_header)
        rows.append(
            {
                "cluster_id": row["cluster_id"],
                "derived_expression": expression,
                "priority": "preferred" if row["action"] == "derive_preferred" else ("fallback" if row["action"] == "derive_fallback" else "candidate"),
                "capability_status": status,
                "notes": note or row["notes"],
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(retained_rows: list[dict[str, str]], backlog_rows: list[dict[str, str]]) -> None:
    keep_core = sum(1 for row in retained_rows if row["v2_action"] == "keep_core")
    keep_regular = sum(1 for row in retained_rows if row["v2_action"] == "keep")
    drop_count = sum(1 for row in retained_rows if row["v2_action"] == "drop")

    lines = [
        "# Retained Factor Shortlist V2",
        "",
        "Summary:",
        f"- keep_core: `{keep_core}`",
        f"- keep_regular: `{keep_regular}`",
        f"- drop: `{drop_count}`",
        "",
        "Core manual v2 overrides:",
        "- keep `log(balance__total_assets)` as the size representative",
        "- keep `indicator__inc_net_profit_to_shareholders_annual`",
        "- keep `indicator__roe`",
        "- delete clusters `Q02`, `Q05`, `Q07`",
        "- rebuild cluster `Q06` before reuse",
        "",
        "Derived backlog capability:",
    ]
    if not backlog_rows:
        lines.append("- none")
    else:
        for row in backlog_rows:
            lines.append(
                f"- `{row['derived_expression']}` | status=`{row['capability_status']}` | {row['notes']}"
            )
    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_RETAINED_PATH.name}]({OUTPUT_RETAINED_PATH})",
            f"- [{OUTPUT_BACKLOG_PATH.name}]({OUTPUT_BACKLOG_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    whitelist_rows = load_csv_rows(WHITELIST_PATH)
    decision_rows = load_csv_rows(DECISION_PATH)
    panel_header = build_panel_header(PANEL_PATH)
    keep_fields, drop_fields, derive_rows = build_decision_maps(decision_rows)

    retained_rows = build_retained_rows(whitelist_rows, panel_header, keep_fields, drop_fields)
    backlog_rows = build_backlog_rows(derive_rows, panel_header)

    write_csv(OUTPUT_RETAINED_PATH, retained_rows)
    write_csv(OUTPUT_BACKLOG_PATH, backlog_rows)
    write_summary(retained_rows, backlog_rows)

    print(f"retained_rows={len(retained_rows)}")
    print(f"backlog_rows={len(backlog_rows)}")
    print(OUTPUT_RETAINED_PATH)
    print(OUTPUT_BACKLOG_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
