import csv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CLUSTERS_PATH = SCRIPT_DIR / "factor_dedup_clusters_v1.csv"
MEMBERS_PATH = SCRIPT_DIR / "factor_dedup_cluster_members_v1.csv"
OUTPUT_CSV_PATH = SCRIPT_DIR / "factor_dedup_review_packet_v1.csv"
OUTPUT_MD_PATH = SCRIPT_DIR / "factor_dedup_review_packet_v1.md"
WECHAT_PATH = SCRIPT_DIR / "factor_dedup_review_packet_v1_wechat.txt"


FIELD_MEANING = {
    "balance__capital_reserve_fund": "资本公积，反映股本溢价等资本性积累。",
    "balance__cash_equivalents": "期末现金及现金等价物余额，反映账面流动现金头寸。",
    "balance__deferred_tax_assets": "递延所得税资产，反映未来可抵扣暂时性差异形成的资产。",
    "balance__equities_parent_company_owners": "归属于母公司股东权益，反映母公司口径净资产。",
    "balance__ordinary_risk_reserve_fund": "一般风险准备，银行为覆盖风险提取的准备。",
    "balance__total_assets": "总资产，反映银行整体规模。",
    "balance__total_liability": "总负债，反映银行整体负债规模。",
    "balance__total_owner_equities": "所有者权益合计，反映总净资产规模。",
    "cash_flow__interest_and_commission_cashin": "收取利息和手续费收到的现金，反映经营现金流入规模。",
    "cash_flow__staff_behalf_paid": "支付给职工以及为职工支付的现金，常与经营规模同步变化。",
    "income__commission_income": "手续费及佣金收入，反映中间业务收入规模。",
    "income__interest_expense": "利息支出，反映负债端资金成本规模。",
    "income__interest_income": "利息收入，反映生息资产收入规模。",
    "income__net_profit": "净利润，反映期间最终盈利规模。",
    "income__np_parent_company_owners": "归母净利润，反映归属于母公司股东的盈利。",
    "income__operating_profit": "营业利润，反映主营经营利润。",
    "income__operating_revenue": "营业收入，反映收入总规模。",
    "income__total_profit": "利润总额，税前利润口径。",
    "indicator__adjusted_profit": "调整后利润，剔除部分非经常性影响后的利润口径。",
    "indicator__operating_profit": "经营利润指标口径，和利润表经营利润高度接近。",
    "cash_flow__invest_cash_paid": "投资支付的现金，反映投资现金流出。",
    "cash_flow__invest_withdrawal_cash": "收回投资收到的现金，反映投资现金流入。",
    "cash_flow__subtotal_invest_cash_inflow": "投资活动现金流入小计，投资流入总额。",
    "cash_flow__subtotal_invest_cash_outflow": "投资活动现金流出小计，投资流出总额。",
    "indicator__inc_net_profit_annual": "净利润同比增速，反映年度盈利改善。",
    "indicator__inc_net_profit_to_shareholders_annual": "归母净利润同比增速，和净利润同比几乎同义。",
    "indicator__inc_operation_profit_annual": "营业利润同比增速，反映经营利润改善。",
    "indicator__inc_return": "净资产收益率类回报指标口径，与 ROE 高度接近。",
    "indicator__roa": "总资产收益率，反映资产使用效率。",
    "indicator__roe": "净资产收益率，反映股东资本回报能力。",
    "cash_flow__net_operate_cash_flow": "经营活动现金流净额，反映经营现金创造能力。",
    "indicator__ocf_to_revenue": "经营现金流/收入，反映收入含金量。",
    "income__investment_income": "投资收益，反映投资类业务贡献。",
    "indicator__value_change_profit": "公允价值变动收益，反映估值变动类收益。",
    "indicator__net_profit_margin": "净利率，净利润/收入。",
    "indicator__net_profit_to_total_revenue": "净利润占总收入比，和净利率几乎同义。",
}

