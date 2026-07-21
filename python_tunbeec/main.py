#!/usr/bin/env python3
"""TUNBEEC Desktop -- Python port entry point.

See ../Tunbeec Desktop Install Guide.txt for setup instructions (venv, requirements.txt).
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tunbeec.app_paths import LOG_FILE  # noqa: E402


def _setup_logging():
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


if __name__ == "__main__":
    _setup_logging()
    from tunbeec.ui.main_window import main
    main()
