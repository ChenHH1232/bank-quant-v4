import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from jqdatasdk import auth, get_all_securities, get_industry_stocks, get_query_count

from joinquant_window_probe import (
    fetch_annual_table,
    fetch_daily_price,
    fetch_daily_valuation,
    fetch_finance_table,
    fetch_quarterly_table,
    filter_finance_current_period,
    result_record,
    safe_save,
    year_range,
    quarter_labels,
)
from jqdatasdk import balance, bank_indicator, cash_flow, finance, income, indicator


DEFAULT_START = "2014-01-01"
DEFAULT_END = "2026-05-01"
DEFAULT_BANK_INDUSTRY_CODE = "801780"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = SCRIPT_DIR / "raw_downloads" / "all_banks"
STATE_PATH = DEFAULT_OUTPUT_ROOT / "download_state.json"
RUN_SUMMARY_PATH = DEFAULT_OUTPUT_ROOT / "run_summary.json"
FINAL_REPORT_PATH = DEFAULT_OUTPUT_ROOT / "final_report.txt"
UNIVERSE_PATH = DEFAULT_OUTPUT_ROOT / "bank_universe.csv"
WECHAT_SENDER = Path(r"D:\hh\codex\daily\send_personal_wechat_text.mjs")
TSX_CMD = Path(r"D:\hh\codex\codex-bridge\node_modules\.bin\tsx.cmd")
WECHAT_FALLBACK_LOG = DEFAULT_OUTPUT_ROOT / "wechat_fallback.log"

QUOTA_ERROR_MARKERS = [
    "频繁",
    "quota",
    "额度",
    "limit",
    "限制",
    "too many",
    "429",
]
CONNECTION_ERROR_MARKERS = [
    "最多只能开启 1 个连接",
]


