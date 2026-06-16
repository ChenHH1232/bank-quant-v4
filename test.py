from pprint import pprint

from data_provider_router import (
    is_joinquant_domain_allowed,
    is_tushare_api_allowed,
    preferred_provider,
    provider_reason,
)
from provider_capabilities import summarize_provider_caps


def main() -> None:
    pprint(summarize_provider_caps())
    print()
    print("preferred_provider(a_share_daily_market) =", preferred_provider("a_share_daily_market"))
    print("reason =", provider_reason("a_share_daily_market"))
    print("tushare daily_basic allowed =", is_tushare_api_allowed("daily_basic"))
    print("tushare fund_adj allowed =", is_tushare_api_allowed("fund_adj"))
    print("joinquant a_share_fundamentals allowed =", is_joinquant_domain_allowed("a_share_fundamentals"))
    print("joinquant minute_stock_data allowed =", is_joinquant_domain_allowed("minute_stock_data"))


if __name__ == "__main__":
    main()
