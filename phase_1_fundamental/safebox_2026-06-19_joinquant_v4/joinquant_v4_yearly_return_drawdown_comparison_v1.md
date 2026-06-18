# JoinQuant V4 Yearly Return Drawdown Comparison V1

## Window Rule

- Annual windows are split by the actual May strategy refresh rhythm:
  - 2021: 2021-05-31 to 2022-05-04
  - 2022: 2022-05-05 to 2023-05-03
  - 2023: 2023-05-04 to 2024-05-05
  - 2024: 2024-05-06 to 2025-05-05
  - 2025: 2025-05-06 to 2026-05-29

## Yearly Comparison

| Year | Primary return | Benchmark return | Return gap | Primary max DD | Benchmark max DD | Drawdown gap | Quick read |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | -1.45% | -3.56% | +2.11% | -16.50% | -18.53% | +2.03% | `primary` 明显更好，且回撤更浅 |
| 2022 | -10.19% | -10.28% | +0.09% | -20.70% | -20.45% | -0.25% | 两条线几乎一样，`primary` 略多一点回撤 |
| 2023 | +10.59% | +11.51% | -0.91% | -13.29% | -11.85% | -1.45% | `benchmark` 更强，且更稳 |
| 2024 | +30.58% | +32.19% | -1.61% | -12.25% | -11.66% | -0.59% | `benchmark` 再胜一年 |
| 2025 | +9.21% | +7.43% | +1.78% | -11.45% | -11.47% | +0.02% | `primary` 收益更高，回撤几乎一样 |

## Main Takeaways

- `primary` 领先的年份:
  - 2021
  - 2022
  - 2025
- `benchmark` 领先的年份:
  - 2023
  - 2024

- 最值得注意的不是“谁总收益更高”，而是结构：
  - `primary` 的优势集中在两端，尤其是 2021 和 2025
  - `benchmark` 的优势集中在中段，也就是 2023 和 2024

- 这和前面看到的组合风格是对得上的：
  - 2023 到 2024 属于大行风格很强的阶段，`benchmark` 的纯核心层反而更占优
  - 2025 以后改善层重新开始带来一点增厚，`primary` 又追回来

## Interpretation

- 改善层不是全年候稳定增益。
- 它更像一个阶段性增强器：
  - 有些年份能明显帮忙
  - 有些年份反而不如只保留常驻核心层

- 目前最合理的研究方向不是简单继续往 `primary` 里加因子，而是问：
  - 哪些市场阶段适合打开改善层
  - 哪些阶段应更接近 `benchmark`

## Suggested Next Step

- 进入“条件启用改善层”的研究，而不是默认全年固定启用。
- 最简单可做的下一版，就是先按年度结果试一个规则：
  - 当年度训练期里改善层相对核心层有明显正增益时，用 `primary`
  - 否则退回 `benchmark`
