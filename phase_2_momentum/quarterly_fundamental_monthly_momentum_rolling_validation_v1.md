# Quarterly Fundamental Monthly Momentum Rolling Validation V1

Protocol:
- research scope = pre-2021 only
- quarterly layer updates the fundamental candidate pool `F_t` using `combo__equal_weight`
- monthly layer ranks only inside `F_t` using deployment-safe `mom_12_1`
- final holdings are equal-weight within the selected monthly set

- fold count: `2`
- strategy snapshots: `130`

Strategy summary:
- `direct_mom12_top6` | snapshots=`26` | mean_return=`0.000512` | cum_return=`0.013251` | mean_candidate_count=`14.69` | mean_holding_count=`6.00`
- `quarterly_top20_mom12_top6` | snapshots=`26` | mean_return=`0.000393` | cum_return=`0.010141` | mean_candidate_count=`13.27` | mean_holding_count=`6.00`
- `quarterly_top16_mom12_top6` | snapshots=`26` | mean_return=`0.000392` | cum_return=`0.010109` | mean_candidate_count=`11.15` | mean_holding_count=`6.00`
- `quarterly_fundamental_top16_equal` | snapshots=`26` | mean_return=`0.000338` | cum_return=`0.008723` | mean_candidate_count=`11.15` | mean_holding_count=`11.15`
- `quarterly_fundamental_top20_equal` | snapshots=`26` | mean_return=`0.000319` | cum_return=`0.008229` | mean_candidate_count=`13.27` | mean_holding_count=`13.27`

Interpretation targets:
- compare `quarterly_top16_mom12_top6` and `quarterly_top20_mom12_top6` against `direct_mom12_top6` to judge whether quarterly fundamental admission adds value
- compare the gated strategies against `quarterly_fundamental_top16_equal` and `quarterly_fundamental_top20_equal` to judge whether monthly momentum adds value after quarterly fundamental admission

Output:
- [quarterly_fundamental_monthly_momentum_rolling_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\quarterly_fundamental_monthly_momentum_rolling_validation_v1_detail.csv)
