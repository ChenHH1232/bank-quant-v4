# JoinQuant V4 Primary vs Benchmark Yearly Comparison V1

## Full-Window Summary

- `primary` return: `44.48%`
- `benchmark` return: `43.06%`
- `primary` annualized return: `7.89%`
- `benchmark` annualized return: `7.67%`
- `primary` excess return: `20.54%`
- `benchmark` excess return: `19.35%`
- Return gap: `+1.42%` in favor of `primary`
- `primary` max drawdown: `22.43%`
- `benchmark` max drawdown: `22.23%`
- Drawdown gap: `+0.20%` against `primary`

## Interpretation

- `primary` does beat `benchmark`, but by a small margin.
- The gain looks like an incremental uplift from the improvement layer, not a regime-changing improvement.
- `benchmark` is slightly steadier on drawdown, while `primary` earns a bit more over the full window.
- Both lines share the same hardest period: `2022/04/15` to `2022/10/31`.

## Annual Highlights

### 2021

- The two lines are almost the same.
- The practical difference is one edge slot:
  - `primary` keeps `601838.XSHG`
  - `benchmark` keeps `601577.XSHG`
- This year supports the view that the common permanent factor layer already explains most of the signal.

### 2022

- `benchmark` absorbs `601825.XSHG` earlier and more stably.
- `primary` still looks slightly more conservative in the edge slots during the transition from `annual_01` to `annual_02`.
- The difference remains marginal rather than structural.

### 2023

- Once both lines switch into `annual_03`, they effectively converge.
- This is the strongest evidence that the large-bank tilt was driven by the common annual core, not by the improvement layer.

### 2024

- This is the cleanest year for observing edge behavior.
- `primary` expands into `600016.XSHG`, which looks like an improvement-layer style choice.
- `benchmark` instead keeps `601825.XSHG`, which is more consistent with the stable core-only approach.

### 2025

- `benchmark` becomes extremely stable in holdings.
- `primary` still has a little more edge rotation.
- The result is consistent with the full-window metrics: slightly more stability for `benchmark`, slightly more payoff for `primary`.

## Practical Takeaway

- The permanent fundamental backbone is the main engine.
- The improvement layer helps, but the current contribution is modest.
- Future optimization should focus less on adding more factors and more on:
  - whether the improvement layer can lift returns without widening drawdown
  - whether May annual refresh timing should be adjusted
  - whether the edge-slot differences are persistent sources of alpha or just mild noise
