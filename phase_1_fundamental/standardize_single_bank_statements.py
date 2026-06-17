import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RAW_ROOT = SCRIPT_DIR / "raw_downloads" / "all_banks"
DEFAULT_OUTPUT_ROOT = SCRIPT_DIR / "standardized_outputs"
UNIVERSE_PATH = DEFAULT_RAW_ROOT / "bank_universe.csv"
WINDOW_START = pd.Timestamp("2014-01-01")
WINDOW_END = pd.Timestamp("2026-05-01")

INCOME_FIELDS = [
    "operating_revenue",
    "interest_income",
    "interest_expense",
    "commission_income",
    "commission_expense",
    "asset_impairment_loss",
    "credit_impairment_loss",
    "investment_income",
    "operating_profit",
    "total_profit",
    "income_tax_expense",
    "net_profit",
    "np_parent_company_owners",
    "minority_profit",
]

CASH_FLOW_FIELDS = [
    "net_deposit_increase",
    "net_borrowing_from_central_bank",
    "net_borrowing_from_finance_co",
    "interest_and_commission_cashin",
    "net_increase_in_placements",
    "net_buyback",
    "tax_levy_refund",
    "goods_and_services_cash_paid",
    "net_loan_and_advance_increase",
    "net_deposit_in_cb_and_ib",
    "original_compensation_paid",
    "policy_dividend_cash_paid",
    "staff_behalf_paid",
    "tax_payments",
    "subtotal_operate_cash_inflow",
    "subtotal_operate_cash_outflow",
    "net_operate_cash_flow",
    "invest_withdrawal_cash",
    "invest_proceeds",
    "fix_intan_other_asset_acqui_cash",
    "invest_cash_paid",
    "impawned_loan_net_increase",
    "subtotal_invest_cash_inflow",
    "subtotal_invest_cash_outflow",
    "net_invest_cash_flow",
    "cash_from_invest",
    "cash_from_bonds_issue",
    "cash_from_borrowing",
    "subtotal_finance_cash_inflow",
    "borrowing_repayment",
    "dividend_interest_payment",
    "subtotal_finance_cash_outflow",
    "net_finance_cash_flow",
    "exchange_rate_change_effect",
    "cash_equivalent_increase",
    "cash_equivalents_at_beginning",
    "cash_and_equivalents_at_end",
]

INDICATOR_FIELDS = [
    "eps",
    "adjusted_profit",
    "operating_profit",
    "value_change_profit",
    "roe",
    "inc_return",
    "roa",
    "net_profit_margin",
    "gross_profit_margin",
    "expense_to_total_revenue",
    "operation_profit_to_total_revenue",
    "net_profit_to_total_revenue",
    "operating_expense_to_total_revenue",
    "ga_expense_to_total_revenue",
    "financing_expense_to_total_revenue",
    "operating_profit_to_profit",
    "invesment_profit_to_profit",
    "adjusted_profit_to_profit",
    "goods_sale_and_service_to_revenue",
    "ocf_to_revenue",
    "ocf_to_operating_profit",
    "inc_total_revenue_year_on_year",
    "inc_total_revenue_annual",
    "inc_revenue_year_on_year",
    "inc_revenue_annual",
    "inc_operation_profit_year_on_year",
    "inc_operation_profit_annual",
    "inc_net_profit_year_on_year",
    "inc_net_profit_annual",
    "inc_net_profit_to_shareholders_year_on_year",
    "inc_net_profit_to_shareholders_annual",
]

