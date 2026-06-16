from provider_capabilities import (
    JOINQUANT_BASIC_A_SHARE_CAPS,
    TUSHARE_2000_POINT_CAPS,
)


DATASET_KIND_TO_PROVIDER = {
    "a_share_daily_market": "joinquant",
    "a_share_fundamental": "joinquant",
    "a_share_trading_statistics": "joinquant",
    "cn_index_daily": "joinquant",
    "fund_basic_daily": "joinquant",
    "tushare_point_scope_general": "tushare",
    "minute_market": None,
    "us_market": None,
    "hk_market_full": None,
    "news_sentiment": None,
}


def preferred_provider(dataset_kind: str) -> str | None:
    return DATASET_KIND_TO_PROVIDER.get(dataset_kind)


def provider_reason(dataset_kind: str) -> str:
    if dataset_kind in {
        "a_share_daily_market",
        "a_share_fundamental",
        "a_share_trading_statistics",
        "cn_index_daily",
        "fund_basic_daily",
    }:
        return (
            "Prefer JoinQuant because the active package covers Shanghai/Shenzhen "
            "daily-frequency stock, index, fund, and fundamental research better."
        )

    if dataset_kind == "tushare_point_scope_general":
        return (
            "Prefer Tushare when the API is inside the confirmed 2000-point scope "
            "and JoinQuant package coverage is not the better fit."
        )

    if dataset_kind in {"minute_market", "us_market", "hk_market_full", "news_sentiment"}:
        return (
            "Blocked by default because current confirmed permissions do not cover "
            "this dataset kind."
        )

    return "No routing rule has been defined for this dataset kind yet."


def is_tushare_api_allowed(api_name: str) -> bool:
    return TUSHARE_2000_POINT_CAPS.can_access(api_name)


def is_joinquant_domain_allowed(domain_name: str) -> bool:
    return JOINQUANT_BASIC_A_SHARE_CAPS.covers(domain_name)
