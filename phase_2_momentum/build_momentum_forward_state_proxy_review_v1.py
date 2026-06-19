from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PANEL_PATH = SCRIPT_DIR / "momentum_monthly_rebalance_panel_v2.csv"
OUT_CSV_PATH = SCRIPT_DIR / "momentum_forward_state_proxy_review_v1.csv"
OUT_MD_PATH = SCRIPT_DIR / "momentum_forward_state_proxy_review_v1.md"

POOL_FLAG = "rebalance_stock_pool_flag_v2"
TARGET_COL = "y_month_total_return_close"
MIN_NAMES_PER_DATE = 5


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df = df[(df[POOL_FLAG] == 1) & (df["rebalance_date"] < pd.Timestamp("2021-01-01"))].copy()
    for col in [
        "mom_3_1",
        "mom_6_1",
        "mom_12_1",
        "avg_money_20d_pre_rebalance",
        "avg_market_cap_20d_pre_rebalance",
        TARGET_COL,
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def assign_groups(values: pd.Series, group_count: int) -> pd.Series:
    ranked = values.rank(method="first")
    try:
        return pd.qcut(ranked, q=group_count, labels=False, duplicates="drop") + 1
    except ValueError:
        return pd.Series(index=values.index, dtype="float64")


def compute_rank_ic(x: pd.Series, y: pd.Series) -> float:
    rx = x.rank(method="average")
    ry = y.rank(method="average")
    value = rx.corr(ry, method="pearson")
    return float(value) if not pd.isna(value) else np.nan


def build_proxy_table(panel_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rebalance_date, group in panel_df.groupby("rebalance_date", sort=True):
        if len(group) < MIN_NAMES_PER_DATE:
            continue
        mom6 = group["mom_6_1"].dropna()
        money = group["avg_money_20d_pre_rebalance"].dropna()
        mcap = group["avg_market_cap_20d_pre_rebalance"].dropna()
        target = pd.to_numeric(group[TARGET_COL], errors="coerce").dropna()

        if len(mom6) < MIN_NAMES_PER_DATE or len(target) < MIN_NAMES_PER_DATE:
            continue

        rows.append(
            {
                "rebalance_date": rebalance_date,
                "forward_pool_mean_return": float(group[TARGET_COL].mean()),
                "forward_pool_median_return": float(group[TARGET_COL].median()),
                "cross_mom6_median": float(mom6.median()),
                "cross_mom6_mean": float(mom6.mean()),
                "cross_mom6_top_bottom_spread": float(mom6.quantile(0.8) - mom6.quantile(0.2)),
                "cross_mom6_positive_ratio": float((mom6 > 0).mean()),
                "cross_mom12_median": float(group["mom_12_1"].dropna().median()) if group["mom_12_1"].dropna().size > 0 else np.nan,
                "cross_money_median": float(money.median()) if len(money) > 0 else np.nan,
                "cross_money_mean": float(money.mean()) if len(money) > 0 else np.nan,
                "cross_mcap_median": float(mcap.median()) if len(mcap) > 0 else np.nan,
                "cross_target_dispersion": float(target.quantile(0.8) - target.quantile(0.2)),
                "cross_factor_ic_mom6": compute_rank_ic(group["mom_6_1"], group[TARGET_COL]),
                "cross_factor_ic_mom12": compute_rank_ic(group["mom_12_1"], group[TARGET_COL]),
            }
        )
    out = pd.DataFrame(rows).sort_values("rebalance_date").reset_index(drop=True)
    out["year"] = out["rebalance_date"].dt.year
    return out


def evaluate_proxy(proxies: pd.DataFrame, proxy_col: str) -> dict[str, object]:
    sample = proxies[[proxy_col, "forward_pool_mean_return", "cross_factor_ic_mom6", "cross_factor_ic_mom12"]].copy()
    sample = sample.dropna(subset=[proxy_col, "forward_pool_mean_return"])
    if len(sample) == 0:
        return {
            "proxy_col": proxy_col,
            "corr_forward_mean": np.nan,
            "corr_mom6_ic": np.nan,
            "corr_mom12_ic": np.nan,
            "top_third_forward_mean": np.nan,
            "bottom_third_forward_mean": np.nan,
            "top_third_mom6_ic": np.nan,
            "bottom_third_mom6_ic": np.nan,
        }

    ranked = sample[proxy_col].rank(method="first")
    sample["_bucket"] = assign_groups(ranked, 3)
    top = sample[sample["_bucket"] == 3]
    bottom = sample[sample["_bucket"] == 1]

    return {
        "proxy_col": proxy_col,
        "corr_forward_mean": float(sample[proxy_col].corr(sample["forward_pool_mean_return"])) if len(sample) > 1 else np.nan,
        "corr_mom6_ic": float(sample[proxy_col].corr(sample["cross_factor_ic_mom6"])) if sample["cross_factor_ic_mom6"].notna().sum() > 1 else np.nan,
        "corr_mom12_ic": float(sample[proxy_col].corr(sample["cross_factor_ic_mom12"])) if sample["cross_factor_ic_mom12"].notna().sum() > 1 else np.nan,
        "top_third_forward_mean": float(top["forward_pool_mean_return"].mean()) if len(top) > 0 else np.nan,
        "bottom_third_forward_mean": float(bottom["forward_pool_mean_return"].mean()) if len(bottom) > 0 else np.nan,
        "top_third_mom6_ic": float(top["cross_factor_ic_mom6"].mean()) if len(top) > 0 else np.nan,
        "bottom_third_mom6_ic": float(bottom["cross_factor_ic_mom6"].mean()) if len(bottom) > 0 else np.nan,
    }


def write_summary(proxy_eval_df: pd.DataFrame) -> None:
    ranked = proxy_eval_df.sort_values(["corr_mom6_ic", "corr_forward_mean"], ascending=[False, False]).reset_index(drop=True)
    lines = [
        "# Momentum Forward State Proxy Review V1",
        "",
        "Scope:",
        "- sample window: `2014-01-01` to `2020-12-31`",
        "- objective: use only contemporaneously observable monthly cross-sectional features to proxy whether the next period is favorable to `mom_6_1`",
        "",
        "Proxy ranking:",
    ]
    for _, row in ranked.iterrows():
        lines.append(
            "- `{proxy}` | corr_forward=`{cf}` | corr_mom6_ic=`{c6}` | corr_mom12_ic=`{c12}` | top3_forward=`{tf}` | bot3_forward=`{bf}` | top3_mom6_ic=`{t6}` | bot3_mom6_ic=`{b6}`".format(
                proxy=row["proxy_col"],
                cf=format_float(row["corr_forward_mean"]),
                c6=format_float(row["corr_mom6_ic"]),
                c12=format_float(row["corr_mom12_ic"]),
                tf=format_float(row["top_third_forward_mean"]),
                bf=format_float(row["bottom_third_forward_mean"]),
                t6=format_float(row["top_third_mom6_ic"]),
                b6=format_float(row["bottom_third_mom6_ic"]),
            )
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "- a useful forward proxy should ideally be positively related both to next-period pool return and to next-period `mom_6_1` IC",
            "- if the same proxy also boosts `mom_12_1`, it may be a broad state signal rather than a specifically medium-term momentum state signal",
            "",
            "Output:",
            f"- [{OUT_CSV_PATH.name}]({OUT_CSV_PATH})",
        ]
    )
    OUT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_float(value: object, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return "nan"
    return f"{float(value):.{digits}f}"


def main() -> None:
    panel_df = load_panel()
    proxy_table = build_proxy_table(panel_df)
    proxy_cols = [
        "cross_mom6_median",
        "cross_mom6_mean",
        "cross_mom6_top_bottom_spread",
        "cross_mom6_positive_ratio",
        "cross_mom12_median",
        "cross_money_median",
        "cross_money_mean",
        "cross_mcap_median",
        "cross_target_dispersion",
    ]
    rows = [evaluate_proxy(proxy_table, proxy_col) for proxy_col in proxy_cols]
    out = pd.DataFrame(rows).sort_values(["corr_mom6_ic", "corr_forward_mean"], ascending=[False, False]).reset_index(drop=True)
    out.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8-sig")
    write_summary(out)
    print(f"saved proxy csv -> {OUT_CSV_PATH}")
    print(f"saved proxy md -> {OUT_MD_PATH}")


if __name__ == "__main__":
    main()
