"""FastAPI backend for the TUNBEEC web client.

Thin HTTP layer over the existing tunbeec/calc, tunbeec/data, tunbeec/app_state, tunbeec/models
modules -- none of that code is modified, this only adds request/response plumbing so the
Next.js client (client/) can drive the same compliance pipeline the PySide6 desktop app
(tunbeec/ui/main_window.py) does.

Run locally: `uvicorn api.main:app --reload --port 8000` from the python_tunbeec/ directory.
"""
from __future__ import annotations

import logging
import os
import sys
import tempfile

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.deps import get_reference
from api.routers import building, compliance, projects, reference
from tunbeec.app_paths import DOE22_DIR, IMAGE_DIR, PROJECT_DIR

# API docs are only served when ENABLE_DOCS=1 (local dev), not in production.
_docs = os.environ.get("ENABLE_DOCS") == "1"
app = FastAPI(
    title="TUNBEEC API",
    docs_url="/docs" if _docs else None,
    redoc_url=None,
    openapi_url="/openapi.json" if _docs else None,
)
log = logging.getLogger("tunbeec.api")

_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins.split(",") if o.strip()],
    allow_credentials=False,  # no cookies or logins, so never send credentials cross-site
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    # Full details go to the server log only, never to the browser.
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on the server. Please try again."})

if IMAGE_DIR.exists():
    app.mount("/static/images", StaticFiles(directory=str(IMAGE_DIR)), name="images")

app.include_router(reference.router)
app.include_router(building.router)
app.include_router(compliance.router)
app.include_router(projects.router)


def _project_dir_writable() -> bool:
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=PROJECT_DIR):
        return True


@app.get("/api/health")
def health(response: Response) -> dict:
    """Checks the reference library, scratch space and, on Windows, the DOE-2.2 engine.

    Returns 503 when any check fails so uptime monitors raise an alert.
    """
    checks: dict[str, str] = {}

    try:
        checks["reference_library"] = "ok" if get_reference().bldg_locations else "fail"
    except Exception:
        log.exception("Health check: reference library failed to load")
        checks["reference_library"] = "fail"

    try:
        checks["project_storage"] = "ok" if _project_dir_writable() else "fail"
    except Exception:
        log.exception("Health check: project directory is not writable")
        checks["project_storage"] = "fail"

    # RUN22.exe only runs on Windows, so the simulation engine is only checked there.
    if sys.platform == "win32":
        checks["simulation_engine"] = "ok" if (DOE22_DIR / "RUN22.exe").is_file() else "fail"

    healthy = all(v == "ok" for v in checks.values())
    if not healthy:
        response.status_code = 503
    return {"status": "ok" if healthy else "degraded", "checks": checks}
