# Mean Reversion Overlay On Annual Pool V1

Purpose:
- test whether the frozen weekly mean-reversion layer can improve execution inside the real annual approved pool
- use the actual `primary` annual holding schedule exported from JoinQuant attribution logs
- treat this as post-2021 acceptance observation, not parameter-tuning evidence

Setup:
- upper approved pool source: `phase_1_fundamental/joinquant_v4_annual_attribution_v1.csv`
- upper pool line: `primary`
- tactical signal: `rev5_abnvol`
- tactical frequency: weekly
- tactical top N inside approved pool: `5`
- baseline: equal-weight hold the full approved pool until the next weekly checkpoint

Window:
- acceptance observation: `2021-05-31` to `2026-04-30`

Results:
- `annual_pool_baseline` | total_return=`0.584687` | annualized_proxy=`0.098381` | max_drawdown_proxy=`-0.217589` | 2021_2022=`-0.056581` | 2023_2024=`0.386706` | 2025_2026=`0.211309` | traded_periods=`250`
- `annual_pool_overlay_rev5_abnvol` | total_return=`0.568945` | annualized_proxy=`0.096148` | max_drawdown_proxy=`-0.234235` | 2021_2022=`-0.069005` | 2023_2024=`0.327931` | 2025_2026=`0.269067` | traded_periods=`250`

Current read:
- on the frozen acceptance window, `annual_pool_baseline` is the stronger execution path inside the annual approved pool
- because this uses the post-2021 window, it should guide deployment interpretation only and should not be used to retune the signal coefficients

Outputs:
- [mean_reversion_overlay_on_annual_pool_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_overlay_on_annual_pool_v1.csv)
- [mean_reversion_overlay_on_annual_pool_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_overlay_on_annual_pool_v1_detail.csv)