@dataclass
class BankRecord:
    code: str
    display_name: str
    start_date: str
    end_date: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download full-window JoinQuant raw data for all bank-sector stocks with resumable progress."
    )
    parser.add_argument("--username", default=os.getenv("JQ_USERNAME"))
    parser.add_argument("--password", default=os.getenv("JQ_PASSWORD"))
    parser.add_argument("--start-date", default=DEFAULT_START)
    parser.add_argument("--end-date", default=DEFAULT_END)
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--bank-industry-code", default=DEFAULT_BANK_INDUSTRY_CODE)
    parser.add_argument("--poll-sleep-seconds", type=int, default=3)
    parser.add_argument("--retry-sleep-seconds", type=int, default=1800)
    parser.add_argument("--limit", type=int, default=0, help="Optional test limit. 0 means no limit.")
    parser.add_argument("--skip-wechat", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Resume from existing state if present.")
    return parser


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_wechat_text(message: str, disabled: bool) -> bool:
    if disabled:
        return False
    temp_path = DEFAULT_OUTPUT_ROOT / "_wechat_message.txt"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_text(message.strip() + "\n", encoding="utf-8")
    last_error = None
    for attempt in range(1, 4):
        try:
            result = subprocess.run(
                [str(TSX_CMD), str(WECHAT_SENDER), "--text-file", str(temp_path)],
                check=True,
                cwd=str(SCRIPT_DIR),
                capture_output=True,
                text=True,
            )
            return True
        except Exception as exc:
            last_error = exc
            time.sleep(3 * attempt)

    fallback = (
        f"[{now_text()}] send_failed\n"
        f"{message.strip()}\n"
        f"error={repr(last_error)}\n"
        f"{'-' * 60}\n"
    )
    WECHAT_FALLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    with WECHAT_FALLBACK_LOG.open("a", encoding="utf-8") as handle:
        handle.write(fallback)
    return False


def load_state(path: Path) -> dict:
    if not path.exists():
        return {
            "created_at": now_text(),
            "updated_at": now_text(),
            "status": "not_started",
            "completed_codes": [],
            "failed_codes": [],
            "current_code": None,
            "events": [],
            "run_started_at": now_text(),
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    state["updated_at"] = now_text()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def append_event(state: dict, level: str, message: str) -> None:
    state.setdefault("events", []).append(
        {
            "time": now_text(),
            "level": level,
            "message": message,
        }
    )


def enumerate_bank_universe(industry_code: str, start_date: str, end_date: str) -> list[BankRecord]:
    months = pd.date_range(start=start_date, end=end_date, freq="MS")
    codes: set[str] = set()
    for dt in months:
        stocks = get_industry_stocks(industry_code, dt.date())
        codes.update(stocks)

    meta = get_all_securities(["stock"])
    records: list[BankRecord] = []
    for code in sorted(codes):
        if code not in meta.index:
            continue
        row = meta.loc[code]
        records.append(
            BankRecord(
                code=code,
                display_name=str(row["display_name"]),
                start_date=str(row["start_date"].date()),
                end_date=str(row["end_date"].date()),
            )
        )
    return records


def save_universe(records: list[BankRecord], path: Path) -> None:
    df = pd.DataFrame(
        [
            {
                "code": item.code,
                "display_name": item.display_name,
                "start_date": item.start_date,
                "end_date": item.end_date,
            }
            for item in records
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def is_retryable_error(exc: Exception) -> bool:
    text = repr(exc)
    return any(marker in text for marker in QUOTA_ERROR_MARKERS + CONNECTION_ERROR_MARKERS)


def remaining_query_text() -> str:
    try:
        query_count = get_query_count()
        total = query_count.get("total")
        spare = query_count.get("spare")
        return f"total={total}, spare={spare}"
    except Exception as exc:
        return f"query_count_unavailable={repr(exc)}"


def save_summary(summary: list[dict[str, object]], path: Path) -> None:
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def download_one_bank(bank: BankRecord, start_date: str, end_date: str, output_root: Path) -> list[dict[str, object]]:
    effective_start = max(start_date, bank.start_date)
    output_dir = output_root / bank.code.replace(".", "_")
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: list[dict[str, object]] = []
    years = year_range(effective_start, end_date)
    quarter_keys = quarter_labels(effective_start, end_date)

    try:
        daily_df = fetch_daily_price(bank.code, effective_start, end_date)
        if daily_df.empty:
            summary.append(result_record("daily_price", "DATA_NOT_FOUND", 0, "No daily price rows returned."))
        else:
            safe_save(daily_df, output_dir / "daily_price.csv")
            summary.append(result_record("daily_price", "OK", len(daily_df), "Saved daily price window."))
    except Exception as exc:
        summary.append(result_record("daily_price", "DATA_NOT_FOUND", 0, repr(exc)))

    try:
        valuation_df = fetch_daily_valuation(bank.code, effective_start, end_date)
        if valuation_df.empty:
            summary.append(result_record("daily_valuation", "DATA_NOT_FOUND", 0, "No daily valuation rows returned."))
        else:
            safe_save(valuation_df, output_dir / "daily_valuation.csv")
            summary.append(
                result_record("daily_valuation", "OK", len(valuation_df), "Saved daily valuation / market-cap window.")
            )
    except Exception as exc:
        summary.append(result_record("daily_valuation", "DATA_NOT_FOUND", 0, repr(exc)))

    quarterly_tables = {
        "balance": balance,
        "income": income,
        "cash_flow": cash_flow,
        "indicator": indicator,
    }
    for name, table in quarterly_tables.items():
        df, missing_keys = fetch_quarterly_table(table, bank.code, quarter_keys)
        if df.empty:
            summary.append(
                result_record(name, "DATA_NOT_FOUND", 0, f"No rows returned. missing_periods={missing_keys}")
            )
            continue
        safe_save(df, output_dir / f"{name}.csv")
        summary.append(
            result_record(name, "OK_WITH_GAPS" if missing_keys else "OK", len(df), f"missing_periods={missing_keys}" if missing_keys else "")
        )

    annual_tables = {
        "bank_indicator": bank_indicator,
    }
    for name, table in annual_tables.items():
        df, missing_years = fetch_annual_table(table, bank.code, years)
        if df.empty:
            summary.append(result_record(name, "DATA_NOT_FOUND", 0, f"No rows returned. missing_years={missing_years}"))
            continue
        safe_save(df, output_dir / f"{name}.csv")
        summary.append(
            result_record(name, "OK_WITH_GAPS" if missing_years else "OK", len(df), f"missing_years={missing_years}" if missing_years else "")
        )

    finance_tables = {
        "finance_income_statement": finance.FINANCE_INCOME_STATEMENT,
        "finance_cashflow_statement": finance.FINANCE_CASHFLOW_STATEMENT,
        "finance_balance_sheet_parent": finance.FINANCE_BALANCE_SHEET_PARENT,
    }
    for name, table in finance_tables.items():
        df = fetch_finance_table(table, bank.code, effective_start, end_date)
        if df.empty:
            summary.append(result_record(name, "DATA_NOT_FOUND", 0, "No rows returned in window."))
            continue
        safe_save(df, output_dir / f"{name}_raw.csv")
        filtered_df = filter_finance_current_period(df)
        safe_save(filtered_df, output_dir / f"{name}_current_only.csv")
        detail = f"raw_rows={len(df)}, current_only_rows={len(filtered_df)}"
        if "report_type" in df.columns:
            counts = df["report_type"].value_counts(dropna=False).to_dict()
            detail += f", report_type_counts={counts}"
        summary.append(result_record(name, "OK", len(filtered_df), detail))

    save_summary(summary, output_dir / "summary.json")
    return summary


def summarize_bank_result(bank: BankRecord, summary: list[dict[str, object]]) -> str:
    ok_count = sum(1 for item in summary if str(item["status"]).startswith("OK"))
    gap_items = [item["dataset"] for item in summary if item["status"] == "OK_WITH_GAPS"]
    missing_items = [item["dataset"] for item in summary if item["status"] == "DATA_NOT_FOUND"]
    return (
        f"V4 银行数据下载进度\n"
        f"{bank.display_name} {bank.code} 已完成\n"
        f"成功数据集: {ok_count}/{len(summary)}\n"
        f"有缺口: {', '.join(gap_items) if gap_items else '无'}\n"
        f"缺失: {', '.join(missing_items) if missing_items else '无'}"
    )


def write_final_report(records: list[BankRecord], state: dict, output_root: Path) -> str:
    completed = set(state.get("completed_codes", []))
    failed = state.get("failed_codes", [])
    lines = [
        "V4 银行窗口期数据下载汇总",
        f"完成时间: {now_text()}",
        f"已完成银行数: {len(completed)} / {len(records)}",
        f"失败银行数: {len(failed)}",
        f"查询额度: {remaining_query_text()}",
        "",
        "已完成名单:",
    ]
    for bank in records:
        if bank.code in completed:
            lines.append(f"- {bank.display_name} {bank.code}")
    if failed:
        lines.append("")
        lines.append("失败名单:")
        for item in failed:
            lines.append(f"- {item['display_name']} {item['code']}: {item['error']}")
    report = "\n".join(lines)
    (output_root / "final_report.txt").write_text(report, encoding="utf-8")
    return report


def main() -> None:
    args = build_parser().parse_args()
    if not args.username or not args.password:
        raise RuntimeError("Missing JoinQuant credentials. Pass --username/--password or set JQ_USERNAME/JQ_PASSWORD.")

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    auth(args.username, args.password)

    state_path = output_root / STATE_PATH.name
    run_summary_path = output_root / RUN_SUMMARY_PATH.name
    final_report_path = output_root / FINAL_REPORT_PATH.name
    universe_path = output_root / UNIVERSE_PATH.name

    state = load_state(state_path) if args.resume else {
        "created_at": now_text(),
        "updated_at": now_text(),
        "status": "starting",
        "completed_codes": [],
        "failed_codes": [],
        "current_code": None,
        "events": [],
        "run_started_at": now_text(),
    }
    save_state(state_path, state)

    records = enumerate_bank_universe(args.bank_industry_code, args.start_date, args.end_date)
    if args.limit and args.limit > 0:
        records = records[: args.limit]
    save_universe(records, universe_path)

    send_wechat_text(
        (
            f"V4 银行批量下载已启动\n"
            f"窗口期: {args.start_date} 到 {args.end_date}\n"
            f"银行数量: {len(records)}\n"
            f"查询额度: {remaining_query_text()}"
        ),
        args.skip_wechat,
    )

    append_event(state, "info", f"Run started for {len(records)} banks.")
    state["status"] = "running"
    save_state(state_path, state)

    run_summary: list[dict[str, object]] = []

    for index, bank in enumerate(records, start=1):
        if bank.code in state.get("completed_codes", []):
            continue

        state["current_code"] = bank.code
        append_event(state, "info", f"Starting {bank.display_name} {bank.code} ({index}/{len(records)})")
        save_state(state_path, state)

        while True:
            try:
                summary = download_one_bank(bank, args.start_date, args.end_date, output_root)
                run_summary.append(
                    {
                        "code": bank.code,
                        "display_name": bank.display_name,
                        "summary": summary,
                    }
                )
                save_summary(run_summary, run_summary_path)
                state.setdefault("completed_codes", []).append(bank.code)
                append_event(state, "info", f"Completed {bank.display_name} {bank.code}")
                save_state(state_path, state)
                send_wechat_text(
                    (
                        f"{summarize_bank_result(bank, summary)}\n"
                        f"当前进度: {len(state['completed_codes'])}/{len(records)}\n"
                        f"查询额度: {remaining_query_text()}"
                    ),
                    args.skip_wechat,
                )
                break
            except Exception as exc:
                if is_retryable_error(exc):
                    message = (
                        f"V4 银行数据下载暂停\n"
                        f"当前银行: {bank.display_name} {bank.code}\n"
                        f"原因: {repr(exc)}\n"
                        f"将于约 {args.retry_sleep_seconds // 60} 分钟后重试\n"
                        f"查询额度: {remaining_query_text()}"
                    )
                    append_event(state, "warning", message)
                    state["status"] = "waiting_retry"
                    save_state(state_path, state)
                    send_wechat_text(message, args.skip_wechat)
                    time.sleep(args.retry_sleep_seconds)
                    state["status"] = "running"
                    save_state(state_path, state)
                    continue

                state.setdefault("failed_codes", []).append(
                    {
                        "code": bank.code,
                        "display_name": bank.display_name,
                        "error": repr(exc),
                    }
                )
                append_event(state, "error", f"Failed {bank.display_name} {bank.code}: {repr(exc)}")
                save_state(state_path, state)
                send_wechat_text(
                    (
                        f"V4 银行数据下载失败\n"
                        f"{bank.display_name} {bank.code}\n"
                        f"错误: {repr(exc)}\n"
                        f"当前进度: {len(state['completed_codes'])}/{len(records)}"
                    ),
                    args.skip_wechat,
                )
                break

        time.sleep(args.poll_sleep_seconds)

    state["status"] = "completed"
    state["current_code"] = None
    save_state(state_path, state)

    report = write_final_report(records, state, output_root)
    final_report_path.write_text(report, encoding="utf-8")
    send_wechat_text(report, args.skip_wechat)
    print(report)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
