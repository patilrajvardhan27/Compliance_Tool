<#
.SYNOPSIS
  One-time setup for the TUNBEEC FastAPI backend + DOE-2.2 (RUN22.exe) on a fresh Windows Server
  Azure VM. Installs Python, the VC++ x86 redist RUN22.exe needs, clones the repo, and registers
  two always-on Windows services: uvicorn (the API) and Caddy (TLS termination + reverse proxy).

.USAGE
  Run as Administrator in an elevated PowerShell prompt on the VM (e.g. via RDP):
    .\bootstrap.ps1 -RepoUrl "https://github.com/<you>/Compliance_Tool.git" -PublicHostname "tunbeec-api.<region>.cloudapp.azure.com" -AllowedOrigin "https://tunbeec-frontend.azurewebsites.net"

.NOTES
  - RUN22.exe is a 1990s/2000s 32-bit console binary (see python_tunbeec/INSTALL.md §5). It needs
    no interactive desktop/GUI session -- it's launched with CREATE_NO_WINDOW today and already
    runs headless in this project's GitHub Actions CI on windows-latest runners. Running it from a
    Windows service on this VM works the same way.
  - PublicHostname must be a real DNS name reachable on port 80 (Caddy uses the ACME HTTP-01
    challenge to get a free Let's Encrypt cert automatically). Azure's free
    "<label>.<region>.cloudapp.azure.com" DNS name on the VM's public IP works fine for this.
#>

param(
    [Parameter(Mandatory = $true)] [string]$RepoUrl,
    [Parameter(Mandatory = $true)] [string]$PublicHostname,
    [Parameter(Mandatory = $true)] [string]$AllowedOrigin,
    [string]$InstallDir = "C:\tunbeec"
)

$ErrorActionPreference = "Stop"

Write-Host "== Installing Chocolatey =="
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

Write-Host "== Installing Python, Git, VC++ x86 redist, NSSM, Caddy =="
choco install -y python312 git vcredist140 nssm caddy
# Refresh PATH in this session so python/git/nssm/caddy are found without a new shell.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "== Cloning repo to $InstallDir =="
if (-not (Test-Path $InstallDir)) {
    git clone $RepoUrl $InstallDir
} else {
    Write-Host "$InstallDir already exists, skipping clone (use redeploy.ps1 to update)."
}

$apiDir = Join-Path $InstallDir "python_tunbeec"
Push-Location $apiDir

Write-Host "== Creating venv + installing API dependencies =="
python -m venv venv
& ".\venv\Scripts\pip.exe" install --upgrade pip
& ".\venv\Scripts\pip.exe" install -r "api\requirements.txt"

Pop-Location

Write-Host "== Registering uvicorn as a Windows service (NSSM) =="
$venvPython = Join-Path $apiDir "venv\Scripts\python.exe"
nssm install TunbeecApi $venvPython "-m uvicorn api.main:app --host 127.0.0.1 --port 8000"
nssm set TunbeecApi AppDirectory $apiDir
nssm set TunbeecApi AppEnvironmentExtra "ALLOWED_ORIGINS=$AllowedOrigin"
nssm set TunbeecApi Start SERVICE_AUTO_START
nssm set TunbeecApi AppStdout (Join-Path $apiDir "api-service.log")
nssm set TunbeecApi AppStderr (Join-Path $apiDir "api-service.log")
nssm set TunbeecApi AppRotateFiles 1

Write-Host "== Writing Caddyfile ($PublicHostname -> 127.0.0.1:8000) =="
$caddyDir = "C:\caddy"
New-Item -ItemType Directory -Force -Path $caddyDir | Out-Null
@"
$PublicHostname {
    reverse_proxy 127.0.0.1:8000
}
"@ | Set-Content -Path (Join-Path $caddyDir "Caddyfile") -Encoding UTF8

$caddyExe = (Get-Command caddy).Source
nssm install TunbeecCaddy $caddyExe "run --config C:\caddy\Caddyfile"
nssm set TunbeecCaddy AppDirectory $caddyDir
nssm set TunbeecCaddy Start SERVICE_AUTO_START

Write-Host "== Opening firewall ports 80/443 (Caddy) =="
New-NetFirewallRule -DisplayName "Caddy HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Caddy HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow -ErrorAction SilentlyContinue

Write-Host "== Starting services =="
nssm start TunbeecApi
nssm start TunbeecCaddy

Write-Host ""
Write-Host "Done. Once DNS/cert propagate, check:"
Write-Host "  https://$PublicHostname/api/health"
Write-Host ""
Write-Host "Point the frontend at this backend by setting, in client/.env.production:"
Write-Host "  NEXT_PUBLIC_API_BASE=https://$PublicHostname"
Write-Host "then rebuilding/redeploying the Next.js app."
