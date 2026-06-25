# Deterioration Weak-Down Entry Validation V1

Objective:
- test whether deterioration-based fundamental weakening is usable as a `weak_down` entry signal
- compare it directly against the current price-state proxy
- focus on entry recognition, not full strategy replacement

Protocol:
- research scope = pre-2021 rolling validation only
- state buckets are reused from the existing rolling proxy framework
- evaluation target = next-month direct momentum environment proxy `direct_mom12_top6` return
- secondary check = next-period return of each proxy's own routed portfolio

Proxy summary:
- `combined_state_proxy` | weak_down_count=`4` / `6` | next_mom_after_weak=`-0.000235` vs nonweak=`-0.002529` | next_mom_negative_rate_after_weak=`0.500000` vs nonweak=`1.000000` | next_proxy_after_weak=`0.000785` vs nonweak=`-0.000686`
- `deterioration_state_proxy` | weak_down_count=`3` / `6` | next_mom_after_weak=`0.000564` vs nonweak=`-0.002564` | next_mom_negative_rate_after_weak=`0.333333` vs nonweak=`1.000000` | next_proxy_after_weak=`0.001172` vs nonweak=`-0.000488`
- `price_state_proxy` | weak_down_count=`2` / `6` | next_mom_after_weak=`-0.002128` vs nonweak=`-0.000436` | next_mom_negative_rate_after_weak=`1.000000` vs nonweak=`0.500000` | next_proxy_after_weak=`-0.000088` vs nonweak=`0.000342`

Price vs deterioration pair check:
- `deterioration_only_weak_down` count=`4` | next_mom_mean=`0.001352` | next_mom_negative_rate=`0.250000`
- `price_only_weak_down` count=`1` | next_mom_mean=`-0.002633` | next_mom_negative_rate=`1.000000`
- `both_weak_down` count=`1` | next_mom_mean=`-0.001623` | next_mom_negative_rate=`1.000000`

Interpretation:
- if deterioration weak-down months are followed by worse next-month momentum conditions than non-weak months, the deterioration signal is usable as a down-entry warning candidate
- if deterioration-only weak-down months are already weak on the next step, that supports the idea that fundamental worsening can warn before price-state confirmation
- if price-only weak-down months are weaker instead, price-state is still the faster entry sensor

Outputs:
- [deterioration_weakdown_entry_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\deterioration_weakdown_entry_validation_v1_detail.csv)
