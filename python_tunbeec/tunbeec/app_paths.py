"""Resolves the resources/ directory shipped alongside main.py (mirrors util.Dir.java).

When frozen into a PyInstaller exe, `__file__` lives inside the bundled `_internal`
(onedir) or a per-launch temp extraction (onefile) directory, neither of which is a
sensible place to keep user data. So in that case, writable paths (PROJECT_DIR,
LOG_FILE) are anchored to the folder containing the actual .exe -- persistent across
runs -- while read-only bundled resources are still read from the PyInstaller bundle
(sys._MEIPASS, which equals the exe's folder in onedir mode).
"""
from __future__ import annotations

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    APP_ROOT = Path(sys.executable).resolve().parent
    RESOURCES_DIR = Path(getattr(sys, "_MEIPASS", APP_ROOT)) / "resources"
else:
    APP_ROOT = Path(__file__).resolve().parent.parent  # python_tunbeec/
    RESOURCES_DIR = APP_ROOT / "resources"

DEFAULT_DB_PATH = RESOURCES_DIR / "lib1" / "DefaultDB.tct"
IMAGE_DIR = RESOURCES_DIR / "image"
DOE22_DIR = RESOURCES_DIR / "doe22"
PROJECT_DIR = APP_ROOT / "PROJECT"
LOG_FILE = APP_ROOT / "applog.txt"
