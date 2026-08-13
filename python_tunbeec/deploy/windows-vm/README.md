# Deploying the TUNBEEC backend on a Windows VM (so DOE-2.2 actually runs)

## Why this exists

The FastAPI backend (`python_tunbeec/api/`) currently runs on `tunbeec-api.azurewebsites.net`, a
**Linux** App Service. `resources/doe22/RUN22.exe` is a Windows-only binary — it cannot execute on
Linux at all, which is the "cannot be run on this platform" message you see in the Windows tab.
This is **not** a hidden-GUI-window problem: the code already calls RUN22.exe with
`creationflags=subprocess.CREATE_NO_WINDOW` (see `tunbeec/calc/performance.py`), and that exact
code path already runs headlessly and successfully in this repo's `test-performance-doe22.yml` CI
workflow on GitHub's `windows-latest` runners. The fix is purely where the backend runs, not the
code — the backend has to move to Windows compute.

This folder sets that up on a plain Windows Server VM (no code changes needed):

- `bootstrap.ps1` — one-time setup: installs Python + the VC++ x86 redist RUN22.exe needs, clones
  the repo, and registers two Windows services (via NSSM) that auto-start on boot and restart on
  crash: `TunbeecApi` (uvicorn, bound to localhost:8000) and `TunbeecCaddy` (Caddy reverse-proxying
  HTTPS on 443 -> localhost:8000, with an automatic free Let's Encrypt cert).
- `redeploy.ps1` — pulls latest code + restarts the API service for future updates.

The frontend (`tunbeec-frontend.azurewebsites.net`) does **not** need to move — it doesn't touch
RUN22.exe, only the API does.

## 1. Create the VM

**Already done** — `tunbeec-api-vm` exists in `tunbeec-rc`/`westus3` (same resource group as
`tunbeec-api`/`tunbeec-frontend`), size `Standard_B2s_v2` (`Standard_B2s` had no capacity in this
region at creation time), public DNS `tunbeec-api-vm.westus3.cloudapp.azure.com`, admin user
`tunbeecadmin`. Ports 3389 (RDP, added automatically), 80, and 443 are open on its NSG. If you ever
need to recreate it:

```bash
RG=tunbeec-rc                    # same resource group as tunbeec-api / tunbeec-frontend
LOCATION=westus3                 # same region as the existing App Services
VM=tunbeec-api-vm
DNS_LABEL=tunbeec-api-vm         # -> tunbeec-api-vm.westus3.cloudapp.azure.com

az vm create \
  --resource-group $RG \
  --name $VM \
  --image Win2022Datacenter \
  --size Standard_B2s_v2 \
  --admin-username tunbeecadmin \
  --admin-password '<pick-a-strong-password>' \
  --public-ip-address-dns-name $DNS_LABEL

az vm open-port --resource-group $RG --name $VM --port 80 --priority 900
az vm open-port --resource-group $RG --name $VM --port 443 --priority 901
```

`Standard_B2s_v2` (2 vCPU/4GB, burstable) is plenty for one console-app simulation at a time;
resize later with `az vm resize` if needed. `Win2022Datacenter` ships winget-less but this
bootstrap script uses Chocolatey instead, so that's fine.

## 2. RDP in and bootstrap

VM public IP: `20.163.104.163` (also reachable as `tunbeec-api-vm.westus3.cloudapp.azure.com`).

RDP to it (Microsoft Remote Desktop on Mac, or `mstsc` on Windows) as `tunbeecadmin` — get the
password from whoever ran `az vm create` (it isn't stored in this repo). In an **elevated**
PowerShell prompt on the VM:

```powershell
git clone https://github.com/patilrajvardhan27/Compliance_Tool.git C:\src
cd C:\src\python_tunbeec\deploy\windows-vm

.\bootstrap.ps1 `
  -RepoUrl "https://github.com/patilrajvardhan27/Compliance_Tool.git" `
  -PublicHostname "tunbeec-api-vm.westus3.cloudapp.azure.com" `
  -AllowedOrigin "https://tunbeec-frontend.azurewebsites.net"
```

(The repo is public, so no git credentials are needed. `bootstrap.ps1` clones its own working copy
to `C:\tunbeec` — the `C:\src` clone above is just to get the script onto the VM; you can delete
`C:\src` afterward.)

Wait a minute for Caddy to obtain its Let's Encrypt cert, then confirm:

```bash
curl https://tunbeec-api-vm.westus3.cloudapp.azure.com/api/health
# {"status":"ok"}
```

## 3. Point the frontend at it

Update `client/.env.production`:

```
NEXT_PUBLIC_API_BASE=https://tunbeec-api-vm.westus3.cloudapp.azure.com
```

Rebuild and redeploy the Next.js app the same way you deployed `tunbeec-frontend` before (the
`output: "standalone"` prebuilt-bundle deploy noted in `client/next.config.ts`).

## 4. Future code updates

RDP in and run, in an elevated PowerShell prompt from this folder:

```powershell
.\redeploy.ps1
```

## 5. Sanity checks after any change

- `https://<hostname>/api/health` returns `{"status":"ok"}`.
- Windows tab of the app: run a Performance Check end-to-end and confirm a `.sim` file and a real
  BecTh value come back (not just "BDL generated, simulation unavailable").
- Browser devtools console on the frontend: no CORS errors, no mixed-content warnings (frontend is
  https, backend must be https too — that's what Caddy is for).
