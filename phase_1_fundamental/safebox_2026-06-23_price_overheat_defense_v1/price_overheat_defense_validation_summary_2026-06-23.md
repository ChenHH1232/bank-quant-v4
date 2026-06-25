# Price Overheat Defense Validation Summary 2026-06-23

Scope:
- evaluate whether pure fundamental `base_core_6 + top_08` can be improved by capping only overheated stocks
- use `price overheat + weak fundamental improvement` instead of market-cap overheat because JoinQuant intraday market cap was not reliably available before `15:00`

Research hypothesis:
- record each selected stock's rebalance-day entry price
- before the next rebalance, allow only sell-down if:
- the stock price rises too fast relative to entry
- and its fundamentals did not improve enough at entry
- released weight remains in cash

Rolling design:
- mother shell = `base_core_6`
- combo = `ic_weight_train`
- selection = top bucket
- price trigger tested = `15% / 20%`
- cap tested = `15% / 10%`
- weak-improvement threshold tested = `improve_count <= 1 / 2`
- minimum available improvement signals = `3`

Rolling baseline:
- mean train/test/review cum = `0.870620 / 0.365221 / 0.058546`

Best rolling candidate:
- config = `price_hot_no_fund_improve__trigger_20__cap_010__maximp_1`
- mean train/test/review cum = `0.997475 / 0.368580 / 0.061228`
- delta test vs baseline = `+0.003359`
- delta review vs baseline = `+0.002681`

Interpretation of rolling:
- the signal looked directionally better than the earlier market-cap-overheat version
- but the edge was very small
- the improvement was not large enough to treat rolling alone as confirmation

JoinQuant executable candidate:
- file = `joinquant_v4_annual_backtest_strategy_base_core_6_price_overheat_without_fundamental_improve_v1.py`
- implementation records entry price on rebalance day and compares it with current price during the holding window
- only stocks that are both price-overheated and weak on fundamental improvement are capped

JoinQuant confirmation result:
- strategy return = `48.38%`
- annualized return = `8.49%`
- excess return = `23.80%`
- alpha = `0.047`
- beta = `1.053`
- sharpe = `0.233`
- max drawdown = `22.29%`
- information ratio = `0.616`
- max drawdown window = `2022/04/15,2022/10/31`

Conclusion:
- the JoinQuant result was essentially unchanged from the current preferred pure-fundamental main candidate
- therefore the rolling edge did not convert into a meaningful full-period executable improvement
- this branch should be archived as a research-positive but acceptance-failed defensive variant

Decision:
- keep current preferred pure-fundamental line unchanged
- do not promote price-overheat defense into the main JoinQuant strategy
- avoid further threshold tuning on this branch to reduce overfitting risk
