import argparse
import csv
import random
import re
import time
from http.cookies import SimpleCookie
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


NOTICE_LIST_URL = "https://np-anotice-stock.eastmoney.com/api/security/ann"
NOTICE_CONTENT_URL = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)
ANNUAL_REPORT_TITLE_RE = re.compile(r":.*?(?P<report_year>\d{4})(?:\u5e74)?\u5e74\u5ea6\u62a5\u544a$")
ANNUAL_REPORT_SUMMARY_RE = re.compile(r":.*?(?P<report_year>\d{4})(?:\u5e74)?\u5e74\u5ea6\u62a5\u544a\u6458\u8981$")
EASTMONEY_JS_CHALLENGE_RE = re.compile(
    r"WTKkN:(?P<a>\d+),bOYDu:(?P<b>\d+).*?wyeCN:(?P<c>\d+)",
    re.DOTALL,
)


@dataclass(frozen=True)
class BankTarget:
    local_code: str
    stock_code: str
    market_code: str

    @property
    def eastmoney_symbol(self) -> str:
        return f"{self.market_code}{self.stock_code}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download Eastmoney annual report PDFs for the bank universe with gentle rate limiting."
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2024,
        help="First report year to keep. Defaults to 2024.",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2025,
        help="Last report year to keep. Defaults to 2025.",
    )
    parser.add_argument(
        "--bank-code",
        action="append",
        default=[],
        help="Optional local bank code filter such as 000001_XSHE. Can be passed multiple times.",
    )
    parser.add_argument(
        "--page-limit",
        type=int,
        default=20,
        help="Maximum notice pages to scan per stock. Defaults to 20.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Notice page size for the Eastmoney API. Defaults to 50.",
    )
    parser.add_argument(
        "--sleep-min",
        type=float,
        default=1.5,
        help="Minimum seconds to sleep between HTTP requests. Defaults to 1.5.",
    )
    parser.add_argument(
        "--sleep-max",
        type=float,
        default=3.5,
        help="Maximum seconds to sleep between HTTP requests. Defaults to 3.5.",
    )
    parser.add_argument(
        "--bank-sleep-min",
        type=float,
        default=4.0,
        help="Minimum seconds to sleep between banks. Defaults to 4.0.",
    )
    parser.add_argument(
        "--bank-sleep-max",
        type=float,
        default=8.0,
        help="Maximum seconds to sleep between banks. Defaults to 8.0.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts per request. Defaults to 3.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=25,
        help="HTTP timeout in seconds. Defaults to 25.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional output directory override. Defaults to phase_1_fundamental/eastmoney_reports/batch.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload existing PDFs instead of skipping them.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve matching annual reports without downloading the PDFs.",
    )
    return parser


def get_default_output_dir() -> Path:
    return Path(__file__).resolve().parent / "eastmoney_reports" / "batch"


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Referer": "https://data.eastmoney.com/",
        }
    )
    return session


def sleep_between(min_seconds: float, max_seconds: float) -> None:
    low = min(min_seconds, max_seconds)
    high = max(min_seconds, max_seconds)
    time.sleep(random.uniform(low, high))


def request_json(
    session: requests.Session,
    url: str,
    params: dict,
    timeout: int,
    max_retries: int,
    sleep_min: float,
    sleep_max: float,
) -> dict:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = exc
            if attempt == max_retries:
                break
            sleep_between(sleep_min, sleep_max)
    raise RuntimeError(f"Request failed for {url} params={params}") from last_error


def request_binary(
    session: requests.Session,
    url: str,
    timeout: int,
    max_retries: int,
    sleep_min: float,
    sleep_max: float,
) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            payload = response.content
            if payload.startswith(b"%PDF-"):
                return payload

            if maybe_solve_eastmoney_js_challenge(session=session, url=url, payload=payload):
                retry_response = session.get(url, timeout=timeout)
                retry_response.raise_for_status()
                retry_payload = retry_response.content
                if retry_payload.startswith(b"%PDF-"):
                    return retry_payload
                payload = retry_payload

            if payload.startswith(b"%PDF-"):
                return payload

            raise RuntimeError("Downloaded payload is not a PDF.")
        except Exception as exc:
            last_error = exc
            if attempt == max_retries:
                break
            sleep_between(sleep_min, sleep_max)
    raise RuntimeError(f"Binary download failed for {url}") from last_error


def maybe_solve_eastmoney_js_challenge(
    session: requests.Session,
    url: str,
    payload: bytes,
) -> bool:
    text = payload.decode("utf-8", errors="ignore")
    if "__tst_status" not in text or "EO_Bot_Ssid" not in text:
        return False

    match = EASTMONEY_JS_CHALLENGE_RE.search(text)
    if not match:
        return False

    seed = int(match.group("a")) + int(match.group("b")) + int(match.group("c"))
    bot_ssid = seed + 3288924160

    cookie = SimpleCookie()
    cookie["__tst_status"] = f"{seed}#"
    cookie["EO_Bot_Ssid"] = str(bot_ssid)

    for morsel in cookie.values():
        session.cookies.set(morsel.key, morsel.value, domain="pdf.dfcfw.com", path="/")

    return True


