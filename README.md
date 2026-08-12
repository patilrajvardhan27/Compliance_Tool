# TUNBEEC

Tunisian building energy code compliance tool (ANME). This repo has two front doors onto the
same compliance engine (`python_tunbeec/tunbeec/`):

| Path | What it is |
|---|---|
| `python_tunbeec/` | Core engine (`tunbeec/calc`, `tunbeec/data`, `tunbeec/app_state`) + the original PySide6 desktop GUI (`main.py`, `tunbeec/ui/`). |
| `python_tunbeec/api/` | FastAPI backend — thin HTTP layer over the same engine, unmodified. |
| `client/` | Next.js + TypeScript web frontend that talks to `python_tunbeec/api/`. Full feature parity with the desktop app. |
| `windows_exe/` | PyInstaller + Inno Setup packaging for a standalone `TUNBEEC-Setup.exe` desktop installer. **Not used by the web deployment below** — that's a separate distribution path for people who want the offline desktop app. |

## Local development

Backend:
```bash
cd python_tunbeec
source venv/bin/activate   # venv already has fastapi/uvicorn installed
uvicorn api.main:app --reload --port 8000
```

Frontend (needs `client/.env.local` with `NEXT_PUBLIC_API_BASE=http://localhost:8000`):
```bash
cd client
npm run dev
```

## Deploying the web app to Azure (no exe file, no VM)

Both `client/` and `python_tunbeec/api/` deploy as plain **Azure App Service (Linux)** web apps
sharing one App Service Plan — fully managed, deploy by pushing code, nothing to RDP/SSH into.

- **Frontend** (`client/`) → App Service, Linux, Node 20 — `next build && next start`.
- **Backend** (`python_tunbeec/api/`) → App Service, Linux, Python 3.11 — `uvicorn`.

**Trade-off**: the "Approche Performencielle" step shells out to `resources/doe22/RUN22.exe`, a
Windows-only 32-bit binary (see `python_tunbeec/INSTALL.md` §5) — it cannot run on Linux, and
Wine/emulation don't work either. On this Linux backend, that step still generates the `.inp` BDL
file, but the API returns `status: "simulation_unavailable"` instead of an auto-run result — the
exact same graceful fallback the desktop app already shows on Mac/Linux today
(`python_tunbeec/tunbeec/calc/performance.py`, `sys.platform != "win32"` check). The
**Prescriptive** compliance path is unaffected and works fully. See "Optional: add a Windows VM
later" at the bottom if live DOE-2.2 simulation in the cloud becomes a requirement — it's an
additive step, not a redo of anything here.