CLUSTER_THEMES = {
    "Q01": "大规模簇：多数成员都在共同反映银行体量、经营规模或利润规模，强烈疑似“规模因子簇”。",
    "Q02": "投资现金流簇：本质上都在描述投资活动流入/流出。",
    "Q03": "利润增速簇：都在描述利润改善速度。",
    "Q04": "盈利能力簇：都在描述资本或资产回报能力。",
    "Q05": "现金含金量簇：都在描述经营现金流质量。",
    "Q06": "投资/估值收益簇：都和投资类或公允价值收益相关。",
    "Q07": "净利率簇：两个字段基本是重复口径。",
}


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_outputs() -> tuple[list[dict[str, str]], str, str]:
    cluster_rows = load_rows(CLUSTERS_PATH)
    member_rows = load_rows(MEMBERS_PATH)

    members_by_cluster: dict[str, list[dict[str, str]]] = {}
    for row in member_rows:
        members_by_cluster.setdefault(row["cluster_id"], []).append(row)

    review_rows: list[dict[str, str]] = []
    md_lines = [
        "# Factor Dedup Review Packet V1",
        "",
        "Purpose:",
        "- prepare a human-review packet for factor de-duplication",
        "- explain each high-correlation cluster in plain language",
        "- mark suggested keep and suggested drop candidates before manual override",
        "",
    ]
    wx_lines = [
        "V4高相关簇人工审核包已生成",
        "",
        "用途：给你人工判断哪些因子保留、哪些删掉降重",
        f"详细文件：{OUTPUT_MD_PATH}",
        "",
        "本轮高相关簇：",
    ]

    for cluster in cluster_rows:
        cluster_id = cluster["cluster_id"]
        theme = CLUSTER_THEMES.get(cluster_id, "高相关重复簇。")
        keep_factor = cluster["suggested_keep_factor"]
        md_lines.append(f"## {cluster_id}")
        md_lines.append("")
        md_lines.append(f"- Suggested keep: `{keep_factor}`")
        md_lines.append(f"- Theme: {theme}")
        md_lines.append(f"- Keep reason: `{cluster['keep_reason']}`")
        md_lines.append("")
        md_lines.append("Members:")
        wx_lines.append(f"{cluster_id}: 保留 {keep_factor}")

        sorted_members = sorted(
            members_by_cluster.get(cluster_id, []),
            key=lambda row: (row["suggested_keep_flag"] != "1", row["factor_name"]),
        )
        for member in sorted_members:
            factor_name = member["factor_name"]
            review_rows.append(
                {
                    "cluster_id": cluster_id,
                    "target_label": member["target_label"],
                    "factor_name": factor_name,
                    "factor_family": member["factor_family"],
                    "meaning_cn": FIELD_MEANING.get(factor_name, ""),
                    "cluster_theme_cn": theme,
                    "single_factor_status": member["single_factor_status"],
                    "validation_rank_ic_mean": member["validation_rank_ic_mean"],
                    "suggested_keep_flag": member["suggested_keep_flag"],
                    "suggested_drop_flag": member["suggested_drop_flag"],
                    "corr_to_keep_factor": member["corr_to_keep_factor"],
                    "manual_review_note": "",
                }
            )
            md_lines.append(
                f"- `{factor_name}` | keep=`{member['suggested_keep_flag']}` | val_ic=`{member['validation_rank_ic_mean']}` | corr_to_keep=`{member['corr_to_keep_factor']}`"
            )
            md_lines.append(f"  Meaning: {FIELD_MEANING.get(factor_name, 'TBD')}")
        md_lines.append("")

    md_lines.extend(
        [
            "Outputs:",
            f"- [{OUTPUT_CSV_PATH.name}]({OUTPUT_CSV_PATH})",
        ]
    )
    wx_lines.extend(
        [
            "",
            f"详细报告已写入：{OUTPUT_MD_PATH}",
        ]
    )
    return review_rows, "\n".join(md_lines), "\n".join(wx_lines)


def main() -> None:
    rows, md_text, wechat_text = build_outputs()
    if rows:
        with OUTPUT_CSV_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        OUTPUT_CSV_PATH.write_text("", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(md_text, encoding="utf-8")
    WECHAT_PATH.write_text(wechat_text, encoding="utf-8")
    print(f"rows={len(rows)}")
    print(OUTPUT_CSV_PATH)
    print(OUTPUT_MD_PATH)
    print(WECHAT_PATH)


if __name__ == "__main__":
    main()