def discover_bank_targets(raw_downloads_dir: Path) -> list[BankTarget]:
    targets: list[BankTarget] = []
    for bank_dir in sorted(raw_downloads_dir.iterdir()):
        if not bank_dir.is_dir():
            continue
        name = bank_dir.name
        if "_" not in name:
            continue
        stock_code, local_exchange = name.split("_", 1)
        if local_exchange == "XSHE":
            market_code = "0"
        elif local_exchange == "XSHG":
            market_code = "1"
        else:
            continue
        targets.append(
            BankTarget(
                local_code=name,
                stock_code=stock_code,
                market_code=market_code,
            )
        )
    return targets


def find_matching_reports(
    session: requests.Session,
    bank: BankTarget,
    start_year: int,
    end_year: int,
    page_limit: int,
    page_size: int,
    timeout: int,
    max_retries: int,
    sleep_min: float,
    sleep_max: float,
) -> dict[int, dict]:
    found: dict[int, dict] = {}

    for page_index in range(1, page_limit + 1):
        payload = request_json(
            session=session,
            url=NOTICE_LIST_URL,
            params={
                "ann_type": "A",
                "client_source": "web",
                "stock_list": bank.stock_code,
                "page_index": page_index,
                "page_size": page_size,
            },
            timeout=timeout,
            max_retries=max_retries,
            sleep_min=sleep_min,
            sleep_max=sleep_max,
        )
        notice_list = payload.get("data", {}).get("list", [])
        if not notice_list:
            break

        for item in notice_list:
            title = item.get("title", "")
            summary_match = ANNUAL_REPORT_SUMMARY_RE.search(title)
            if summary_match:
                continue
            match = ANNUAL_REPORT_TITLE_RE.search(title)
            if not match:
                continue
            report_year = int(match.group("report_year"))
            if report_year < start_year or report_year > end_year:
                continue
            if report_year in found:
                continue
            found[report_year] = item

        if all(year in found for year in range(start_year, end_year + 1)):
            break

        sleep_between(sleep_min, sleep_max)

    return found


def enrich_with_pdf_url(
    session: requests.Session,
    art_code: str,
    timeout: int,
    max_retries: int,
    sleep_min: float,
    sleep_max: float,
) -> dict:
    payload = request_json(
        session=session,
        url=NOTICE_CONTENT_URL,
        params={
            "art_code": art_code,
            "client_source": "web",
            "page_index": 1,
        },
        timeout=timeout,
        max_retries=max_retries,
        sleep_min=sleep_min,
        sleep_max=sleep_max,
    )
    return payload.get("data", {})


def sanitize_title_for_csv(title: str) -> str:
    return title.replace("\r", " ").replace("\n", " ").strip()


