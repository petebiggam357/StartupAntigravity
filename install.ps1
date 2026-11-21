<#
.SYNOPSIS
  Startup Antigravity — One-Command Windows 10/11 PowerShell Installer.
.DESCRIPTION
  Verifies Python 3.10+ (and fixes the common Windows python3 alias gap),
  installs Startup Antigravity into $env:USERPROFILE\.gemini\config\plugins\startup-antigravity,
  and runs the built-in self-test suite.
.EXAMPLE
  .\install.ps1
  .\install.ps1 -Junction
#>
param(
  [switch]$Junction
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/petebiggam357/StartupAntigravity.git"
$PluginsRoot = Join-Path $env:USERPROFILE ".gemini\config\plugins"
$TargetDir = Join-Path $PluginsRoot "startup-antigravity"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==> Checking Python 3.10+..." -ForegroundColor Cyan
$pyCmd = $null
foreach ($candidate in @("python3", "python")) {
  $found = Get-Command $candidate -ErrorAction SilentlyContinue
  if ($found -and $found.Source -notlike "*WindowsApps*") {
    $pyCmd = $found.Source
    break
  }
}

if (-not $pyCmd) {
  Write-Host "ERROR: Real Python 3.10+ not found on PATH (Microsoft Store stubs do not count)." -ForegroundColor Red
  Write-Host "Install via: winget install --id Python.Python.3.12 -e --source winget" -ForegroundColor Yellow
  Write-Host "Then disable python/python3 App Execution Aliases in Windows Settings -> Apps -> Advanced app settings." -ForegroundColor Yellow
  exit 1
}

& $pyCmd -c "import sys; assert sys.version_info >= (3, 10), f'Python 3.10+ required, got {sys.version}'"
$pyDir = Split-Path -Parent $pyCmd
$py3Shim = Join-Path $pyDir "python3.exe"
if (-not (Test-Path $py3Shim)) {
  Write-Host "==> Creating python3.exe shim beside python.exe so Antigravity hooks/MCP resolve cleanly..." -ForegroundColor Yellow
  Copy-Item $pyCmd $py3Shim
}
Write-Host "    Using $(& $pyCmd --version) at $pyCmd" -ForegroundColor Green

New-Item -ItemType Directory -Force -Path $PluginsRoot | Out-Null

if ($Junction) {
  if (Test-Path $TargetDir) { Remove-Item -Recurse -Force $TargetDir }
  Write-Host "==> Creating directory junction (no admin required): $TargetDir -> $ScriptDir" -ForegroundColor Cyan
  cmd /c mklink /J "`"$TargetDir`"" "`"$ScriptDir`""
} elseif (Test-Path (Join-Path $ScriptDir "plugin.json")) {
  if (Test-Path $TargetDir) { Remove-Item -Recurse -Force $TargetDir }
  Write-Host "==> Copying local repo into $TargetDir" -ForegroundColor Cyan
  Copy-Item -Recurse -Force $ScriptDir $TargetDir
} else {
  if (Test-Path (Join-Path $TargetDir ".git")) {
    Write-Host "==> Pulling latest Startup Antigravity..." -ForegroundColor Cyan
    git -C $TargetDir pull --ff-only
  } else {
    Write-Host "==> Cloning Startup Antigravity into $TargetDir" -ForegroundColor Cyan
    git clone $RepoUrl $TargetDir
  }
}

Write-Host "==> Running built-in self-test suite..." -ForegroundColor Cyan
Push-Location $TargetDir
try {
  & $pyCmd -m unittest discover -s tests -v
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "SUCCESS! Startup Antigravity is installed at: $TargetDir" -ForegroundColor Green
Write-Host "Next step: Open Antigravity -> Additional Options (...) > MCP Servers > Refresh, then open a new folder!" -ForegroundColor Cyan
