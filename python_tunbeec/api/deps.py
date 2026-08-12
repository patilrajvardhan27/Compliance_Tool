"""Process-wide singletons shared across requests: the reference library DB (read-only, loaded
once, same lifetime as ReferenceData in the desktop app's MainWindow.__init__) and the resolved
paths it and the DOE-2.2 engine need.
"""
from __future__ import annotations

from functools import lru_cache

from tunbeec.app_paths import DEFAULT_DB_PATH
from tunbeec.data.reference import ReferenceData


@lru_cache(maxsize=1)
def get_reference() -> ReferenceData:
    return ReferenceData(DEFAULT_DB_PATH)
