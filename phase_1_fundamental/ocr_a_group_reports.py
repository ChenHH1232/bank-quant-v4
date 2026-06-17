import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz


DEFAULT_PDFS = [
    "600036_XSHG_2024_annual_report.pdf",
    "600036_XSHG_2025_annual_report.pdf",
    "601328_XSHG_2024_annual_report.pdf",
    "601328_XSHG_2025_annual_report.pdf",
    "601398_XSHG_2025_annual_report.pdf",
]

KEYWORDS = [
    "资本充足率",
    "資本充足率",
    "资本适足率",
    "資本適足率",
    "一级资本充足率",
    "一級資本充足率",
    "一级资本适足率",
    "一級資本適足率",
    "核心一级资本充足率",
    "核心一級資本充足率",
    "核心一级资本适足率",
    "核心一級資本適足率",
    "不良贷款率",
    "不良貸款率",
    "不良贷款比率",
    "不良貸款比率",
    "拨备覆盖率",
    "撥備覆蓋率",
    "备抵覆盖率",
    "備抵覆蓋率",
    "拨贷比",
    "撥貸比",
    "贷款拨备率",
    "貸款撥備率",
    "流动性比例",
    "流動性比例",
    "流动性匹配率",
    "流動性匹配率",
    "流动性覆盖率",
    "流動性覆蓋率",
    "流动性覆盖比率",
    "流動性覆蓋比率",
    "单一最大客户贷款占资本净额比率",
    "單一最大客戶貸款占資本淨額比率",
    "单一客户贷款集中度",
    "單一客戶貸款集中度",
    "最大十家客户贷款占资本净额比率",
    "最大十家客戶貸款占資本淨額比率",
    "最大十家客户贷款集中度",
    "最大十家客戶貸款集中度",
    "单一集团客户授信集中度",
    "單一集團客戶授信集中度",
    "主要监管指标",
    "主要監管指標",
    "补充监管指标",
    "補充監管指標",
]

POWERSHELL_OCR_SCRIPT = r"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation.UniversalApiContract, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation.UniversalApiContract, ContentType=WindowsRuntime]

function Await([object]$Op, [type]$T) {
  $m = [System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } |
    Select-Object -First 1
  $task = $m.MakeGenericMethod($T).Invoke($null, @($Op))
  $task.Wait()
  return $task.Result
}

$imageDir = $args[0]
$outPath = $args[1]
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$builder = New-Object System.Text.StringBuilder
$files = Get-ChildItem -LiteralPath $imageDir -Filter *.png | Sort-Object Name

foreach ($fileItem in $files) {
  $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($fileItem.FullName)) ([Windows.Storage.StorageFile])
  $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
  [void]$builder.AppendLine(("===== PAGE {0} =====" -f $fileItem.BaseName))
  [void]$builder.AppendLine($result.Text)
  [void]$builder.AppendLine("")
}

[System.IO.File]::WriteAllText($outPath, $builder.ToString(), [System.Text.Encoding]::UTF8)
"""


def find_all(text: str, pattern: str):
    start = 0
    while True:
        idx = text.find(pattern, start)
        if idx < 0:
            return
        yield idx
        start = idx + len(pattern)


def collect_snippets(text: str) -> list[str]:
    snippets: list[str] = []
    seen: set[str] = set()
    for keyword in KEYWORDS:
        for idx in find_all(text, keyword):
            start = max(0, idx - 260)
            end = min(len(text), idx + len(keyword) + 520)
            snippet = text[start:end].replace("\x00", " ").strip()
            key = snippet[:240]
            if key in seen:
                continue
            seen.add(key)
            snippets.append(f"[{keyword}]\n{snippet}")
    return snippets


def render_pdf_to_images(pdf_path: Path, image_dir: Path) -> None:
    doc = fitz.open(pdf_path)
    matrix = fitz.Matrix(2, 2)
    for page_index in range(doc.page_count):
        out_path = image_dir / f"{page_index + 1:04d}.png"
        if out_path.exists():
            continue
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pix.save(out_path)


def run_windows_ocr(image_dir: Path, out_text_path: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as handle:
        handle.write(POWERSHELL_OCR_SCRIPT)
        script_path = Path(handle.name)

    try:
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                str(image_dir),
                str(out_text_path),
            ],
            check=True,
        )
    finally:
        script_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Windows OCR on selected annual report PDFs.")
    parser.add_argument(
        "--pdf",
        action="append",
        default=[],
        help="PDF filename under eastmoney_reports/batch. Can be passed multiple times.",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    batch_dir = base_dir / "eastmoney_reports" / "batch"
    out_dir = base_dir / "eastmoney_reports" / "ocr_text"
    temp_root = base_dir / "ocr_work"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_root.mkdir(parents=True, exist_ok=True)

    selected_pdfs = args.pdf or DEFAULT_PDFS

    for pdf_name in selected_pdfs:
        pdf_path = batch_dir / pdf_name
        stem = pdf_path.stem
        text_path = out_dir / f"{stem}_windows_ocr.txt"
        snippet_path = out_dir / f"{stem}_windows_ocr_bank_indicator_snippets.txt"
        image_dir = temp_root / stem / "pages"

        print(f"PROCESSING {pdf_name}")
        image_dir.mkdir(parents=True, exist_ok=True)
        render_pdf_to_images(pdf_path, image_dir)
        run_windows_ocr(image_dir, text_path)

        text = text_path.read_text(encoding="utf-8", errors="ignore")
        snippets = collect_snippets(text)
        snippet_path.write_text("\n\n-----\n\n".join(snippets) if snippets else "NO_HITS", encoding="utf-8")
        print(f"OCR_DONE text_chars={len(text)} snippets={len(snippets)}")

        shutil.rmtree(image_dir.parent, ignore_errors=True)


if __name__ == "__main__":
    main()
