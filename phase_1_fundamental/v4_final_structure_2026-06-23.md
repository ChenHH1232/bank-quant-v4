# V4 Final Structure 2026-06-23

Date: `2026-06-23`

## Guiding Statement

V4 no longer pursues the theoretical completeness of "fundamental + momentum + mean reversion".
Instead, it accepts the current project evidence:

> under the current A-share bank sample and execution framework, the effective core of the strategy is fundamental selection, and risk control should be handled independently rather than relying mainly on momentum to dilute equity exposure

The latest JoinQuant evidence further shows:

> shortbond overlay is not only a defensive side tool; in the current project scope it can improve the leading pure-fundamental branches enough to enter the formal candidate stack

## Final Structure

### Formal First Main Line

`Core-Level Shadow + Shortbond Overlay`

- current first-ranked execution version
- best overall combination of return, excess return, Sharpe, IR, and drawdown behavior
- strongest current full-cycle candidate

### Formal Second Main Line

`Balanced + Shortbond Overlay`

- second-ranked execution version
- stronger than pure `balanced`
- useful as the simpler overlay-backed production branch

### Plain Benchmark Branches

`Pure Fundamental Core-Level Shadow`

- no-overlay relative-path benchmark
- still valuable as a plain structural reference

`Pure Fundamental Balanced`

- no-overlay simplicity benchmark
- still valuable as the cleanest plain baseline

## Formally Rejected Branches

- fixed `mom_12_1` independent `40%` allocation
- monthly momentum style switching
- momentum-driven quality/profitability tilts
- general mean-reversion branch

## Interpretation

The V4 framework now has a clearer separation of roles:

- fundamental selection is responsible for the stock-selection core
- shortbond overlay is responsible for absolute-risk control and can improve the execution path of the strongest branches
- momentum and mean reversion are not part of the formal default stack under the current project sample and execution framework

## Practical Reading

The current V4 hierarchy is no longer:

- pure fundamental first
- overlay optional

It is now:

- overlay-enhanced pure-fundamental branches first
- plain pure-fundamental branches second
- momentum and mean-reversion branches archived from the formal default stack
