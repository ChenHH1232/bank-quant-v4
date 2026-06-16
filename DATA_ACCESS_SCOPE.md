# DATA_ACCESS_SCOPE

## Tushare

Updated: 2026-06-15

User-reported account state:

- Tushare points: 2000
- Token is stored separately in the vault and should not be copied into this project

Based on the official Tushare permission docs:

- With `2000+` points, the account gets:
  - `200` requests per minute
  - `100000` total calls per day per API
  - access to APIs whose required point threshold is `<= 2000`
- Tushare points are a permission threshold, not a consumable credit balance

Practical scope for this V4 project:

- Available core market/fundamental data should include APIs with a `2000` threshold, such as:
  - `daily`
  - `weekly`
  - `monthly`
  - `pro_bar` for supported daily/weekly/monthly style use cases noted by Tushare
  - `daily_basic`
  - `top_list`
  - `top_inst`
  - `pledge_detail`
  - `pledge_stat`
  - `margin`
  - `margin_detail`
  - `repurchase`
  - `block_trade`
  - `stk_holdernumber`
  - `moneyflow`
  - `stk_holdertrade`
  - `stk_limit`
  - `hk_hold`
  - `income`
  - `balancesheet`
  - `cashflow`
  - `forecast`
  - `express`
  - `dividend`
  - `fina_indicator`
  - `fina_audit`
  - `fina_mainbz`
  - `disclosure_date`
  - `fund_basic`
  - `fund_company`
  - `fund_nav`
  - `fund_daily`
  - `fund_div`
  - `fund_portfolio`

Current known Tushare limitations for V4:

- APIs requiring more than `2000` points should be treated as unavailable by default
  - example: `share_float` needs `3000`
  - example: `fund_adj` needs `5000+`
- Minute data is **not** covered by points and needs separate permission
- Hong Kong / U.S. market standalone products are **not** covered by points and need separate permission
- News, announcements, policy library, research report library, realtime products, and other standalone permissions are **not** covered by points

Implementation rule for V4:

- Default provider preference:
  - A-share daily market and fundamental research: Tushare can be used directly within the 2000-point scope
  - Data outside the 2000-point Tushare scope should be blocked unless another approved source is available
- Before adding a new Tushare API to the pipeline, verify that its official minimum point requirement is `<= 2000` or that separate permission has already been confirmed

## JoinQuant

User-reported account state:

- Purchased package: `沪深股票基础版`
- Package price reference: `6999` per year

Practical JoinQuant scope for V4:

- The purchased package should be treated as an approved paid source for Shanghai/Shenzhen stock research data
- Confirmed or strongly indicated by the user-provided package screenshot:
  - `auth license`: `1`
  - daily total quota: about `5000 万` rows
  - history coverage: `2005 至今`
  - data granularity: primarily `日频`
- Included categories should cover at least:
  - all-market common utilities
    - trading calendar
    - security code conversion / aggregation helpers
    - instrument list
    - instrument metadata common interfaces
  - Shanghai/Shenzhen A-share basic data
    - stock list data
    - trading statistics
    - ex-right / ex-dividend related data
    - industry concept and component-stock data
    - northbound / southbound and HK connect market data
    - basic market data for A-shares
  - Shanghai/Shenzhen A-share fundamentals
    - standalone financial statement data
    - report-period financial data
    - listed company basic fundamental data
  - Shanghai/Shenzhen index data
    - index行情-related daily data
    - index constituents
    - index weights
  - fund data
    - basic fund data
    - off-exchange fund statistics

Current known JoinQuant limitations for V4:

- Treat this package as `沪深股票日频研究优先` rather than minute-data coverage
- Do **not** assume minute-level stock/index/fund data is available under this package unless separately verified in the active account
- Do **not** assume convertible bond, futures, options, Hong Kong, or U.S. market data are included unless separately verified
- Do **not** assume unlimited concurrency; current known `auth license` count is `1`

Operational interpretation for V4:

- JoinQuant should be treated as the preferred paid source for covered Shanghai/Shenzhen stock daily-frequency data and A-share fundamentals
- For daily A-share market/fundamental research tasks, JoinQuant may be preferred when Tushare point limits, field coverage, or update behavior are not ideal
- Exact endpoint-level availability should still be verified against the active JoinQuant account before production use
- Where package-level screenshots are the basis for a capability claim, mark that capability as `confirmed by user package evidence` rather than `fully endpoint-verified`

## Sources

- Tushare permission and rate table: https://tushare.pro/document/1?doc_id=290
- Tushare API point thresholds: https://tushare.pro/document/1?doc_id=108
- Tushare minute-data note: https://tushare.pro/document/1?doc_id=234
- JoinQuant JQData package reference page: https://www.joinquant.com/help/api/doc?name=JQDatadoc&id=10868
- JoinQuant package coverage details above are inferred from the user-provided package screenshot plus the referenced JQData page
