# Mean Reversion Anchored Validation V1

Protocol:
- train period: `2015-01` to `2018-12`
- validation period: `2019-01` to `2019-12`
- review period: `2020-01` to `2020-12`
- compare `rev5_abnvol` against raw `rev_5d` using train-period normalization only

Validation 2019:
- `rev5_abnvol` total return=`0.312876`
- raw `rev_5d` total return=`0.312643`

Review 2020:
- `rev5_abnvol` total return=`-0.046131`
- raw `rev_5d` total return=`-0.066198`

Interpretation:
- if `rev5_abnvol` beats raw `rev_5d` in both validation and review, then abnormal-volume filtering is a robust enhancement
- if it only wins in validation but not review, then the enhancement is still promising but not yet robust enough

Output:
- [mean_reversion_anchored_validation_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_anchored_validation_v1.csv)
