import csv
from collections import defaultdict
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PAIRWISE_PATH = SCRIPT_DIR / "factor_pairwise_corr_v1.csv"
COLLINEARITY_PATH = SCRIPT_DIR / "factor_collinearity_v1.csv"
SINGLE_FACTOR_RESULTS_PATH = SCRIPT_DIR / "single_factor_test_results_v1.csv"
OUTPUT_CLUSTERS_PATH = SCRIPT_DIR / "factor_dedup_clusters_v1.csv"
OUTPUT_MEMBERS_PATH = SCRIPT_DIR / "factor_dedup_cluster_members_v1.csv"
SUMMARY_PATH = SCRIPT_DIR / "factor_dedup_clusters_v1.md"

CORR_THRESHOLD = 0.80


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, item: str) -> None:
        if item not in self.parent:
            self.parent[item] = item

    def find(self, item: str) -> str:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: str, right: str) -> None:
        self.add(left)
        self.add(right)
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def build_clusters(pairwise_df: pd.DataFrame, candidate_factors: set[str], target_label: str) -> list[list[str]]:
    uf = UnionFind()
    for factor in candidate_factors:
        uf.add(factor)

    sub = pairwise_df[
        (pairwise_df["target_label"] == target_label)
        & (pairwise_df["abs_spearman_corr"] >= CORR_THRESHOLD)
        & (pairwise_df["left_factor"].isin(candidate_factors))
        & (pairwise_df["right_factor"].isin(candidate_factors))
    ].copy()

    for _, row in sub.iterrows():
        uf.union(str(row["left_factor"]), str(row["right_factor"]))

    grouped: dict[str, list[str]] = defaultdict(list)
    for factor in candidate_factors:
        grouped[uf.find(factor)].append(factor)

    return [sorted(items) for items in grouped.values() if len(items) >= 2]


def choose_representative(cluster: list[str], score_map: dict[str, float], family_map: dict[str, str]) -> tuple[str, str]:
    sorted_members = sorted(
        cluster,
        key=lambda name: (
            -score_map.get(name, float("-inf")),
            family_map.get(name, ""),
            name,
        ),
    )
    keep = sorted_members[0]
    reason = "highest_validation_rank_ic_mean_within_cluster"
    return keep, reason


def main() -> None:
    pairwise_df = load_csv(PAIRWISE_PATH)
    collinearity_df = load_csv(COLLINEARITY_PATH)
    results_df = load_csv(SINGLE_FACTOR_RESULTS_PATH)

    candidate_df = collinearity_df.copy()
    family_map = {
        str(row["factor_name"]): str(row["factor_family"])
        for _, row in candidate_df.iterrows()
    }
    score_map = {
        str(row["factor_name"]): float(row["validation_rank_ic_mean"])
        for _, row in candidate_df.iterrows()
        if pd.notna(row["validation_rank_ic_mean"])
    }
    status_map = {
        str(row["factor_name"]): str(row["final_status"])
        for _, row in results_df.iterrows()
    }
    corr_map: dict[tuple[str, str], float] = {}
    for _, row in pairwise_df.iterrows():
        left = str(row["left_factor"])
        right = str(row["right_factor"])
        corr = float(row["spearman_corr"])
        corr_map[(left, right)] = corr
        corr_map[(right, left)] = corr

    cluster_rows: list[dict[str, object]] = []
    member_rows: list[dict[str, object]] = []
    cluster_id_counter = 1

    for target_label, target_group in candidate_df.groupby("target_label"):
        candidate_factors = set(target_group["factor_name"].astype(str))
        clusters = build_clusters(pairwise_df, candidate_factors, str(target_label))
        clusters = sorted(clusters, key=lambda items: (-len(items), items[0]))

        for cluster in clusters:
            keep_factor, keep_reason = choose_representative(cluster, score_map, family_map)
            cluster_id = f"{'Q' if 'quarter' in target_label else 'Y'}{cluster_id_counter:02d}"
            cluster_id_counter += 1

            validation_scores = [score_map.get(name, float("nan")) for name in cluster if name in score_map]
            best_score = max([value for value in validation_scores if pd.notna(value)], default=float("nan"))

            cluster_rows.append(
                {
                    "cluster_id": cluster_id,
                    "target_label": target_label,
                    "cluster_size": len(cluster),
                    "suggested_keep_factor": keep_factor,
                    "keep_factor_family": family_map.get(keep_factor, ""),
                    "keep_factor_validation_rank_ic_mean": round(float(best_score), 6) if pd.notna(best_score) else "",
                    "keep_reason": keep_reason,
                    "members_joined": " | ".join(cluster),
                }
            )

            for factor_name in cluster:
                relation_corr = ""
                if factor_name != keep_factor and (factor_name, keep_factor) in corr_map:
                    relation_corr = round(float(corr_map[(factor_name, keep_factor)]), 6)
                member_rows.append(
                    {
                        "cluster_id": cluster_id,
                        "target_label": target_label,
                        "factor_name": factor_name,
                        "factor_family": family_map.get(factor_name, ""),
                        "single_factor_status": status_map.get(factor_name, ""),
                        "validation_rank_ic_mean": round(float(score_map.get(factor_name, float("nan"))), 6) if pd.notna(score_map.get(factor_name, float("nan"))) else "",
                        "suggested_keep_flag": int(factor_name == keep_factor),
                        "suggested_drop_flag": int(factor_name != keep_factor),
                        "corr_to_keep_factor": relation_corr,
                    }
                )

    if cluster_rows:
        with OUTPUT_CLUSTERS_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(cluster_rows[0].keys()))
            writer.writeheader()
            writer.writerows(cluster_rows)
    else:
        OUTPUT_CLUSTERS_PATH.write_text("", encoding="utf-8")

    if member_rows:
        with OUTPUT_MEMBERS_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(member_rows[0].keys()))
            writer.writeheader()
            writer.writerows(member_rows)
    else:
        OUTPUT_MEMBERS_PATH.write_text("", encoding="utf-8")

    lines = [
        "# Factor Dedup Clusters V1",
        "",
        "Rule:",
        f"- built from pairwise `abs(spearman_corr) >= {CORR_THRESHOLD}`",
        "- only single-factor `A/B` candidates are included",
        "- quarterly and annual targets are clustered separately",
        "",
        f"- Total clusters: `{len(cluster_rows)}`",
        f"- Total clustered factors: `{len(member_rows)}`",
        "",
        "Clusters:",
    ]
    if not cluster_rows:
        lines.append("- none")
    else:
        for row in cluster_rows:
            lines.append(
                f"- `{row['cluster_id']}` | keep `{row['suggested_keep_factor']}` | size=`{row['cluster_size']}`"
            )
    lines.extend(
        [
            "",
            "Outputs:",
            f"- [{OUTPUT_CLUSTERS_PATH.name}]({OUTPUT_CLUSTERS_PATH})",
            f"- [{OUTPUT_MEMBERS_PATH.name}]({OUTPUT_MEMBERS_PATH})",
        ]
    )
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"clusters={len(cluster_rows)}")
    print(f"clustered_factors={len(member_rows)}")
    print(OUTPUT_CLUSTERS_PATH)
    print(OUTPUT_MEMBERS_PATH)
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
