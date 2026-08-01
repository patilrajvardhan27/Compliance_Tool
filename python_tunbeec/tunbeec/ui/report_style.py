"""Shared look-and-feel helpers for the result/report dialogs.

Reproduces the visual language of the original Java app's Jasper reports
(lib1/ReportPerformance.jrxml, ReportPrescriptive{1,2,3}.jrxml -- see image.png):
ANME logo top-left, saturated blue banner bars with bold white centered titles,
bold field labels, and red/green verdict text.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from tunbeec.app_paths import IMAGE_DIR

BANNER_BLUE = "#2929d4"
COMPLIANT_GREEN = "#1d8a2c"
NON_COMPLIANT_RED = "#d02020"

_LOGO_FILE = "LogoANME.jpg"


def banner(text: str, point_size: int = 12) -> QLabel:
    """Full-width blue section banner with bold white centered text."""
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"background: {BANNER_BLUE}; color: white; font-weight: bold;"
        f" font-size: {point_size}pt; padding: 6px; border-radius: 2px;"
    )
    return lbl


def title_header(title: str) -> QWidget:
    """Report masthead: ANME logo on the left, blue title banner filling the rest."""
    row = QWidget()
    h = QHBoxLayout(row)
    h.setContentsMargins(0, 0, 0, 0)
    logo_path = IMAGE_DIR / _LOGO_FILE
    logo = QPixmap(str(logo_path)) if logo_path.exists() else QPixmap()
    if not logo.isNull():
        lbl_logo = QLabel()
        lbl_logo.setPixmap(logo.scaledToHeight(48, Qt.TransformationMode.SmoothTransformation))
        h.addWidget(lbl_logo)
    h.addWidget(banner(title, point_size=14), 1)
    return row


def verdict_banner(compliant: bool, text: str) -> QLabel:
    """Green/red full-width verdict bar."""
    color = COMPLIANT_GREEN if compliant else NON_COMPLIANT_RED
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"background: {color}; color: white; font-weight: bold; font-size: 12pt; padding: 8px;"
    )
    return lbl