BANK_INDICATOR_FIELDS = [
    "total_loan",
    "total_deposit",
    "interest_earning_assets",
    "non_interest_earning_assets",
    "interest_earning_assets_yield",
    "interest_bearing_liabilities",
    "non_interest_bearing_liabilities",
    "interest_bearing_liabilities_interest_rate",
    "non_interest_income",
    "non_interest_income_ratio",
    "net_interest_margin",
    "net_profit_margin",
    "core_level_capital",
    "net_core_level_capital",
    "core_level_capital_adequacy_ratio",
    "net_level_1_capital",
    "level_1_capital_adequacy_ratio",
    "net_capital",
    "capital_adequacy_ratio",
    "weighted_risky_asset",
    "deposit_loan_ratio",
    "short_term_asset_liquidity_ratio_CNY",
    "short_term_asset_liquidity_ratio_FC",
    "Nonperforming_loan_rate",
    "single_largest_customer_loan_ratio",
    "top_ten_customer_loan_ratio",
    "bad_debts_reserve",
    "non_performing_loan_provision_coverage",
    "cost_to_income_ratio",
    "former_core_capital",
    "former_net_core_capital",
    "former_net_core_capital_adequacy_ratio",
    "former_net_capital",
    "former_capital_adequacy_ratio",
    "former_weighted_risky_asset",
    "normal_amount",
    "normal_amount_ratio",
    "concerned_amount",
    "concerned_amount_ratio",
    "secondary_amount",
    "secondary_amount_ratio",
    "suspicious_amount",
    "suspicious_amount_ratio",
    "loss_amount",
    "loss_amount_ratio",
    "short_term_loan_average_balance",
    "short_term_loan_annualized_average_interest_rate",
    "mid_term_loan_annualized_average_balance",
    "mid_term_loan_annualized_average_interest_rate",
    "enterprise_deposits_average_balance",
    "enterprise_deposits_average_interest_rate",
    "savings_deposit_average_balance",
    "savings_deposit_average_interest_rate",
]

BALANCE_FIELDS = [
    "cash_equivalents",
    "settlement_provi",
    "lend_capital",
    "trading_assets",
    "bill_receivable",
    "account_receivable",
    "advance_payment",
    "insurance_receivables",
    "interest_receivable",
    "other_receivable",
    "bought_sellback_assets",
    "inventories",
    "other_current_assets",
    "total_current_assets",
    "loan_and_advance",
    "hold_for_sale_assets",
    "hold_to_maturity_investments",
    "longterm_equity_invest",
    "investment_property",
    "fixed_assets",
    "constru_in_process",
    "intangible_assets",
    "good_will",
    "long_deferred_expense",
    "deferred_tax_assets",
    "other_non_current_assets",
    "total_non_current_assets",
    "total_assets",
    "shortterm_loan",
    "borrowing_from_centralbank",
    "deposit_in_interbank",
    "borrowing_capital",
    "trading_liability",
    "notes_payable",
    "accounts_payable",
    "advance_peceipts",
    "sold_buyback_secu_proceeds",
    "commission_payable",
    "salaries_payable",
    "taxs_payable",
    "interest_payable",
    "other_payable",
    "insurance_contract_reserves",
    "proxy_secu_proceeds",
    "non_current_liability_in_one_year",
    "other_current_liability",
    "total_current_liability",
    "longterm_loan",
    "bonds_payable",
    "estimate_liability",
    "deferred_tax_liability",
    "other_non_current_liability",
    "total_non_current_liability",
    "total_liability",
    "paidin_capital",
    "capital_reserve_fund",
    "treasury_stock",
    "surplus_reserve_fund",
    "ordinary_risk_reserve_fund",
    "retained_profit",
    "equities_parent_company_owners",
    "minority_interests",
    "total_owner_equities",
    "other_comprehensive_income",
    "contract_assets",
    "contract_liability",
    "usufruct_assets",
]

PARENT_BALANCE_FIELDS = [
    "deposit_in_ib",
    "cash_equivalents",
    "deposit_client",
    "cash_in_cb",
    "settlement_provi",
    "settlement_provi_client",
    "lend_capital",
    "bought_sellback_assets",
    "interest_receivable",
    "insurance_receivables",
    "loan_and_advance",
    "advance_payment",
    "hold_for_sale_assets",
    "hold_to_maturity_investments",
    "longterm_equity_invest",
    "investment_property",
    "inventories",
    "fixed_assets",
    "constru_in_process",
    "intangible_assets",
    "long_deferred_expense",
    "deferred_tax_assets",
    "other_asset",
    "total_assets",
    "borrowing_from_centralbank",
    "shortterm_loan",
    "borrowing_capital",
    "sold_buyback_secu_proceeds",
    "proxy_secu_proceeds",
    "notes_payable",
    "advance_peceipts",
    "commission_payable",
    "salaries_payable",
    "taxs_payable",
    "interest_payable",
    "estimate_liability",
    "longterm_loan",
    "bonds_payable",
    "deferred_tax_liability",
    "other_liability",
    "total_liability",
    "paidin_capital",
    "capital_reserve_fund",
    "treasury_stock",
    "surplus_reserve_fund",
    "equities_parent_company_owners",
    "retained_profit",
    "minority_interests",
    "total_owner_equities",
    "other_comprehensive_income",
]


