""""-Create-" glass-type dialog -- port of gui.GuiGlass."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLineEdit, QMessageBox, QVBoxLayout

from tunbeec.models import GlassEntry


class GlassDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Glass Type")
        self.result_entry: GlassEntry | None = None

        v = QVBoxLayout(self)
        f = QFormLayout()
        self.txt_name = QLineEdit()
        self.spn_conduct = QDoubleSpinBox(); self.spn_conduct.setDecimals(4); self.spn_conduct.setMaximum(20)
        self.spn_sc = QDoubleSpinBox(); self.spn_sc.setDecimals(3); self.spn_sc.setMaximum(1.0)
        self.spn_vt = QDoubleSpinBox(); self.spn_vt.setDecimals(3); self.spn_vt.setMaximum(1.0)
        f.addRow("Name:", self.txt_name)
        f.addRow("Conductance (W/m2.K):", self.spn_conduct)
        f.addRow("Shading Coefficient (SC):", self.spn_sc)
        f.addRow("Visible Transmittance (VT):", self.spn_vt)
        v.addLayout(f)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        v.addWidget(buttons)

    def _on_save(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a name.")
            return
        self.result_entry = GlassEntry(
            user_name=name, user_type="GLASS_TYPE", type="SHADING-COEF",
            glass_conduct=self.spn_conduct.value(), sc=self.spn_sc.value(), vt=self.spn_vt.value(),
        )
        self.accept()
