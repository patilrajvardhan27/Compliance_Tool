"""Prescriptive-path results screen -- mirrors lib1/ReportPrescriptive{1,2,3}.jrxml at a
functional (not pixel-identical) level: envelope U-values/SC vs. code thresholds, per bracket,
plus the overall Compliant/Non-Compliant verdict.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialogButtonBox, QDialog, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from tunbeec.calc.prescriptive import PrescriptiveResult


class PrescriptiveResultDialog(QDialog):
    def __init__(self, result: PrescriptiveResult, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Result - Prescriptive Approach")
        self.resize(560, 360)
        v = QVBoxLayout(self)

        v.addWidget(QLabel(f"Climate zone: {result.bldg_zone}    Glazing level: {result.grade}"))
        v.addWidget(QLabel(f"X1 (glazing/total wall): {result.x1:.1f}%    X2 (glazing/east+west wall): {result.x2:.1f}%"))

        if result.needs_performance_path:
            v.addWidget(QLabel(
                "The glazing ratio exceeds the range covered by the prescriptive approach.\n"
                "Use the Performance Approach for this building."
            ))
        else:
            table = QTableWidget(len(result.rows), 4)
            table.setHorizontalHeaderLabels(["Element", "Building Value", "Limit Value", "Result"])
            for i, row in enumerate(result.rows):
                table.setItem(i, 0, QTableWidgetItem(f"{row.item} {row.unit}"))
                table.setItem(i, 1, QTableWidgetItem(f"{row.bldg_value:.3f}"))
                table.setItem(i, 2, QTableWidgetItem(f"{row.comp_value_1:.3f}"))
                table.setItem(i, 3, QTableWidgetItem("Compliant" if row.compliant else "Non-Compliant"))
            table.horizontalHeader().setStretchLastSection(True)
            v.addWidget(table)

            verdict = QLabel("Overall Result: " + ("Compliant" if result.compliant else "Non-Compliant"))
            verdict.setStyleSheet(
                "font-weight: bold; color: " + ("green" if result.compliant else "red") + ";"
            )
            v.addWidget(verdict)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        v.addWidget(buttons)
