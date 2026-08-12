"""FastAPI backend for the TUNBEEC web client.

Thin HTTP layer over the existing tunbeec/calc, tunbeec/data, tunbeec/app_state, tunbeec/models
modules -- none of that code is modified, this only adds request/response plumbing so the
Next.js client (client/) can drive the same compliance pipeline the PySide6 desktop app
(tunbeec/ui/main_window.py) does.

Run locally: `uvicorn api.main:app --reload --port 8000` from the python_tunbeec/ directory.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import building, compliance, projects, reference
from tunbeec.app_paths import IMAGE_DIR

app = FastAPI(title="TUNBEEC API")

_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if IMAGE_DIR.exists():
    app.mount("/static/images", StaticFiles(directory=str(IMAGE_DIR)), name="images")

app.include_router(reference.router)
app.include_router(building.router)
app.include_router(compliance.router)
app.include_router(projects.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
