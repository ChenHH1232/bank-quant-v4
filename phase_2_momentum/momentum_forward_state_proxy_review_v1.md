# Momentum Forward State Proxy Review V1

Scope:
- sample window: `2014-01-01` to `2020-12-31`
- objective: use only contemporaneously observable monthly cross-sectional features to proxy whether the next period is favorable to `mom_6_1`

Proxy ranking:
- `cross_mcap_median` | corr_forward=`0.094650` | corr_mom6_ic=`0.259623` | corr_mom12_ic=`0.023506` | top3_forward=`0.009597` | bot3_forward=`0.009952` | top3_mom6_ic=`0.153472` | bot3_mom6_ic=`0.029509`
- `cross_mom6_positive_ratio` | corr_forward=`-0.022845` | corr_mom6_ic=`0.220389` | corr_mom12_ic=`0.147074` | top3_forward=`0.008800` | bot3_forward=`0.008257` | top3_mom6_ic=`0.097320` | bot3_mom6_ic=`-0.087174`
- `cross_target_dispersion` | corr_forward=`0.034876` | corr_mom6_ic=`0.130923` | corr_mom12_ic=`0.148097` | top3_forward=`0.006112` | bot3_forward=`-0.000892` | top3_mom6_ic=`0.040202` | bot3_mom6_ic=`-0.040988`
- `cross_mom6_mean` | corr_forward=`0.015610` | corr_mom6_ic=`0.056456` | corr_mom12_ic=`0.094562` | top3_forward=`0.013006` | bot3_forward=`0.009269` | top3_mom6_ic=`0.185093` | bot3_mom6_ic=`-0.088166`
- `cross_mom6_top_bottom_spread` | corr_forward=`-0.017374` | corr_mom6_ic=`0.049461` | corr_mom12_ic=`0.040247` | top3_forward=`0.013566` | bot3_forward=`0.002170` | top3_mom6_ic=`0.124698` | bot3_mom6_ic=`-0.035230`
- `cross_mom6_median` | corr_forward=`0.027147` | corr_mom6_ic=`0.027751` | corr_mom12_ic=`0.080482` | top3_forward=`0.012895` | bot3_forward=`0.005803` | top3_mom6_ic=`0.144400` | bot3_mom6_ic=`-0.112649`
- `cross_mom12_median` | corr_forward=`-0.113751` | corr_mom6_ic=`-0.100667` | corr_mom12_ic=`0.022120` | top3_forward=`-0.001510` | bot3_forward=`0.015179` | top3_mom6_ic=`-0.001542` | bot3_mom6_ic=`-0.071138`
- `cross_money_mean` | corr_forward=`-0.244534` | corr_mom6_ic=`-0.134122` | corr_mom12_ic=`-0.057869` | top3_forward=`-0.019075` | bot3_forward=`0.016783` | top3_mom6_ic=`-0.074398` | bot3_mom6_ic=`-0.006702`
- `cross_money_median` | corr_forward=`-0.264283` | corr_mom6_ic=`-0.140712` | corr_mom12_ic=`-0.068104` | top3_forward=`-0.015184` | bot3_forward=`0.020873` | top3_mom6_ic=`-0.023914` | bot3_mom6_ic=`0.027121`

Interpretation:
- a useful forward proxy should ideally be positively related both to next-period pool return and to next-period `mom_6_1` IC
- if the same proxy also boosts `mom_12_1`, it may be a broad state signal rather than a specifically medium-term momentum state signal

Output:
- [momentum_forward_state_proxy_review_v1.csv](D:\hh\codex\v4\phase_2_momentum\momentum_forward_state_proxy_review_v1.csv)
