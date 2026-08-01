"""Prescriptive-path results screen -- styled after lib1/ReportPrescriptive{1,2,3}.jrxml
(ANME logo, blue section banners, color-coded per-element and overall verdicts).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView, QDialogButtonBox, QDialog, QGridLayout, QHeaderView, QLabel,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from tunbeec.calc.prescriptive import PrescriptiveResult
from tunbeec.ui.report_style import (
    BANNER_BLUE, COMPLIANT_GREEN, NON_COMPLIANT_RED, banner, title_header, verdict_banner,
)


def _info_cell(text: str, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 11pt;" + (" font-weight: bold;" if bold else ""))
    return lbl


class PrescriptiveResultDialog(QDialog):
    def __init__(self, result: PrescriptiveResult, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Result - Prescriptive Approach")
        self.resize(780, 620)
        v = QVBoxLayout(self)
        v.setSpacing(10)

        v.addWidget(title_header("Prescriptive Compliance Report"))

        v.addWidget(banner("Building Glazing"))
        info = QWidget()
        g = QGridLayout(info)
        g.addWidget(_info_cell("Climate Zone:", bold=True), 0, 0)
        g.addWidget(_info_cell(result.bldg_zone), 0, 1)
        g.addWidget(_info_cell("Glazing Level:", bold=True), 0, 2)
        g.addWidget(_info_cell(result.grade), 0, 3)
        g.addWidget(_info_cell("X1 (glazing / total wall):", bold=True), 1, 0)
        g.addWidget(_info_cell(f"{result.x1:.1f} %"), 1, 1)
        g.addWidget(_info_cell("X2 (glazing / east+west wall):", bold=True), 1, 2)
        g.addWidget(_info_cell(f"{result.x2:.1f} %"), 1, 3)
        v.addWidget(info)

        if result.needs_performance_path:
            v.addWidget(banner("Envelope Requirements"))
            msg = QLabel(
                "The glazing ratio exceeds the range covered by the prescriptive approach.\n"
                "Use the Performance Approach for this building."
            )
            msg.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {NON_COMPLIANT_RED}; padding: 12px;")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(msg)
            v.addStretch(1)
        else:
            v.addWidget(banner("Envelope Requirements"))
            table = QTableWidget(len(result.rows), 4)
            table.setHorizontalHeaderLabels(["Element", "Building Value", "Limit Value", "Result"])
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            table.setAlternatingRowColors(True)
            table.setStyleSheet(
                "QTableWidget { font-size: 11pt; alternate-background-color: #eef1fb; }"
                f"QHeaderView::section {{ background: {BANNER_BLUE}; color: white;"
                " font-weight: bold; font-size: 11pt; padding: 6px; border: none; }"
            )
            bold = QFont()
            bold.setBold(True)
            for i, row in enumerate(result.rows):
                cells = [
                    QTableWidgetItem(f"{row.item} {row.unit}"),
                    QTableWidgetItem(f"{row.bldg_value:.3f}"),
                    QTableWidgetItem(f"{row.comp_value_1:.3f}"),
                    QTableWidgetItem("Compliant" if row.compliant else "Non-Compliant"),
                ]
                cells[1].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                cells[2].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                cells[3].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                cells[3].setFont(bold)
                cells[3].setForeground(QBrush(QColor(
                    COMPLIANT_GREEN if row.compliant else NON_COMPLIANT_RED)))
                for col, cell in enumerate(cells):
                    table.setItem(i, col, cell)
                table.setRowHeight(i, 36)
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            v.addWidget(table, 1)

            v.addWidget(verdict_banner(
                result.compliant,
                "Overall Result: " + ("Compliant" if result.compliant else "Non-Compliant"),
            ))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        v.addWidget(buttons)
