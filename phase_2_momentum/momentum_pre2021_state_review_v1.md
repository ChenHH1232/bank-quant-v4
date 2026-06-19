# Momentum Pre-2021 State Review V1

Scope:
- sample window: `2014-01-01` to `2020-12-31`
- classification unit: annual state buckets built from monthly bank-pool average forward returns
- state rule: `trend_up` if annual average monthly forward return >= 1%, `weak_down` if < 0, otherwise `mixed_flat`

Year-state classification:
- `2015` | state=`weak_down` | avg_month_forward=`-0.003716` | positive_month_ratio=`0.416667`
- `2016` | state=`mixed_flat` | avg_month_forward=`0.002629` | positive_month_ratio=`0.583333`
- `2017` | state=`trend_up` | avg_month_forward=`0.019732` | positive_month_ratio=`0.666667`
- `2018` | state=`weak_down` | avg_month_forward=`-0.008561` | positive_month_ratio=`0.416667`
- `2019` | state=`trend_up` | avg_month_forward=`0.022955` | positive_month_ratio=`0.500000`
- `2020` | state=`weak_down` | avg_month_forward=`-0.001287` | positive_month_ratio=`0.666667`

Factor performance by state bucket:
- `trend_up` | `mom_6_1` | years=`2017|2019` | ic=`0.273155` | pos=`0.750000` | spread=`0.027736`
- `trend_up` | `mom_12_1` | years=`2017|2019` | ic=`0.236560` | pos=`0.750000` | spread=`0.024068`
- `trend_up` | `mom_3_1` | years=`2017|2019` | ic=`0.126427` | pos=`0.625000` | spread=`0.013051`
- `mixed_flat` | `mom_6_1` | years=`2016` | ic=`0.000733` | pos=`0.583333` | spread=`0.007294`
- `mixed_flat` | `mom_3_1` | years=`2016` | ic=`-0.134389` | pos=`0.416667` | spread=`-0.008764`
- `mixed_flat` | `mom_12_1` | years=`2016` | ic=`-0.233872` | pos=`0.166667` | spread=`-0.006673`
- `weak_down` | `mom_3_1` | years=`2015|2018|2020` | ic=`-0.049077` | pos=`0.361111` | spread=`-0.006256`
- `weak_down` | `mom_12_1` | years=`2015|2018|2020` | ic=`-0.058735` | pos=`0.416667` | spread=`0.000305`
- `weak_down` | `mom_6_1` | years=`2015|2018|2020` | ic=`-0.112213` | pos=`0.388889` | spread=`-0.005374`

Interpretation:
- if `mom_6_1` is clearly strongest only inside `trend_up` years, then its research edge is state-dependent rather than all-weather
- if `mom_12_1` is less explosive but relatively less damaged in `mixed_flat` or `weak_down` years, it supports the slow-style-filter interpretation
- this review is still pre-2021 only and can be used for mechanism explanation without contaminating the out-of-sample deployment window

Outputs:
- [momentum_pre2021_state_review_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_pre2021_state_review_v1.csv)