@dataclass
class StatementSourceConfig:
    statement_family: str
    primary_file: str
    fallback_file: str
    primary_period_col: str
    primary_pub_col: str
    fallback_period_col: str
    fallback_pub_col: str
    fields: list[str]
    period_mode: str = "quarterly_ytd"


SOURCE_CONFIGS = [
    StatementSourceConfig(
        statement_family="income",
        primary_file="finance_income_statement_current_only.csv",
        fallback_file="income.csv",
        primary_period_col="report_date",
        primary_pub_col="pub_date",
        fallback_period_col="statDate",
        fallback_pub_col="pubDate",
        fields=INCOME_FIELDS,
    ),
    StatementSourceConfig(
        statement_family="cash_flow",
        primary_file="finance_cashflow_statement_current_only.csv",
        fallback_file="cash_flow.csv",
        primary_period_col="report_date",
        primary_pub_col="pub_date",
        fallback_period_col="statDate",
        fallback_pub_col="pubDate",
        fields=CASH_FLOW_FIELDS,
    ),
    StatementSourceConfig(
        statement_family="indicator",
        primary_file="indicator.csv",
        fallback_file="indicator.csv",
        primary_period_col="statDate",
        primary_pub_col="pubDate",
        fallback_period_col="statDate",
        fallback_pub_col="pubDate",
        fields=INDICATOR_FIELDS,
        period_mode="quarterly_direct",
    ),
    StatementSourceConfig(
        statement_family="balance",
        primary_file="balance.csv",
        fallback_file="balance.csv",
        primary_period_col="statDate",
        primary_pub_col="pubDate",
        fallback_period_col="statDate",
        fallback_pub_col="pubDate",
        fields=BALANCE_FIELDS,
        period_mode="quarterly_direct",
    ),
    StatementSourceConfig(
        statement_family="parent_balance",
        primary_file="finance_balance_sheet_parent_current_only.csv",
        fallback_file="finance_balance_sheet_parent_current_only.csv",
        primary_period_col="report_date",
        primary_pub_col="pub_date",
        fallback_period_col="report_date",
        fallback_pub_col="pub_date",
        fields=PARENT_BALANCE_FIELDS,
        period_mode="quarterly_direct",
    ),
    StatementSourceConfig(
        statement_family="bank_indicator",
        primary_file="bank_indicator.csv",
        fallback_file="bank_indicator.csv",
        primary_period_col="statDate",
        primary_pub_col="pubDate",
        fallback_period_col="statDate",
        fallback_pub_col="pubDate",
        fields=BANK_INDICATOR_FIELDS,
        period_mode="annual_direct",
    ),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Standardize one bank's quarterly statement fields with missingness checks and audit logs."
    )
    parser.add_argument("--code", default="000001.XSHE", help="Bank code, default is Ping An Bank.")
    parser.add_argument("--raw-root", default=str(DEFAULT_RAW_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    return parser


def code_to_dir_name(code: str) -> str:
    return code.replace(".", "_")


def load_listing_date(code: str) -> pd.Timestamp | None:
    if not UNIVERSE_PATH.exists():
        return None
    universe = pd.read_csv(UNIVERSE_PATH)
    match = universe[universe["code"] == code]
    if match.empty:
        return None
    return pd.to_datetime(match.iloc[0]["start_date"])


def enrich_periods(df: pd.DataFrame, period_col: str, pub_col: str) -> pd.DataFrame:
    result = df.copy()
    result["report_period_end"] = pd.to_datetime(result[period_col])
    result["pub_date_std"] = pd.to_datetime(result[pub_col], errors="coerce")
    result["year"] = result["report_period_end"].dt.year
    result["quarter"] = result["report_period_end"].dt.quarter
    result["quarter_key"] = result["year"].astype(str) + "q" + result["quarter"].astype(str)
    return result


def build_period_lookup(df: pd.DataFrame) -> dict[str, pd.Series]:
    if df.empty:
        return {}
    deduped = df.sort_values("report_period_end").drop_duplicates("quarter_key", keep="last")
    return {row["quarter_key"]: row for _, row in deduped.iterrows()}


def quarter_key_from_timestamp(value: pd.Timestamp) -> str:
    return f"{value.year}q{value.quarter}"


def build_expected_periods(listing_date: pd.Timestamp | None) -> list[str]:
    start_date = max(WINDOW_START, listing_date) if listing_date is not None else WINDOW_START
    quarter_starts = pd.date_range(start=start_date, end=pd.Timestamp(f"{WINDOW_END.year}-12-31"), freq="QS")
    return [quarter_key_from_timestamp(ts) for ts in quarter_starts]


def build_expected_years(listing_date: pd.Timestamp | None) -> list[str]:
    start_year = max(WINDOW_START.year, listing_date.year) if listing_date is not None else WINDOW_START.year
    return [str(year) for year in range(start_year, WINDOW_END.year + 1)]


def previous_quarter_key(quarter_key: str) -> str | None:
    year = int(quarter_key[:4])
    quarter = int(quarter_key[-1])
    if quarter == 1:
        return None
    return f"{year}q{quarter - 1}"


def build_annual_lookup(df: pd.DataFrame) -> dict[str, pd.Series]:
    if df.empty:
        return {}
    result = df.copy()
    result["year_key"] = result["report_period_end"].dt.year.astype(str)
    deduped = result.sort_values("report_period_end").drop_duplicates("year_key", keep="last")
    return {row["year_key"]: row for _, row in deduped.iterrows()}


def pre_listing_or_not_expected(report_period_end: pd.Timestamp, listing_date: pd.Timestamp | None) -> bool:
    if listing_date is None:
        return False
    return report_period_end < listing_date


def standardize_statement_family(
    code: str,
    config: StatementSourceConfig,
    raw_root: Path,
    output_root: Path,
    listing_date: pd.Timestamp | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    bank_dir = raw_root / code_to_dir_name(code)
    primary_path = bank_dir / config.primary_file
    fallback_path = bank_dir / config.fallback_file
    primary_df = (
        enrich_periods(pd.read_csv(primary_path), config.primary_period_col, config.primary_pub_col)
        if primary_path.exists()
        else pd.DataFrame()
    )
    fallback_df = (
        enrich_periods(pd.read_csv(fallback_path), config.fallback_period_col, config.fallback_pub_col)
        if fallback_path.exists()
        else pd.DataFrame()
    )
    if config.period_mode == "annual_direct":
        primary_lookup = build_annual_lookup(primary_df)
        fallback_lookup = build_annual_lookup(fallback_df)
        expected_keys = build_expected_years(listing_date)
    else:
        primary_lookup = build_period_lookup(primary_df)
        fallback_lookup = build_period_lookup(fallback_df)
        expected_keys = build_expected_periods(listing_date)

    standardized_rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []

    for period_key in expected_keys:
        primary_row = primary_lookup.get(period_key)
        fallback_row = fallback_lookup.get(period_key)
        chosen_source_name = config.primary_file if primary_row is not None else config.fallback_file if fallback_row is not None else None
        chosen_row = primary_row if primary_row is not None else fallback_row
        if chosen_row is not None:
            report_period_end = pd.to_datetime(chosen_row["report_period_end"])
        else:
            if config.period_mode == "annual_direct":
                report_period_end = pd.Timestamp(f"{period_key}-12-31")
            else:
                year = int(period_key[:4])
                quarter = int(period_key[-1])
                month_day = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}[quarter]
                report_period_end = pd.Timestamp(f"{year}-{month_day}")
        pub_date = pd.to_datetime(chosen_row["pub_date_std"]) if chosen_row is not None else pd.NaT
        prev_key = previous_quarter_key(period_key) if config.period_mode == "quarterly_ytd" else None
        prev_primary_row = primary_lookup.get(prev_key) if prev_key else None
        prev_fallback_row = fallback_lookup.get(prev_key) if prev_key else None

        for field in config.fields:
            raw_primary_value = primary_row.get(field) if primary_row is not None and field in primary_row.index else None
            raw_fallback_value = fallback_row.get(field) if fallback_row is not None and field in fallback_row.index else None
            raw_value_used = None
            prior_value_used = None
            transformation_rule = "identity_q1_or_ytd_diff"
            conversion_success = False
            missing_reason = ""
            std_period_basis = ""
            std_value = None
            source_field = field

            if chosen_row is None:
                missing_reason = (
                    "pre_listing_or_not_expected"
                    if pre_listing_or_not_expected(report_period_end, listing_date)
                    else "outside_current_available_window"
                    if period_key in {"2026q2", "2026q3", "2026q4"}
                    else "provider_unavailable_annual_bank_indicator"
                    if config.period_mode == "annual_direct" and period_key in {"2024", "2025", "2026"}
                    else "missing_target_report"
                )
            elif field not in chosen_row.index:
                missing_reason = "source_specific_field_not_available"
            else:
                raw_value_used = chosen_row.get(field)
                if config.period_mode == "annual_direct":
                    if pd.isna(raw_value_used):
                        missing_reason = (
                            "provider_unavailable_annual_bank_indicator"
                            if period_key in {"2024", "2025", "2026"}
                            else "missing_raw_value"
                        )
                    else:
                        std_value = raw_value_used
                        std_period_basis = "annual_direct"
                        conversion_success = True
                elif config.period_mode == "quarterly_direct":
                    if pd.isna(raw_value_used):
                        missing_reason = "missing_raw_value"
                    else:
                        std_value = raw_value_used
                        std_period_basis = "quarterly_direct"
                        conversion_success = True
                else:
                    quarter_number = int(period_key[-1])
                    if quarter_number == 1:
                        if pd.isna(raw_value_used):
                            missing_reason = "missing_raw_value"
                        else:
                            std_value = raw_value_used
                            std_period_basis = "single_quarter"
                            conversion_success = True
                    else:
                        prior_row = prev_primary_row if chosen_source_name == config.primary_file else prev_fallback_row
                        if prior_row is None:
                            missing_reason = "missing_prior_cumulative_report"
                        elif field not in prior_row.index:
                            missing_reason = "source_specific_field_not_available"
                        else:
                            prior_value_used = prior_row.get(field)
                            if pd.isna(raw_value_used):
                                missing_reason = "missing_raw_value"
                            elif pd.isna(prior_value_used):
                                missing_reason = "missing_prior_cumulative_report"
                            else:
                                std_value = raw_value_used - prior_value_used
                                std_period_basis = "converted_from_ytd"
                                conversion_success = True

            standardized_rows.append(
                {
                    "code": code,
                    "statement_family": config.statement_family,
                    "report_period_end": report_period_end,
                    "quarter_key": period_key if config.period_mode != "annual_direct" else None,
                    "year_key": period_key if config.period_mode == "annual_direct" else None,
                    "pub_date": pub_date,
                    "standard_field_name": field,
                    "standard_value": std_value,
                    "source_table": chosen_source_name,
                    "source_field": source_field,
                    "period_basis": std_period_basis,
                    "transformation_rule": transformation_rule,
                    "missing_reason": missing_reason,
                }
            )

            audit_rows.append(
                {
                    "code": code,
                    "statement_family": config.statement_family,
                    "report_period_end": report_period_end,
                    "quarter_key": period_key if config.period_mode != "annual_direct" else None,
                    "year_key": period_key if config.period_mode == "annual_direct" else None,
                    "standard_field_name": field,
                    "source_table": chosen_source_name,
                    "source_field": source_field,
                    "raw_primary_value": raw_primary_value,
                    "raw_fallback_value": raw_fallback_value,
                    "raw_value_used": raw_value_used,
                    "prior_cumulative_value_used": prior_value_used,
                    "transformation_rule": transformation_rule,
                    "conversion_success": conversion_success,
                    "missing_reason": missing_reason,
                }
            )

    standardized_df = pd.DataFrame(standardized_rows)
    audit_df = pd.DataFrame(audit_rows)
    output_dir = output_root / code_to_dir_name(code)
    output_dir.mkdir(parents=True, exist_ok=True)
    standardized_df.to_csv(output_dir / f"{config.statement_family}_standardized.csv", index=False, encoding="utf-8-sig")
    audit_df.to_csv(output_dir / f"{config.statement_family}_audit.csv", index=False, encoding="utf-8-sig")
    return standardized_df, audit_df


def main() -> None:
    args = build_parser().parse_args()
    raw_root = Path(args.raw_root)
    output_root = Path(args.output_root)
    listing_date = load_listing_date(args.code)

    summary_rows: list[dict[str, object]] = []
    for config in SOURCE_CONFIGS:
        standardized_df, audit_df = standardize_statement_family(
            code=args.code,
            config=config,
            raw_root=raw_root,
            output_root=output_root,
            listing_date=listing_date,
        )
        summary_rows.append(
            {
                "statement_family": config.statement_family,
                "standardized_rows": len(standardized_df),
                "audit_rows": len(audit_df),
                "missing_rows": int(standardized_df["missing_reason"].fillna("").ne("").sum()),
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    output_dir = output_root / code_to_dir_name(args.code)
    summary_df.to_csv(output_dir / "standardization_summary.csv", index=False, encoding="utf-8-sig")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
