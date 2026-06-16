from dataclasses import dataclass


@dataclass(frozen=True)
class TushareCapabilities:
    points: int
    requests_per_minute: int
    daily_limit_per_api: int
    allowed_apis: frozenset[str]
    blocked_apis: frozenset[str]
    notes: tuple[str, ...]

    def can_access(self, api_name: str) -> bool:
        return api_name in self.allowed_apis

    def is_blocked_by_default(self, api_name: str) -> bool:
        return api_name in self.blocked_apis


@dataclass(frozen=True)
class JoinQuantCapabilities:
    package_name: str
    annual_price_cny: int
    auth_license_count: int
    daily_quota_rows: int
    history_start_year: int
    primary_frequency: str
    covered_domains: frozenset[str]
    blocked_domains: frozenset[str]
    notes: tuple[str, ...]

    def covers(self, domain_name: str) -> bool:
        return domain_name in self.covered_domains

    def is_blocked_by_default(self, domain_name: str) -> bool:
        return domain_name in self.blocked_domains


TUSHARE_2000_POINT_CAPS = TushareCapabilities(
    points=2000,
    requests_per_minute=200,
    daily_limit_per_api=100000,
    allowed_apis=frozenset(
        {
            "daily",
            "weekly",
            "monthly",
            "pro_bar",
            "daily_basic",
            "top_list",
            "top_inst",
            "pledge_detail",
            "pledge_stat",
            "margin",
            "margin_detail",
            "repurchase",
            "block_trade",
            "stk_holdernumber",
            "moneyflow",
            "stk_holdertrade",
            "stk_limit",
            "hk_hold",
            "income",
            "balancesheet",
            "cashflow",
            "forecast",
            "express",
            "dividend",
            "fina_indicator",
            "fina_audit",
            "fina_mainbz",
            "disclosure_date",
            "fund_basic",
            "fund_company",
            "fund_nav",
            "fund_daily",
            "fund_div",
            "fund_portfolio",
        }
    ),
    blocked_apis=frozenset(
        {
            "share_float",
            "fund_adj",
            "stk_mins",
            "news",
            "major_news",
            "npr",
        }
    ),
    notes=(
        "Tushare points are a permission threshold, not a consumable balance.",
        "Minute data is not included in the 2000-point scope.",
        "News, announcements, and other standalone products need separate permission.",
    ),
)


JOINQUANT_BASIC_A_SHARE_CAPS = JoinQuantCapabilities(
    package_name="hs_stock_basic",
    annual_price_cny=6999,
    auth_license_count=1,
    daily_quota_rows=50_000_000,
    history_start_year=2005,
    primary_frequency="daily",
    covered_domains=frozenset(
        {
            "trading_calendar",
            "security_code_mapping",
            "instrument_list",
            "instrument_metadata",
            "a_share_basic_market_data",
            "a_share_trading_statistics",
            "a_share_ex_rights",
            "industry_and_concept_membership",
            "hk_connect_market_data",
            "a_share_fundamentals",
            "report_period_financials",
            "listed_company_basics",
            "cn_index_daily_data",
            "cn_index_constituents",
            "cn_index_weights",
            "fund_basic_data",
            "off_exchange_fund_statistics",
        }
    ),
    blocked_domains=frozenset(
        {
            "minute_stock_data",
            "minute_index_data",
            "minute_fund_data",
            "convertible_bond_data",
            "futures_data",
            "options_data",
            "hk_market_full_scope",
            "us_market_data",
        }
    ),
    notes=(
        "Treat this package as Shanghai/Shenzhen stock daily-frequency research first.",
        "Do not assume minute data is available unless separately verified.",
        "Do not assume domain coverage outside the package screenshot without endpoint verification.",
    ),
)


def summarize_provider_caps() -> dict[str, object]:
    return {
        "tushare": {
            "points": TUSHARE_2000_POINT_CAPS.points,
            "requests_per_minute": TUSHARE_2000_POINT_CAPS.requests_per_minute,
            "daily_limit_per_api": TUSHARE_2000_POINT_CAPS.daily_limit_per_api,
            "allowed_api_count": len(TUSHARE_2000_POINT_CAPS.allowed_apis),
            "blocked_api_count": len(TUSHARE_2000_POINT_CAPS.blocked_apis),
        },
        "joinquant": {
            "package_name": JOINQUANT_BASIC_A_SHARE_CAPS.package_name,
            "annual_price_cny": JOINQUANT_BASIC_A_SHARE_CAPS.annual_price_cny,
            "auth_license_count": JOINQUANT_BASIC_A_SHARE_CAPS.auth_license_count,
            "daily_quota_rows": JOINQUANT_BASIC_A_SHARE_CAPS.daily_quota_rows,
            "history_start_year": JOINQUANT_BASIC_A_SHARE_CAPS.history_start_year,
            "primary_frequency": JOINQUANT_BASIC_A_SHARE_CAPS.primary_frequency,
            "covered_domain_count": len(JOINQUANT_BASIC_A_SHARE_CAPS.covered_domains),
            "blocked_domain_count": len(JOINQUANT_BASIC_A_SHARE_CAPS.blocked_domains),
        },
    }
