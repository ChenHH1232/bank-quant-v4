# Momentum Pre-2021 Mechanism Review V1

Scope:
- sample window: `2014-01-01` to `2020-12-31`
- stock pool: monthly bank pool with `rebalance_stock_pool_flag_v2 == 1`
- target: next monthly rebalance `close-to-close` total return
- purpose: explain pre-2021 why `mom_6_1` looked strong in research while `mom_12_1` may have been more deployment-stable

Overall factor ranking on full pre-2021 annual review averages:
- `mom_6_1` | ic=`0.035067` | pos=`0.541667` | spread=`0.007774` | rho_mcap=`0.016735` | rho_liq=`0.220712` | rho_pb=`0.367823`
- `mom_12_1` | ic=`0.010507` | pos=`0.486111` | spread=`0.007063` | rho_mcap=`0.052268` | rho_liq=`0.297414` | rho_pb=`0.481829`
- `mom_3_1` | ic=`-0.004795` | pos=`0.458333` | spread=`-0.000238` | rho_mcap=`-0.013561` | rho_liq=`0.109800` | rho_pb=`0.221149`

Period summary:
- `train_2015_2019` | `mom_3_1` | ic=`-0.014750` | pos=`0.466667` | spread=`-0.003292` | rho_mcap=`0.003926` | rho_liq=`0.102473` | rho_pb=`0.206289`
- `validation_2020` | `mom_3_1` | ic=`0.044984` | pos=`0.416667` | spread=`0.015030` | rho_mcap=`-0.100995` | rho_liq=`0.146440` | rho_pb=`0.295448`
- `full_pre2021` | `mom_3_1` | ic=`-0.004795` | pos=`0.458333` | spread=`-0.000238` | rho_mcap=`-0.013561` | rho_liq=`0.109800` | rho_pb=`0.221149`
- `train_2015_2019` | `mom_6_1` | ic=`0.057386` | pos=`0.566667` | spread=`0.007568` | rho_mcap=`0.051662` | rho_liq=`0.221647` | rho_pb=`0.350164`
- `validation_2020` | `mom_6_1` | ic=`-0.076528` | pos=`0.416667` | spread=`0.008806` | rho_mcap=`-0.157901` | rho_liq=`0.216037` | rho_pb=`0.456115`
- `full_pre2021` | `mom_6_1` | ic=`0.035067` | pos=`0.541667` | spread=`0.007774` | rho_mcap=`0.016735` | rho_liq=`0.220712` | rho_pb=`0.367823`
- `train_2015_2019` | `mom_12_1` | ic=`0.017608` | pos=`0.466667` | spread=`0.005220` | rho_mcap=`0.093048` | rho_liq=`0.284295` | rho_pb=`0.443154`
- `validation_2020` | `mom_12_1` | ic=`-0.024998` | pos=`0.583333` | spread=`0.016277` | rho_mcap=`-0.151632` | rho_liq=`0.363007` | rho_pb=`0.675206`
- `full_pre2021` | `mom_12_1` | ic=`0.010507` | pos=`0.486111` | spread=`0.007063` | rho_mcap=`0.052268` | rho_liq=`0.297414` | rho_pb=`0.481829`

Per-year best factor by rank IC:
- `2015`: best=`mom_12_1` | ic=`-0.068849` | spread=`-0.012500`
- `2016`: best=`mom_6_1` | ic=`0.000733` | spread=`0.007294`
- `2017`: best=`mom_6_1` | ic=`0.339874` | spread=`0.028722`
- `2018`: best=`mom_12_1` | ic=`-0.082357` | spread=`-0.002864`
- `2019`: best=`mom_6_1` | ic=`0.206435` | spread=`0.026751`
- `2020`: best=`mom_3_1` | ic=`0.044984` | spread=`0.015030`

Interpretation hints:
- if `mom_6_1` has better average pre-2021 IC but also stronger positive correlation with size or liquidity, it may be partly capturing style exposure rather than pure trend continuation
- if `mom_12_1` is weaker in average IC but more stable across years or less style-loaded, it may behave like a slow bank-style filter
- use this file as pre-2021 evidence only; do not mix it with repeated post-2021 out-of-sample tuning

Outputs:
- [momentum_pre2021_mechanism_review_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_pre2021_mechanism_review_v1.csv)
