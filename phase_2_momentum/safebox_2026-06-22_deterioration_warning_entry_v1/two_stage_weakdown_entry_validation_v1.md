# Two-Stage Weak-Down Entry Validation V1

Objective:
- test a minimal two-stage weak-down entry rule
- stage 1 = deterioration proxy raises a warning
- stage 2 = price-state proxy confirms the weak-down entry
- compare this rule against pure price and pure deterioration entry signals

Rule:
- if deterioration proxy enters `weak_down`, a warning becomes active
- if price proxy later enters `weak_down` while warning is active, confirm `weak_down`
- warning resets after a confirmation event

Signal summary:
- `price_only` | count=`2` / `8` | next_mom_on=`-0.002128` vs off=`0.000058` | next_mom_negative_rate_on=`1.000000` vs off=`0.500000`
- `deterioration_only` | count=`5` / `8` | next_mom_on=`0.000757` vs off=`-0.002564` | next_mom_negative_rate_on=`0.400000` vs off=`1.000000`
- `two_stage_confirmed` | count=`2` / `8` | next_mom_on=`-0.002128` vs off=`0.000058` | next_mom_negative_rate_on=`1.000000` vs off=`0.500000`

Interpretation:
- if `two_stage_confirmed` keeps the downside precision of `price_only` while reducing false early triggers from `deterioration_only`, the two-stage rule is a better weak-down entry candidate
- if `two_stage_confirmed` becomes too sparse or loses downside precision, pure price confirmation remains better for actual weak-down entry

Output:
- [two_stage_weakdown_entry_validation_v1_detail.csv](D:\hh\codex\v4\phase_2_momentum\two_stage_weakdown_entry_validation_v1_detail.csv)