def save_manifest(manifest_path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "local_code",
        "stock_code",
        "market_code",
        "report_year",
        "notice_date",
        "art_code",
        "title",
        "pdf_url",
        "status",
        "local_path",
    ]
    with manifest_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = build_parser().parse_args()
    base_dir = Path(__file__).resolve().parent
    raw_downloads_dir = base_dir / "raw_downloads" / "all_banks"
    output_dir = Path(args.output_dir) if args.output_dir else get_default_output_dir()
    manifest_path = output_dir / "eastmoney_annual_report_manifest.csv"

    if not raw_downloads_dir.exists():
        raise RuntimeError(f"Missing bank raw download directory: {raw_downloads_dir}")

    targets = discover_bank_targets(raw_downloads_dir)
    if args.bank_code:
        bank_filter = set(args.bank_code)
        targets = [target for target in targets if target.local_code in bank_filter]

    if not targets:
        raise RuntimeError("No bank targets matched the current filters.")

    output_dir.mkdir(parents=True, exist_ok=True)
    session = build_session()
    manifest_rows: list[dict] = []

    for idx, bank in enumerate(targets, start=1):
        print(f"[{idx}/{len(targets)}] scanning {bank.local_code}")
        try:
            reports = find_matching_reports(
                session=session,
                bank=bank,
                start_year=args.start_year,
                end_year=args.end_year,
                page_limit=args.page_limit,
                page_size=args.page_size,
                timeout=args.timeout,
                max_retries=args.max_retries,
                sleep_min=args.sleep_min,
                sleep_max=args.sleep_max,
            )
        except Exception as exc:
            for report_year in range(args.start_year, args.end_year + 1):
                manifest_rows.append(
                    {
                        "local_code": bank.local_code,
                        "stock_code": bank.stock_code,
                        "market_code": bank.market_code,
                        "report_year": report_year,
                        "notice_date": "",
                        "art_code": "",
                        "title": "",
                        "pdf_url": "",
                        "status": f"scan_failed: {exc}",
                        "local_path": "",
                    }
                )
            save_manifest(manifest_path, manifest_rows)
            print(f"  scan failed: {exc}")
            sleep_between(args.bank_sleep_min, args.bank_sleep_max)
            continue

        for report_year in range(args.start_year, args.end_year + 1):
            item = reports.get(report_year)
            if not item:
                manifest_rows.append(
                    {
                        "local_code": bank.local_code,
                        "stock_code": bank.stock_code,
                        "market_code": bank.market_code,
                        "report_year": report_year,
                        "notice_date": "",
                        "art_code": "",
                        "title": "",
                        "pdf_url": "",
                        "status": "not_found",
                        "local_path": "",
                    }
                )
                print(f"  {report_year}: not found")
                continue

            art_code = item["art_code"]
            title = sanitize_title_for_csv(item.get("title", ""))
            notice_date = item.get("notice_date", "")[:10]

            try:
                detail = enrich_with_pdf_url(
                    session=session,
                    art_code=art_code,
                    timeout=args.timeout,
                    max_retries=args.max_retries,
                    sleep_min=args.sleep_min,
                    sleep_max=args.sleep_max,
                )
            except Exception as exc:
                manifest_rows.append(
                    {
                        "local_code": bank.local_code,
                        "stock_code": bank.stock_code,
                        "market_code": bank.market_code,
                        "report_year": report_year,
                        "notice_date": notice_date,
                        "art_code": art_code,
                        "title": title,
                        "pdf_url": "",
                        "status": f"detail_failed: {exc}",
                        "local_path": "",
                    }
                )
                print(f"  {report_year}: detail fetch failed")
                continue

            pdf_url = detail.get("attach_url_web", "")
            if not pdf_url:
                manifest_rows.append(
                    {
                        "local_code": bank.local_code,
                        "stock_code": bank.stock_code,
                        "market_code": bank.market_code,
                        "report_year": report_year,
                        "notice_date": notice_date,
                        "art_code": art_code,
                        "title": title,
                        "pdf_url": "",
                        "status": "pdf_missing",
                        "local_path": "",
                    }
                )
                print(f"  {report_year}: pdf missing")
                continue

            output_file = output_dir / f"{bank.local_code}_{report_year}_annual_report.pdf"
            if output_file.exists() and not args.force:
                manifest_rows.append(
                    {
                        "local_code": bank.local_code,
                        "stock_code": bank.stock_code,
                        "market_code": bank.market_code,
                        "report_year": report_year,
                        "notice_date": notice_date,
                        "art_code": art_code,
                        "title": title,
                        "pdf_url": pdf_url,
                        "status": "exists_skipped",
                        "local_path": str(output_file),
                    }
                )
                print(f"  {report_year}: already exists")
                continue

            if args.dry_run:
                manifest_rows.append(
                    {
                        "local_code": bank.local_code,
                        "stock_code": bank.stock_code,
                        "market_code": bank.market_code,
                        "report_year": report_year,
                        "notice_date": notice_date,
                        "art_code": art_code,
                        "title": title,
                        "pdf_url": pdf_url,
                        "status": "dry_run",
                        "local_path": str(output_file),
                    }
                )
                print(f"  {report_year}: resolved")
                continue

            try:
                payload = request_binary(
                    session=session,
                    url=pdf_url,
                    timeout=args.timeout,
                    max_retries=args.max_retries,
                    sleep_min=args.sleep_min,
                    sleep_max=args.sleep_max,
                )
            except Exception as exc:
                manifest_rows.append(
                    {
                        "local_code": bank.local_code,
                        "stock_code": bank.stock_code,
                        "market_code": bank.market_code,
                        "report_year": report_year,
                        "notice_date": notice_date,
                        "art_code": art_code,
                        "title": title,
                        "pdf_url": pdf_url,
                        "status": f"download_failed: {exc}",
                        "local_path": str(output_file),
                    }
                )
                print(f"  {report_year}: download failed")
                continue

            output_file.write_bytes(payload)
            manifest_rows.append(
                {
                    "local_code": bank.local_code,
                    "stock_code": bank.stock_code,
                    "market_code": bank.market_code,
                    "report_year": report_year,
                    "notice_date": notice_date,
                    "art_code": art_code,
                    "title": title,
                    "pdf_url": pdf_url,
                    "status": "downloaded",
                    "local_path": str(output_file),
                }
            )
            print(f"  {report_year}: downloaded")
            sleep_between(args.sleep_min, args.sleep_max)

        save_manifest(manifest_path, manifest_rows)

        if idx < len(targets):
            sleep_between(args.bank_sleep_min, args.bank_sleep_max)

    print(f"manifest written to: {manifest_path}")


if __name__ == "__main__":
    main()
