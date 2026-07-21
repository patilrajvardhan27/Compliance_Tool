""""-Create-" material dialog -- port of gui.GuiMaterial."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLineEdit, QMessageBox, QStackedWidget,
    QVBoxLayout, QWidget,
)

from tunbeec.calc.uvalue import calc_resistance
from tunbeec.models import MaterialEntry


class MaterialDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Material")
        self.result_entry: MaterialEntry | None = None

        v = QVBoxLayout(self)
        top = QFormLayout()
        self.txt_name = QLineEdit()
        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["Properties", "Resistance"])
        top.addRow("Name:", self.txt_name)
        top.addRow("Type:", self.cmb_type)
        v.addLayout(top)

        self.stack = QStackedWidget()
        props_page = QWidget()
        pf = QFormLayout(props_page)
        self.spn_thickness = QDoubleSpinBox(); self.spn_thickness.setDecimals(4); self.spn_thickness.setMaximum(10)
        self.spn_conductivity = QDoubleSpinBox(); self.spn_conductivity.setDecimals(4); self.spn_conductivity.setMaximum(1000)
        self.spn_density = QDoubleSpinBox(); self.spn_density.setDecimals(2); self.spn_density.setMaximum(10000)
        self.spn_spec_heat = QDoubleSpinBox(); self.spn_spec_heat.setDecimals(2); self.spn_spec_heat.setMaximum(10000)
        pf.addRow("Thickness (m):", self.spn_thickness)
        pf.addRow("Conductivity (W/m.K):", self.spn_conductivity)
        pf.addRow("Density (kg/m3):", self.spn_density)
        pf.addRow("Specific Heat (J/kg.K):", self.spn_spec_heat)

        resist_page = QWidget()
        rf = QFormLayout(resist_page)
        self.spn_rvalue = QDoubleSpinBox(); self.spn_rvalue.setDecimals(4); self.spn_rvalue.setMaximum(1000)
        rf.addRow("R Value (m2.K/W):", self.spn_rvalue)

        self.stack.addWidget(props_page)
        self.stack.addWidget(resist_page)
        v.addWidget(self.stack)
        self.cmb_type.currentIndexChanged.connect(self.stack.setCurrentIndex)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        v.addWidget(buttons)

    def _on_save(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a name.")
            return
        if self.cmb_type.currentIndex() == 0:
            thickness, conductivity = self.spn_thickness.value(), self.spn_conductivity.value()
            if conductivity <= 0:
                QMessageBox.warning(self, "Error", "Conductivity must be positive.")
                return
            resistance = calc_resistance(thickness, conductivity)
            self.result_entry = MaterialEntry(
                user_name=name, type="PROPERTIES", thickness=thickness, conductivity=conductivity,
                density=self.spn_density.value(), spec_heat=self.spn_spec_heat.value(), resistance=resistance,
            )
        else:
            self.result_entry = MaterialEntry(user_name=name, type="RESISTANCE", resistance=self.spn_rvalue.value())
        self.accept()
