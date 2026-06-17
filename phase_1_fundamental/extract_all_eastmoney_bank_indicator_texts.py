import csv
from pathlib import Path
import subprocess
import sys


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    batch_dir = base_dir / "eastmoney_reports" / "batch"
    manifest_path = batch_dir / "eastmoney_annual_report_manifest.csv"
    runner = base_dir / "extract_eastmoney_bank_indicator_samples.py"

    if not manifest_path.exists():
        raise RuntimeError(f"Missing manifest: {manifest_path}")

    pdf_names: list[str] = []
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            local_path = (row.get("local_path") or "").strip()
            status = (row.get("status") or "").strip()
            if status != "downloaded" or not local_path:
                continue
            path = Path(local_path)
            if path.exists() and path.stat().st_size > 1024 and path.read_bytes()[:5] == b"%PDF-":
                pdf_names.append(path.name)

    pdf_names = sorted(dict.fromkeys(pdf_names))
    if not pdf_names:
        raise RuntimeError("No valid downloaded PDFs found in the manifest.")

    chunk_size = 8
    for start in range(0, len(pdf_names), chunk_size):
        chunk = pdf_names[start:start + chunk_size]
        command = [sys.executable, str(runner)]
        for name in chunk:
            command.extend(["--pdf", name])
        print(f"Running chunk {start // chunk_size + 1}: {len(chunk)} PDFs")
        subprocess.run(command, check=True)

    print(f"Completed extraction for {len(pdf_names)} PDFs.")


if __name__ == "__main__":
    main()
