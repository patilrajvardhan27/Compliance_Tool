""""-Create-"/"Edit" wall & roof construction dialog -- port of gui.GuiConst.

Simplified to the "create a new construction" flow (viewing/editing an existing library
construction read-only is not needed for compliance checking, only for defining new ones).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QSpinBox, QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from tunbeec.calc.uvalue import calc_u_value_from_layers
from tunbeec.data.reference import ReferenceData
from tunbeec.models import BuildingInput, ConstructionEntry, LayerEntry, MaterialEntry
from tunbeec.ui.material_dialog import MaterialDialog

_LAYER_ROWS = 7
_COLS = ["Material", "Thickness(m)", "Conductivity(W/m.K)", "Density(kg/m3)", "Specific Heat(J/kg.K)", "R Value(m2.K/W)"]


class ConstructionDialog(QDialog):
    def __init__(self, kind: str, ref: ReferenceData, bi: BuildingInput, parent=None):
        super().__init__(parent)
        self.kind = kind  # "Wall" | "Roof"
        self.ref = ref
        self.bi = bi
        self.setWindowTitle(f"New Construction ({'Wall' if kind == 'Wall' else 'Roof'})")
        self.resize(640, 420)
        self.new_construction: ConstructionEntry | None = None
        self.new_layer: LayerEntry | None = None

        v = QVBoxLayout(self)
        top = QFormLayout()
        self.txt_name = QLineEdit()
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["Enter layers", "Enter U-Value"])
        self.spn_roughness = QSpinBox(); self.spn_roughness.setRange(1, 6); self.spn_roughness.setValue(4)
        self.spn_absorptance = QDoubleSpinBox(); self.spn_absorptance.setDecimals(2); self.spn_absorptance.setMaximum(1.0)
        self.spn_absorptance.setValue(0.6)
        top.addRow("Name:", self.txt_name)
        top.addRow("Method:", self.cmb_method)
        top.addRow("Roughness:", self.spn_roughness)
        top.addRow("Absorptance:", self.spn_absorptance)
        v.addLayout(top)

        self.stack = QStackedWidget()

        layers_page = QWidget()
        lv = QVBoxLayout(layers_page)
        self.txt_layer_name = QLineEdit()
        lv.addWidget(QLabel("Layer Name:"))
        lv.addWidget(self.txt_layer_name)
        self.tbl_layers = QTableWidget(_LAYER_ROWS, len(_COLS))
        self.tbl_layers.setHorizontalHeaderLabels(_COLS)
        self.mat_combos: list[QComboBox] = []
        self.all_materials = dict(ref.materials)
        self.all_materials.update({m.user_name: m for m in bi.user_materials})
        for row in range(_LAYER_ROWS):
            combo = QComboBox()
            combo.addItems([""] + ["-Create-"] + list(self.all_materials.keys()))
            combo.currentTextChanged.connect(lambda text, r=row: self._on_material_selected(r, text))
            self.tbl_layers.setCellWidget(row, 0, combo)
            self.mat_combos.append(combo)
            for col in range(1, 6):
                item = QTableWidgetItem("")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tbl_layers.setItem(row, col, item)
        self.tbl_layers.horizontalHeader().setStretchLastSection(True)
        lv.addWidget(self.tbl_layers)
        self.lbl_calc_u = QLabel("Calculated U: -")
        lv.addWidget(self.lbl_calc_u)

        uvalue_page = QWidget()
        uf = QFormLayout(uvalue_page)
        self.spn_uvalue = QDoubleSpinBox(); self.spn_uvalue.setDecimals(3); self.spn_uvalue.setMaximum(20.0)
        self.spn_uvalue.setValue(0.5)
        uf.addRow("U-Value (W/m2.C):", self.spn_uvalue)

        self.stack.addWidget(layers_page)
        self.stack.addWidget(uvalue_page)
        v.addWidget(self.stack)
        self.cmb_method.currentIndexChanged.connect(self.stack.setCurrentIndex)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        v.addWidget(buttons)

    def _on_material_selected(self, row: int, name: str):
        if name == "-Create-":
            dlg = MaterialDialog(self)
            if dlg.exec() and dlg.result_entry:
                mat = dlg.result_entry
                self.all_materials[mat.user_name] = mat
                self.bi.user_materials.append(mat)
                combo = self.mat_combos[row]
                combo.blockSignals(True)
                combo.addItem(mat.user_name)
                combo.setCurrentText(mat.user_name)
                combo.blockSignals(False)
                name = mat.user_name
            else:
                self.mat_combos[row].blockSignals(True)
                self.mat_combos[row].setCurrentIndex(0)
                self.mat_combos[row].blockSignals(False)
                return
        mat = self.all_materials.get(name)
        if mat is None:
            for col in range(1, 6):
                self.tbl_layers.item(row, col).setText("")
        else:
            self.tbl_layers.item(row, 1).setText("" if mat.thickness is None else str(mat.thickness))
            self.tbl_layers.item(row, 2).setText("" if mat.conductivity is None else str(mat.conductivity))
            self.tbl_layers.item(row, 3).setText("" if mat.density is None else str(mat.density))
            self.tbl_layers.item(row, 4).setText("" if mat.spec_heat is None else str(mat.spec_heat))
            self.tbl_layers.item(row, 5).setText(str(mat.resistance))
        self._recompute_u()

    def _recompute_u(self):
        resistances = []
        for row in range(_LAYER_ROWS):
            text = self.tbl_layers.item(row, 5).text()
            if text:
                try:
                    resistances.append(float(text))
                except ValueError:
                    pass
        if resistances:
            u = calc_u_value_from_layers(resistances)
            self.lbl_calc_u.setText(f"Calculated U: {u:.3f}")
        else:
            self.lbl_calc_u.setText("Calculated U: -")

    def _on_save(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a name.")
            return

        if self.cmb_method.currentIndex() == 0:
            layer_name = self.txt_layer_name.text().strip()
            if not layer_name:
                QMessageBox.warning(self, "Error", "Please enter a layer name.")
                return
            materials = [c.currentText() for c in self.mat_combos if c.currentText() not in ("", "-Create-")]
            if not materials:
                QMessageBox.warning(self, "Error", "Please select at least one material.")
                return
            resistances = [self.all_materials[m].resistance for m in materials]
            u_value = calc_u_value_from_layers(resistances)
            self.new_layer = LayerEntry(user_name=layer_name, materials=materials, u_value=u_value)
            self.new_construction = ConstructionEntry(
                user_name=name, type="LAYERS", absorptance=self.spn_absorptance.value(),
                roughness=self.spn_roughness.value(), layer_name=layer_name, u_value=u_value,
            )
        else:
            self.new_construction = ConstructionEntry(
                user_name=name, type="U-VALUE", absorptance=self.spn_absorptance.value(),
                roughness=self.spn_roughness.value(), u_value=self.spn_uvalue.value(),
            )
        self.accept()
