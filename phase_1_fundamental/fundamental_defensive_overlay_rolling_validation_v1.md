# Fundamental Defensive Overlay Rolling Validation V1

Protocol:
- base execution line = annual pure-fundamental `base_core_7 + combo__ic_weight_train`
- factor selection remains the existing annual `5Y train + 2Y test + 1Y review` process
- overlay is searched only after the base pure-fundamental factor set is frozen inside each fold
- regime signal = cross-sectional deterioration breadth averaged across a chosen metric combination
- deterioration metrics searched:
- `npl`, `capital`, `coverage`, `roe`, `profit_growth`
- warning threshold grid = `40% / 45%`
- severe threshold grid = `55% / 60%`
- warning equity weight grid = `60% / 80%`
- severe equity weight grid = `20% / 40%`
- defensive asset candidates wired into the framework = `cash`, `treasury_etf_511010`, `short_bond_etf_511260`

Data reality check:
- `cash` full-review-cover candidate rows: `405`
- `treasury_etf_511010` full-review-cover candidate rows: `400`
- `short_bond_etf_511260` full-review-cover candidate rows: `400`

Chosen fold results:
- `annual_01` | status=`chosen_best_available` | config=`all_5__wthr_45__sthr_55__weq_80__seq_20__asset_cash` | asset=`cash` | metric_combo=`all_5` | train_cum=`0.008389` | test_cum=`0.006964` | review_cum=`-0.000524` | review_mean=`-0.000131`
- `annual_02` | status=`chosen_best_available` | config=`bank_core_3__wthr_40__sthr_55__weq_60__seq_40__asset_cash` | asset=`cash` | metric_combo=`bank_core_3` | train_cum=`0.004932` | test_cum=`0.003923` | review_cum=`-0.001472` | review_mean=`-0.000367`
- `annual_03` | status=`chosen_best_available` | config=`earnings_2__wthr_40__sthr_55__weq_60__seq_40__asset_cash` | asset=`cash` | metric_combo=`earnings_2` | train_cum=`0.005589` | test_cum=`0.000667` | review_cum=`0.000841` | review_mean=`0.000280`
- `annual_04` | status=`chosen_best_available` | config=`earnings_2__wthr_40__sthr_55__weq_60__seq_40__asset_cash` | asset=`cash` | metric_combo=`earnings_2` | train_cum=`0.004262` | test_cum=`0.002226` | review_cum=`0.004822` | review_mean=`0.001605`
- `annual_05` | status=`chosen_best_available` | config=`earnings_2__wthr_40__sthr_55__weq_60__seq_40__asset_cash` | asset=`cash` | metric_combo=`earnings_2` | train_cum=`0.003022` | test_cum=`0.005931` | review_cum=`0.001458` | review_mean=`0.000729`

Chosen-vs-baseline review summary:
- mean review cumulative advantage = `0.000001`
- mean review mean-return advantage = `0.000000`
- overlay beats baseline on review cumulative in `1/5` folds

Interpretation boundary:
- this file validates the annual rolling search frame for trigger rule and equity-weight mapping
- the full annual review comparison is now available across `cash`, `treasury_etf_511010`, and `short_bond_etf_511260`
- average review cumulative return across full-cover overlay candidates ranks as `short_bond_etf_511260` (0.001656) > `treasury_etf_511010` (0.001421) > `cash` (0.001014)
- fold selection is still driven only by train/test information, so any review-period asset ranking here is diagnostic rather than an input to the chosen config

Outputs:
- [fundamental_defensive_overlay_rolling_validation_v1_config_results.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_rolling_validation_v1_config_results.csv)
- [fundamental_defensive_overlay_rolling_validation_v1_chosen.csv](D:\hh\codex\v4\phase_1_fundamental\fundamental_defensive_overlay_rolling_validation_v1_chosen.csv)