> **Already have `tunbeec-rc` / `tunbeec-api` / `tunbeec-frontend` running?** Skip straight to
> [Redeploying after code changes](#redeploying-after-code-changes) — it's just the two
> `az webapp deploy` commands below, no resource-creation steps to repeat.

Everything below uses the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
(`az login` first). Replace the example names with your own if they're taken — App Service names
are globally unique across all of Azure, not just your subscription.

> **Copy-paste tip**: every command is written as a single line on purpose — some terminals mangle
> multi-line `\`-continued commands on paste. Run one line at a time.

> **Region note for CU Boulder's `azucob0ceaelbslw` / `OIT_Public_Cloud_Broker_Managed` subscription**:
> this subscription enforces a per-region quota allow-list. `eastus`, `eastus2`, and `centralus` all
> reject App Service (Linux) compute with `Current Limit (Total VMs): 0`. **`westus3` is confirmed
> working** — there's an existing, running Linux App Service Plan on this same subscription in that
> region (Azure Portal → App Services → `saber-plan`). All commands below already use `westus3`. If
> a fresh subscription/tenant hits the same `Total VMs: 0` error somewhere else, check
> **Portal → Subscriptions → Usage + quotas** (filter: App Service) for the exact allowed region(s)
> before retrying, rather than guessing regions one at a time.

### 0. Resource group + shared App Service Plan

One Linux plan hosts both apps (isolated processes, shared compute), so this is a single line
item on the bill instead of two:
```bash
az group create --name tunbeec-rc --location westus3
```
```bash
az appservice plan create --name tunbeec-plan --resource-group tunbeec-rc --sku B1 --is-linux --location westus3
```

### 1. Backend — `python_tunbeec/api/` on Python 3.11

```bash
az webapp create --resource-group tunbeec-rc --plan tunbeec-plan --name tunbeec-api --runtime "PYTHON:3.11"
```
```bash
az webapp config set --resource-group tunbeec-rc --name tunbeec-api --startup-file "uvicorn api.main:app --host 0.0.0.0 --port 8000"
```

`ALLOWED_ORIGINS` (read by `api/main.py`'s CORS middleware) must match the frontend's URL from
step 2 exactly:
```bash
az webapp config appsettings set --resource-group tunbeec-rc --name tunbeec-api --settings ALLOWED_ORIGINS=https://tunbeec-frontend.azurewebsites.net SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

Deploy. This stages `python_tunbeec/` into a temp folder and swaps in `api/requirements.txt` as
the root `requirements.txt` — Azure's build step (Oryx) only looks at the one at the deployment
root, and the real root one (`python_tunbeec/requirements.txt`) is PySide6 for the desktop GUI,
which this deployment doesn't need or want:
```bash
rm -rf /tmp/tunbeec-api-deploy && mkdir -p /tmp/tunbeec-api-deploy
```
```bash
rsync -a --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude 'applog.txt' "python_tunbeec/" /tmp/tunbeec-api-deploy/
```
```bash
cp python_tunbeec/api/requirements.txt /tmp/tunbeec-api-deploy/requirements.txt
```
```bash
cd /tmp/tunbeec-api-deploy && zip -r /tmp/tunbeec-api.zip . -x ".*" && cd -
```
```bash
az webapp deploy --resource-group tunbeec-rc --name tunbeec-api --src-path /tmp/tunbeec-api.zip --type zip
```

Verify:
```bash
curl https://tunbeec-api.azurewebsites.net/api/health
# {"status":"ok"}
```

### 2. Frontend — `client/` on Node 20

```bash
az webapp create --resource-group tunbeec-rc --plan tunbeec-plan --name tunbeec-frontend --runtime "NODE:20-lts"
```
```bash
az webapp config set --resource-group tunbeec-rc --name tunbeec-frontend --startup-file "npm run start"
```

`NEXT_PUBLIC_API_BASE` gets baked into the JS bundle **at build time**, so set it before the first
build runs — Oryx picks up App Settings as build-time env vars:
```bash
az webapp config appsettings set --resource-group tunbeec-rc --name tunbeec-frontend --settings NEXT_PUBLIC_API_BASE=https://tunbeec-api.azurewebsites.net SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

Deploy the source (zip-deploy triggers the Oryx build server-side, so `node_modules`/`.next`
don't need to be in the zip):
```bash
cd client && zip -r ../client.zip . -x "node_modules/*" ".next/*" && cd ..
```
```bash
az webapp deploy --resource-group tunbeec-rc --name tunbeec-frontend --src-path client.zip --type zip
```

Your app is live at `https://tunbeec-frontend.azurewebsites.net`.

### Redeploying after code changes

Once `tunbeec-rc` / `tunbeec-plan` / `tunbeec-api` / `tunbeec-frontend` already exist, pushing an
update to either side is just re-running its zip-and-deploy commands — nothing from step 0 needs
repeating, and `az webapp create`/`config set`/`appsettings set` only need to be re-run if you're
changing the runtime, startup command, or an env var (e.g. `ALLOWED_ORIGINS` after a custom domain).

**Backend changed** (anything under `python_tunbeec/`):
```bash
rm -rf /tmp/tunbeec-api-deploy && mkdir -p /tmp/tunbeec-api-deploy
```
```bash
rsync -a --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude 'applog.txt' --exclude 'PROJECT' "python_tunbeec/" /tmp/tunbeec-api-deploy/
```
```bash
cp python_tunbeec/api/requirements.txt /tmp/tunbeec-api-deploy/requirements.txt
```
```bash
cd /tmp/tunbeec-api-deploy && zip -r /tmp/tunbeec-api.zip . -x ".*" && cd -
```
```bash
az webapp deploy --resource-group tunbeec-rc --name tunbeec-api --src-path /tmp/tunbeec-api.zip --type zip
```
```bash
curl https://tunbeec-api.azurewebsites.net/api/health   # {"status":"ok"} once the restart finishes
```

**Frontend changed** (anything under `client/`):
```bash
cd client && rm -f ../client.zip && zip -r ../client.zip . -x "node_modules/*" ".next/*" && cd ..
```
```bash
az webapp deploy --resource-group tunbeec-rc --name tunbeec-frontend --src-path client.zip --type zip
```

Both deploys trigger an Oryx build server-side and take 1-3 minutes; watch progress with
`az webapp log tail --resource-group tunbeec-rc --name <tunbeec-api|tunbeec-frontend>` if a deploy
seems stuck or the app 500s after redeploying. If a change touched **both** sides in a way that
changes the wire contract between them (new/renamed API route, new required field), deploy the
backend first, then the frontend — the frontend calls a fixed `NEXT_PUBLIC_API_BASE` and does no
version negotiation.

### 3. Notes

- **Cost**: one `B1` Linux App Service Plan hosting both apps is ~$13/mo total — no per-app
  compute cost since they share the plan.
- **Custom domain**: `az webapp config hostname add` on either app, then re-run its
  `ALLOWED_ORIGINS`/`NEXT_PUBLIC_API_BASE` app-settings step with the new hostname (these are
  build/runtime-time values, not auto-updated).
- **Project files live on the user's own computer, not the server.** Open/Save/Save As use the
  browser's File System Access API (native OS file dialogs in Chromium; a download + `<input
  type="file">` picker fallback elsewhere) — the `.tct` never touches App Service disk. The backend
  only exposes two stateless conversion endpoints, `POST /api/projects/serialize` (JSON → `.tct`
  bytes) and `POST /api/projects/parse` (`.tct` bytes → JSON); nothing is written to
  `PROJECT_DIR` except DOE-2.2's own scratch `.inp`/`.sim` files during a Performance run, which
  a zip redeploy is fine to wipe. There is no Azure Files / persistent-storage step to worry about.

### Optional: add a Windows VM later for live DOE-2.2 simulation

If the Prescriptive-only limitation above becomes a blocker, the Performance/DOE-2.2 path can be
added by standing up one more resource — an Azure VM running Windows Server, with
`python_tunbeec/api` running there instead of (or as a second backend alongside) the Linux one,
fronted by a reverse proxy for HTTPS. This is additive (new VM + `nssm`-registered service + Caddy
for TLS), not a redo of the Linux setup above. Ask when you're ready to add it — worth noting for
when that happens: on this subscription the `Standard_B*` burstable VM family isn't offered in any
region tried, but `Standard_D2as_v7` in `eastus2` is confirmed to provision successfully, and
Windows VM computer names must be ≤15 characters (set via `--computer-name`, separate from the
Azure resource `--name`).
