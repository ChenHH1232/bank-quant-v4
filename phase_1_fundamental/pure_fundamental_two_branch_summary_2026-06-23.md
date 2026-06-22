# Pure Fundamental Two Branch Summary 2026-06-23

Scope:
- freeze the current interpretation of the pure-fundamental line after the `base_core_6` follow-up research
- consolidate the recent branch tests around `eps`, `core_level_capital_adequacy_ratio`, and quality-layer overweight
- preserve the current view of what remains executable, what stays secondary, and what may later support manual annual switching

Current main executable branch:
- shell = `base_core_6 = base_core_7 - derived__log_total_assets`
- execution = `5y / 2y / 1y + combo__ic_weight_train + top_08`
- status = current preferred pure-fundamental baseline

Branch A: balanced pure-fundamental baseline
- shorthand = `base_core_6 + top_08`
- interpretation:
- this remains the best confirmed all-around pure-fundamental line so far
- it preserves the original multi-factor balance between profitability and bank-quality constraints
- repeated JoinQuant confirmation still says this line is hard to beat cleanly

Branch B: capital-quality side candidate
- shorthand = `base_core_6 - indicator__eps + bank_indicator__core_level_capital_adequacy_ratio`
- rolling replacement result:
- strongest swap was remove `indicator__eps`, add `bank_indicator__core_level_capital_adequacy_ratio`
- replacement rolling means:
  - baseline test/review = `0.269435 / 0.065544`
  - candidate test/review = `0.283983 / 0.078288`
- JoinQuant confirmation result:
  - strategy return = `47.98%`
  - annualized return = `8.43%`
  - excess return = `23.46%`
  - beta = `1.027`
  - sharpe = `0.237`
  - information ratio = `0.647`
- interpretation:
- this branch did not beat the main line on absolute return
- but it did show a slightly steadier excess path and slightly better risk-adjusted behavior
- therefore it is not strong enough to replace Branch A, but strong enough to remain an accepted side candidate

Yearly comparison between the two pure-fundamental branches:
- `2021`: Branch B clearly lagged Branch A
- `2022`: Branch B clearly outperformed Branch A
- `2023`: Branch B slightly outperformed Branch A
- `2024`: Branch B clearly outperformed Branch A
- `2025`: Branch B lagged again
- implication:
- the `core_level` branch is not a universal upgrade
- it looks regime-dependent rather than globally dominant

Quality-layer overweight research:
- local research suggested that the bank-quality block often dominated the profitability block
- regime-style rolling also showed that quality was usually stronger than profitability on fold-local diagnostics
- however the direct JoinQuant executable version with persistent `30 / 70` profitability-quality tilt failed badly:
  - strategy return = `17.39%`
  - excess return = `-2.06%`
  - sharpe = `-0.034`
  - information ratio = `-0.061`
  - max drawdown = `26.35%`
- conclusion:
- the insight "quality matters more" is valid as research guidance
- but directly forcing a heavy permanent quality overweight destroyed the executable balance of the live strategy

Current branch status:
- primary confirmed branch:
  - `base_core_6 + top_08`
- accepted side candidate:
  - `base_core_6 - indicator__eps + bank_indicator__core_level_capital_adequacy_ratio`
- rejected execution branch:
  - persistent quality overweight `30 / 70`

Forward-looking interpretation:
- the evidence now supports the idea that pure-fundamental performance may depend on whether the next annual regime favors:
  - profitability expression
  - or capital-quality expression
- but the current automatic switching rules were too crude and did not beat the cleaner static alternatives strongly enough

Manual switching note for future use:
- a future human-in-the-loop process could plausibly choose between the two pure-fundamental branches each year:
  - Branch A when the next year is expected to favor profitability and balanced stock selection
  - Branch B when the next year is expected to favor stronger capital quality, large-bank resilience, or stricter balance-sheet preference
- this should be treated as a new explicit forecasting workflow, not as an already-confirmed automatic strategy upgrade

Decision:
- keep Branch A as the default pure-fundamental executable main line
- archive Branch B as the formal side candidate worth monitoring
- archive persistent quality overweight as a research-positive but JoinQuant-rejected branch
- preserve the manual annual branch-switch idea as a future discretionary framework, not as a current automated rule
