# Fundamental Momentum Combination Framework V1

Objective:
- freeze one unified comparison framework for combining bank fundamentals and momentum
- make sure different combination routes are judged under the same evaluation language
- prevent structural conclusions from being mixed together

## Three Distinct Combination Routes

### 1. Portfolio-Layer Combination

Definition:
- run a fundamental strategy and a momentum strategy as two separate sub-portfolios
- combine them only at the capital-allocation layer

Form:
- `R_mix = alpha * R_F + (1 - alpha) * R_M`

Interpretation:
- this is mainly an allocation problem
- it asks whether two valid standalone strategies diversify each other

Expected strength:
- most likely route to improve stability

Expected limitation:
- it does not create a new integrated stock-selection logic
- it is closer to `running two strategies together`

### 2. Score-Layer Combination

Definition:
- combine fundamental score and momentum score into one stock-level ranking score

Form:
- `S_i = alpha * F_i + (1 - alpha) * M_i`

Interpretation:
- this is mainly a factor-engineering problem

Expected strength:
- can produce a single unified stock-selection rule

Expected limitation:
- highly sensitive to normalization, scaling, and weight choice
- one signal can cancel the other
- weaker interpretability and higher overfitting risk

Current process rule:
- this route stays lower priority unless simpler routes fail to explain the opportunity set

### 3. Sequential Filter Then Rank

Definition:
- fundamentals first define the admissible candidate set
- momentum then ranks only inside that candidate set

Form:
- `U_t -> F_t -> H_t`

Interpretation:
- this is mainly a structured stock-selection logic
- it asks whether `quality-constrained momentum` exists

Expected strength:
- strongest economic interpretation

Expected limitation:
- first-layer filtering may remove stocks that pure momentum would have captured well
- therefore it should never be assumed to beat pure momentum automatically

## Unified Control Group Set

Every serious comparison should anchor against these four versions:

1. pure fundamental
2. pure momentum
3. sequential filter then rank
4. portfolio-layer combination

This is the minimum set needed to answer:

- does the joint structure beat pure fundamental
- does the joint structure beat pure momentum
- is the benefit coming from diversification or from a new stock-selection logic

## Evaluation Dimensions

All routes should be judged on the same core metrics:

- annualized return
- max drawdown
- Sharpe ratio
- turnover
- rolling out-of-sample stability

Optional secondary metrics:

- volatility
- beta
- excess return
- information ratio

## Interpretation Discipline

If portfolio-layer combination wins:
- conclude that `allocation-level diversification` is valuable
- do not automatically claim that integrated stock-selection logic is better

If sequential filter then rank wins:
- conclude that `fundamental admission + momentum selection` adds structural value
- do not automatically claim that diversification is the main source

If score-layer combination wins:
- conclude only after strong robustness checks
- because this route is the most exposed to normalization-driven false positives

## Current Practical Priority

The routes should currently be prioritized in this order:

1. portfolio-layer combination
2. sequential filter then rank
3. score-layer combination

Reason:
- portfolio-layer combination is the cleanest path to testing diversification
- sequential filtering is the cleanest path to testing structured economic logic
- score-layer mixing has the highest fragility and should not lead the process

## Current Research Status

Portfolio-layer route:
- active and currently strongest practical combined branch
- fixed `60/40` remains the best executable baseline
- annual entry plus monthly exit is the active upgrade candidate

Sequential route:
- economically coherent
- but current quarterly fundamental gate plus monthly momentum version does not beat pure momentum in rolling validation
- archived as a valid backup structure, not the active main line

Score-layer route:
- not current priority

## Process Rule Going Forward

No future claim that `fundamentals + momentum work better together` should be accepted unless it is clear:

- which of the three routes is being discussed
- which control groups were used
- and whether the advantage came from diversification, filtering, or score integration

## References

- [annual_entry_monthly_exit_formal_candidate_v1.md](D:\hh\codex\v4\phase_2_momentum\annual_entry_monthly_exit_formal_candidate_v1.md)
- [quarterly_fundamental_monthly_momentum_validation_note_v1.md](D:\hh\codex\v4\phase_2_momentum\quarterly_fundamental_monthly_momentum_validation_note_v1.md)
- [fundamental_momentum_layered_research_rule_v1.md](D:\hh\codex\v4\phase_2_momentum\fundamental_momentum_layered_research_rule_v1.md)
