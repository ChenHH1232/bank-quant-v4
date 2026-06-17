import csv
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "phase1_training_panel.csv"
SINGLE_FACTOR_RESULTS_PATH = SCRIPT_DIR / "single_factor_test_results_v1.csv"
OUTPUT_FACTORS_PATH = SCRIPT_DIR / "factor_collinearity_v1.csv"
OUTPUT_PAIRWISE_PATH = SCRIPT_DIR / "factor_pairwise_corr_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "factor_collinearity_v1.md"

TRAIN_START = pd.Timestamp("2014-05-01")
TRAIN_END = pd.Timestamp("2019-05-01")
STATUS_KEEP = {"A", "B"}
CORR_ALERT_THRESHOLD = 0.80


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[df["rebalance_stock_pool_flag"].astype(str) == "1"].copy()
    df = df[(df["rebalance_date"] >= TRAIN_START) & (df["rebalance_date"] < TRAIN_END)].copy()
    return df


def load_results(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def preprocess_feature(train_df: pd.DataFrame, factor_name: str) -> pd.Series:
    values = pd.to_numeric(train_df[factor_name], errors="coerce")
    non_null = values.dropna()
    if non_null.empty:
        return pd.Series(index=train_df.index, dtype="float64")
    lower = float(non_null.quantile(0.01))
    upper = float(non_null.quantile(0.99))
    clipped = values.clip(lower=lower, upper=upper)
    mean_value = float(clipped.dropna().mean())
    std_value = float(clipped.dropna().std(ddof=0))
    if std_value <= 0 or pd.isna(std_value):
        return pd.Series(index=train_df.index, dtype="float64")
    return (clipped - mean_value) / std_value


def compute_vif(feature_frame: pd.DataFrame, column_name: str) -> float:
    y = feature_frame[column_name].to_numpy(dtype=float)
    x = feature_frame.drop(columns=[column_name]).to_numpy(dtype=float)
    if x.shape[1] == 0:
        return 1.0
    x = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    fitted = x @ beta
    ss_res = float(np.sum((y - fitted) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    if ss_tot <= 0:
        return float("nan")
    r_squared = 1.0 - (ss_res / ss_tot)
    if r_squared >= 0.999999:
        return float("inf")
    return 1.0 / max(1e-12, 1.0 - r_squared)


def build_target_subset(panel_df: pd.DataFrame, factor_rows: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    factor_names = factor_rows["factor_name"].tolist()
    prepared = pd.DataFrame(index=panel_df.index)
    for factor_name in factor_names:
        prepared[factor_name] = preprocess_feature(panel_df, factor_name)
    prepared = prepared.dropna(axis=1, how="all")
    usable_factors = prepared.columns.tolist()
    prepared = prepared.dropna(subset=usable_factors, how="all")
    return prepared, usable_factors


def build_pairwise_rows(feature_frame: pd.DataFrame, target_label: str) -> list[dict[str, object]]:
    corr_matrix = feature_frame.corr(method="spearman")
    rows: list[dict[str, object]] = []
    columns = corr_matrix.columns.tolist()
    for i, left in enumerate(columns):
        for right in columns[i + 1 :]:
            corr_value = corr_matrix.loc[left, right]
            if pd.isna(corr_value):
                continue
            rows.append(
                {
                    "target_label": target_label,
                    "left_factor": left,
                    "right_factor": right,
                    "spearman_corr": round(float(corr_value), 6),
                    "abs_spearman_corr": round(abs(float(corr_value)), 6),
                    "high_corr_flag": int(abs(float(corr_value)) >= CORR_ALERT_THRESHOLD),
                }
            )
    return rows


def build_factor_rows(feature_frame: pd.DataFrame, factor_rows: pd.DataFrame, target_label: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if feature_frame.empty:
        return rows
    corr_matrix = feature_frame.corr(method="spearman")
    for _, factor_row in factor_rows.iterrows():
        factor_name = factor_row["factor_name"]
        if factor_name not in feature_frame.columns:
            continue
        series = feature_frame[factor_name]
        non_null_count = int(series.notna().sum())
        same_target_factors = [col for col in feature_frame.columns if col != factor_name]
        max_abs_corr = 0.0
        closest_factor = ""
        if same_target_factors:
            pair_series = corr_matrix.loc[factor_name, same_target_factors].abs().sort_values(ascending=False)
            if not pair_series.empty:
                closest_factor = str(pair_series.index[0])
                max_abs_corr = float(pair_series.iloc[0])
        vif_value = compute_vif(feature_frame.dropna(), factor_name) if len(feature_frame.dropna()) >= max(20, len(feature_frame.columns) + 5) else float("nan")
        rows.append(
            {
                "target_label": target_label,
                "factor_name": factor_name,
                "factor_family": factor_row["factor_family"],
                "single_factor_status": factor_row["final_status"],
                "validation_rank_ic_mean": factor_row["validation_rank_ic_mean"],
                "non_null_rows": non_null_count,
                "peer_factor_count": len(same_target_factors),
                "closest_factor": closest_factor,
                "max_abs_spearman_corr": round(max_abs_corr, 6),
                "high_corr_flag": int(max_abs_corr >= CORR_ALERT_THRESHOLD),
                "vif": round(float(vif_value), 6) if pd.notna(vif_value) and np.isfinite(vif_value) else ("inf" if np.isinf(vif_value) else ""),
                "vif_alert_flag": int(pd.notna(vif_value) and np.isfinite(vif_value) and float(vif_value) >= 10.0),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(factor_rows: list[dict[str, object]], pairwise_rows: list[dict[str, object]]) -> None:
    factor_df = pd.DataFrame(factor_rows)
    pair_df = pd.DataFrame(pairwise_rows)
    lines = [
        "# Factor Collinearity Check V1",
        "",
        "Scope:",
        "- training window only: `2014-05-01` to `2019-05-01`",
        "- sample only: `rebalance_stock_pool_flag = 1`",
        "- only single-factor `A/B` candidates are included",
        "- quarterly and annual targets are checked separately",
        "",
    ]
    if factor_df.empty:
        lines.append("- no factor rows")
    else:
        for target_label, group in factor_df.groupby("target_label"):
            lines.append(f"## {target_label}")
            lines.append(f"- factor count: `{len(group)}`")
            lines.append(f"- high-corr factors (`abs corr >= {CORR_ALERT_THRESHOLD}`): `{int(group['high_corr_flag'].sum())}`")
            lines.append(f"- high-VIF factors (`VIF >= 10`): `{int(group['vif_alert_flag'].sum())}`")
            top_corr = group.sort_values("max_abs_spearman_corr", ascending=False).head(5)
            lines.append("- highest-correlation factors:")
            for _, row in top_corr.iterrows():
                lines.append(
                    f"- `{row['factor_name']}` vs `{row['closest_factor']}` | corr=`{row['max_abs_spearman_corr']}` | vif=`{row['vif']}`"
                )
            if not pair_df.empty:
                pair_sub = pair_df[pair_df["target_label"] == target_label].sort_values("abs_spearman_corr", ascending=False).head(5)
                lines.append("- top pairwise correlations:")
                for _, row in pair_sub.iterrows():
                    lines.append(
                        f"- `{row['left_factor']}` vs `{row['right_factor']}` | corr=`{row['spearman_corr']}`"
                    )
            lines.append("")
    lines.extend(
        [
            "Outputs:",
            f"- [{OUTPUT_FACTORS_PATH.name}]({OUTPUT_FACTORS_PATH})",
            f"- [{OUTPUT_PAIRWISE_PATH.name}]({OUTPUT_PAIRWISE_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    panel_df = load_panel(PANEL_PATH)
    results_df = load_results(SINGLE_FACTOR_RESULTS_PATH)
    ab_df = results_df[results_df["final_status"].astype(str).isin(STATUS_KEEP)].copy()

    factor_rows: list[dict[str, object]] = []
    pairwise_rows: list[dict[str, object]] = []

    for target_label, group in ab_df.groupby("target_label"):
        feature_frame, usable_factors = build_target_subset(panel_df, group)
        group = group[group["factor_name"].isin(usable_factors)].copy()
        if feature_frame.empty or group.empty:
            continue
        feature_frame = feature_frame[group["factor_name"].tolist()].dropna()
        factor_rows.extend(build_factor_rows(feature_frame, group, target_label))
        pairwise_rows.extend(build_pairwise_rows(feature_frame, target_label))

    write_csv(OUTPUT_FACTORS_PATH, factor_rows)
    write_csv(OUTPUT_PAIRWISE_PATH, pairwise_rows)
    write_summary(factor_rows, pairwise_rows)
    print(f"factors={len(factor_rows)}")
    print(f"pairs={len(pairwise_rows)}")
    print(OUTPUT_FACTORS_PATH)
    print(OUTPUT_PAIRWISE_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
