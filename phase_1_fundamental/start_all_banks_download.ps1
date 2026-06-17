$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe"
$scriptPath = Join-Path $projectRoot "download_all_banks_joinquant.py"
$logDir = Join-Path $projectRoot "raw_downloads\all_banks\logs"
$stdoutLog = Join-Path $logDir "stdout.log"
$stderrLog = Join-Path $logDir "stderr.log"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$arguments = @(
  $scriptPath
  "--username", "18258118862"
  "--password", "Chenzenghao123"
  "--start-date", "2014-01-01"
  "--end-date", "2026-05-01"
  "--resume"
)

Start-Process `
  -FilePath $pythonExe `
  -ArgumentList $arguments `
  -WorkingDirectory $projectRoot `
  -WindowStyle Hidden `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog

Write-Output "Started background bank download."
Write-Output "Stdout log: $stdoutLog"
Write-Output "Stderr log: $stderrLog"
