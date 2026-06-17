# Phase 1: Fundamental

Goal:

- Collect and clean core bank fundamental data
- Run standalone statistical tests on fundamental factors first
- Do not mix momentum or mean-reversion features into this phase

Workflow:

1. Define required fields and source mapping
2. Download raw data
3. Align disclosure dates and reporting periods
4. Clean and standardize field formats
5. Build valid data segments for stock-quarter observations
6. Build factor candidates
7. Run rolling statistical tests

Current validity outputs:

- [valid_data_segment_definition.md](/D:/hh/codex/v4/phase_1_fundamental/valid_data_segment_definition.md)
- [quarterly_valid_data_segments.csv](/D:/hh/codex/v4/phase_1_fundamental/quarterly_valid_data_segments.csv)
