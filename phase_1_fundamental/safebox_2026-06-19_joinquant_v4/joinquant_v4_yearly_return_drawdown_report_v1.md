# JoinQuant V4 Yearly Return Drawdown Split V1

## Scope

- Input file: `joinquant_v4_daily_nav_input_from_results_v1.csv`
- Window source: `joinquant_v4_annual_attribution_v1.csv`
- Annual windows are defined from each May rebalance date to the day before the next May rebalance date.

## Strategy Windows

- 2021: 2021-05-31 to 2022-05-04
- 2022: 2022-05-05 to 2023-05-03
- 2023: 2023-05-04 to 2024-05-05
- 2024: 2024-05-06 to 2025-05-05
- 2025: 2025-05-06 to 2026-05-29

## Output Files

- `joinquant_v4_yearly_return_drawdown_split_v1.csv`
- `joinquant_v4_yearly_return_drawdown_comparison_v1.csv`

## Per-Line Metrics

### benchmark

- 2021: return=-3.56% max_drawdown=-18.53% window=2021-05-31 to 2022-05-04
- 2022: return=-10.28% max_drawdown=-20.45% window=2022-05-05 to 2023-05-03
- 2023: return=11.51% max_drawdown=-11.85% window=2023-05-04 to 2024-05-05
- 2024: return=32.19% max_drawdown=-11.66% window=2024-05-06 to 2025-05-05
- 2025: return=7.43% max_drawdown=-11.47% window=2025-05-06 to 2026-05-29

### primary

- 2021: return=-1.45% max_drawdown=-16.50% window=2021-05-31 to 2022-05-04
- 2022: return=-10.19% max_drawdown=-20.70% window=2022-05-05 to 2023-05-03
- 2023: return=10.59% max_drawdown=-13.29% window=2023-05-04 to 2024-05-05
- 2024: return=30.58% max_drawdown=-12.25% window=2024-05-06 to 2025-05-05
- 2025: return=9.21% max_drawdown=-11.45% window=2025-05-06 to 2026-05-29

## Primary vs Benchmark

- 2021: return_gap=2.11% drawdown_gap=2.03%
- 2022: return_gap=0.09% drawdown_gap=-0.25%
- 2023: return_gap=-0.91% drawdown_gap=-1.45%
- 2024: return_gap=-1.61% drawdown_gap=-0.59%
- 2025: return_gap=1.78% drawdown_gap=0.02%
