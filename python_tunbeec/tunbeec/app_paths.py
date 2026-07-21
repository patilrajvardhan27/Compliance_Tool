"""Resolves the resources/ directory shipped alongside main.py (mirrors util.Dir.java)."""
from __future__ import annotations

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent  # python_tunbeec/
RESOURCES_DIR = APP_ROOT / "resources"
DEFAULT_DB_PATH = RESOURCES_DIR / "lib1" / "DefaultDB.tct"
IMAGE_DIR = RESOURCES_DIR / "image"
DOE22_DIR = RESOURCES_DIR / "doe22"
PROJECT_DIR = APP_ROOT / "PROJECT"
LOG_FILE = APP_ROOT / "applog.txt"
