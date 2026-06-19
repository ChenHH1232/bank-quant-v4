# Mean Reversion Field Coverage Check V1

Scope:
- source panel: `momentum_factor_panel_v2.csv`
- data window target: keep the same research window as momentum, with formal pre-2021 research and later out-of-sample acceptance
- purpose: determine whether the existing daily panel is already sufficient for first-pass mean-reversion research

Coverage summary:
- present fields: `16`
- derivable fields: `13`
- missing required fields: `0`

Verdict:
- first-pass mean-reversion research can start without a new download
- the current panel is already sufficient, because the required missing items are derivable from the existing daily price, return, liquidity, and size fields

Still-missing but non-blocking fields:
- `paused`, `is_st`, `high_limit`, `low_limit` are not in the current panel
- these are execution-layer enhancements and should not block the first research pass

Recommended next action:
- build a mean-reversion factor panel directly from the current daily panel, without re-downloading data first

Output:
- [mean_reversion_field_coverage_check_v1.csv](D:\hh\codex\v4\phase_2_momentum\mean_reversion_field_coverage_check_v1.csv)
