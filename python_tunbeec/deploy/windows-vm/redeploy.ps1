<#
.SYNOPSIS
  Pull the latest code and restart the TUNBEEC API service on the Windows VM.
  Run as Administrator after bootstrap.ps1 has already set things up once.

.USAGE
  .\redeploy.ps1 [-InstallDir "C:\tunbeec"]
#>

param(
    [string]$InstallDir = "C:\tunbeec"
)

$ErrorActionPreference = "Stop"

nssm stop TunbeecApi

Push-Location $InstallDir
git pull
Pop-Location

$apiDir = Join-Path $InstallDir "python_tunbeec"
Push-Location $apiDir
& ".\venv\Scripts\pip.exe" install -r "api\requirements.txt"
Pop-Location

nssm start TunbeecApi
Write-Host "Redeployed and restarted TunbeecApi."
