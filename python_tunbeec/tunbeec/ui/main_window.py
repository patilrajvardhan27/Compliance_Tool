"""Main application window -- Python/PySide6 port of gui.GuiMain.

5 tabs (General Information / Envelope / Windows / Spaces / HVAC System) plus a top button
strip (New/Open/Save/Save As/Prescriptive Approach/Performance Approach). The original Java
app had 4 tabs; the window/skylight inputs were split out of Envelope into their own tab so
everything fits on screen, and Domestic Hot Water moved from Spaces to the HVAC tab.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QButtonGroup, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressDialog, QPushButton,
    QRadioButton, QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from tunbeec.app_paths import DEFAULT_DB_PATH, DOE22_DIR, IMAGE_DIR, PROJECT_DIR
from tunbeec.app_state import apply_building_type_defaults, new_building_input, populate_space_rows
from tunbeec.calc.bldg_info import calc_bldg_geometry
from tunbeec.calc.performance import generate_bdl, resolve_envelope_info, run_doe22, write_inp
from tunbeec.calc.performance_report import assemble_report, determine_performance_result
from tunbeec.calc.prescriptive import run_prescriptive
from tunbeec.calc.sim_parser import parse_bec_th, parse_bldg_energy
from tunbeec.data.project import load_project, save_project
from tunbeec.data.reference import ReferenceData
from tunbeec.models import BuildingInput, SpaceConditionRow, WindowAllocationRow
from tunbeec.ui.construction_dialog import ConstructionDialog
from tunbeec.ui.glass_dialog import GlassDialog
from tunbeec.ui.performance_view import PerformanceReportDialog
from tunbeec.ui.prescriptive_view import PrescriptiveResultDialog

_SHAPES_10 = [
    "Rectangular", "L-Shape", "T-Shape", "U-Shape",
    "Hexagon", "Octagon", "Decagon", "Dodecagon", "Hexadecagon", "Octadecagon",
]
_POLYGON_SHAPES = set(_SHAPES_10[4:])

# shape -> (x1y1 visible, x2y2 visible, x3 visible, y3 visible)
_SHAPE_FIELD_VISIBILITY = {
    "Rectangular": (True, False, False, False),
    "L-Shape": (True, True, False, False),
    "T-Shape": (True, True, True, False),
    "U-Shape": (True, True, True, True),
}
for _s in _POLYGON_SHAPES:
    _SHAPE_FIELD_VISIBILITY[_s] = (True, False, False, False)  # only Y1 shown (X1 hidden separately below)

_HOT_WATER_SYSTEMS = ["Tankless Electric DHW System", "Tank Gas-fired DHW System"]
_SKYLIGHT_TYPES = ["None", "Flat", "Dome"]
_FIRST_FLOOR_CONTACTS = ["Ground", "Conditioned Space", "Unconditioned Space"]

# Illustrations bundled from the original Java app (resources/image/) -- shape name -> filename.
_SHAPE_IMAGE_FILES = {
    "Rectangular": "Rectangular.jpg",
    "L-Shape": "L-Shape.jpg",
    "T-Shape": "T-Shape.jpg",
    "U-Shape": "U-Shape.jpg",
    "Hexagon": "Hexagon-Shape.jpg",
    "Octagon": "Octagon-Shape.jpg",
    "Decagon": "Decagon-Shape.jpg",
    "Dodecagon": "Dodecagon-Shape.jpg",
    "Hexadecagon": "Hexadecagon-Shape.jpg",
    "Octadecagon": "Octadecagon-Shape.jpg",
}

# HVAC system name (as stored in the reference DB, see Bldg_System) -> illustration filename.
_HVAC_SYSTEM_IMAGE_FILES = {
    "Packaged Variable Air Volume System": "PackagedVAV.jpg",
    "Split System with Baseboard": "SplitSystem.jpg",
    "Residential System": "ResidentialSystem.jpg",
    "Fan Coil System": "FancoilSystem.jpg",
    "Central Variable Air Volume System": "VavSystem.jpg",
}

_SHADING_IMAGE_FILE = "fp.jpg"


def _set_illustration(label: QLabel, filename: str) -> None:
    """Load resources/image/<filename> into `label`, scaled to fit while preserving aspect ratio."""
    path = IMAGE_DIR / filename
    pixmap = QPixmap(str(path)) if path.exists() else QPixmap()
    if pixmap.isNull():
        label.clear()
        label.setText(f"[missing illustration: {filename}]" if filename else "")
        return
    label.setPixmap(pixmap.scaled(
        260, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
    ))


def _float_field(default=0.0, decimals=3, maximum=100000.0) -> QDoubleSpinBox:
    w = QDoubleSpinBox()
    w.setDecimals(decimals)
    w.setMaximum(maximum)
    w.setMinimum(-maximum)
    w.setValue(default)
    return w


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TUNBEEC")
        self.resize(900, 680)
        icon_path = IMAGE_DIR / "CU.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.ref = ReferenceData(DEFAULT_DB_PATH)
        self.bi: BuildingInput = new_building_input(self.ref)
        self.current_path: Path | None = None

        self._build_ui()
        self._refresh_all()

    # -- top-level layout --------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        button_row = QHBoxLayout()
        self.btn_exit = QPushButton("Exit")
        self.btn_new = QPushButton("New Project")
        self.btn_open = QPushButton("Open")
        self.btn_save = QPushButton("Save")
        self.btn_save_as = QPushButton("Save As")
        self.btn_prescriptive = QPushButton("Prescriptive Approach")
        self.btn_performance = QPushButton("Performance Approach")
        for b in (self.btn_exit, self.btn_new, self.btn_open, self.btn_save, self.btn_save_as,
                  self.btn_prescriptive, self.btn_performance):
            button_row.addWidget(b)
        layout.addLayout(button_row)

        self.btn_exit.clicked.connect(self.close)
        self.btn_new.clicked.connect(self.on_new)
        self.btn_open.clicked.connect(self.on_open)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_save_as.clicked.connect(self.on_save_as)
        self.btn_prescriptive.clicked.connect(self.on_run_prescriptive)
        self.btn_performance.clicked.connect(self.on_run_performance)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_general(), "General Information")
        self.tabs.addTab(self._build_tab_envelope(), "Envelope")
        self.tabs.addTab(self._build_tab_windows(), "Windows")
        self.tabs.addTab(self._build_tab_spaces(), "Spaces")
        self.tabs.addTab(self._build_tab_hvac(), "HVAC System")
        layout.addWidget(self.tabs)

        self.setCentralWidget(central)
        self._update_compliance_buttons()

    # -- Tab 1: General Information -------------------------------------------------------
    def _build_tab_general(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)

        gb_info = QGroupBox("General Project Information")
        f = QFormLayout(gb_info)
        self.txt_bldg_name = QLineEdit()
        self.txt_bldg_address = QLineEdit()
        f.addRow("Building Name:", self.txt_bldg_name)
        f.addRow("Address:", self.txt_bldg_address)
        v.addWidget(gb_info)

        gb_use = QGroupBox("Building Type")
        f2 = QFormLayout(gb_use)
        self.cmb_bldg_type = QComboBox()
        self.cmb_bldg_type.addItems([t.bldg_type for t in self.ref.bldg_types])
        self.cmb_bldg_location = QComboBox()
        self.cmb_bldg_location.addItems(self.ref.bldg_locations)
        self.spn_num_floor = QSpinBox()
        self.spn_num_floor.setRange(1, 200)
        self.spn_cond_area = _float_field(100.0, decimals=1, maximum=100.0)
        f2.addRow("Type:", self.cmb_bldg_type)
        f2.addRow("Location:", self.cmb_bldg_location)
        f2.addRow("Number of Floors:", self.spn_num_floor)
        self.lbl_cond_area = QLabel("Conditioned Area (%):")
        f2.addRow(self.lbl_cond_area, self.spn_cond_area)
        v.addWidget(gb_use)

        gb_shape = QGroupBox("Building Shape")
        gb_shape_row = QHBoxLayout(gb_shape)
        shape_fields = QWidget()
        f3 = QFormLayout(shape_fields)
        gb_shape_row.addWidget(shape_fields, 1)
        self.lbl_shape_image = QLabel()
        self.lbl_shape_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_shape_image.setMinimumSize(260, 220)
        gb_shape_row.addWidget(self.lbl_shape_image)
        self.cmb_bldg_shape = QComboBox()
        self.cmb_bldg_shape.addItems(_SHAPES_10)
        f3.addRow("Shape:", self.cmb_bldg_shape)

        self.spn_x1 = _float_field(10.0)
        self.spn_y1 = _float_field(10.0)
        self.spn_x2 = _float_field(0.0)
        self.spn_y2 = _float_field(0.0)
        self.spn_x3 = _float_field(0.0)
        self.spn_y3 = _float_field(0.0)
        self.row_x1 = (QLabel("X1 (m):"), self.spn_x1)
        self.row_y1 = (QLabel("Y1 (m):"), self.spn_y1)
        self.row_x2 = (QLabel("X2 (m):"), self.spn_x2)
        self.row_y2 = (QLabel("Y2 (m):"), self.spn_y2)
        self.row_x3 = (QLabel("X3 (m):"), self.spn_x3)
        self.row_y3 = (QLabel("Y3 (m):"), self.spn_y3)
        for label, widget in (self.row_x1, self.row_y1, self.row_x2, self.row_y2, self.row_x3, self.row_y3):
            f3.addRow(label, widget)

        self.txt_floor_area = QLineEdit()
        self.txt_floor_area.setReadOnly(True)
        f3.addRow("Floor Area (m2):", self.txt_floor_area)

        self.spn_azimuth = _float_field(0.0, decimals=1, maximum=360.0)
        self.spn_floor_height = _float_field(3.0, decimals=2, maximum=20.0)
        f3.addRow("Orientation (deg):", self.spn_azimuth)
        f3.addRow("Floor Height (m):", self.spn_floor_height)
        v.addWidget(gb_shape)
        v.addStretch(1)

        self.cmb_bldg_type.currentTextChanged.connect(self._on_bldg_type_changed)
        self.cmb_bldg_shape.currentTextChanged.connect(self._on_shape_changed)
        for spn in (self.spn_x1, self.spn_y1, self.spn_x2, self.spn_y2, self.spn_x3, self.spn_y3):
            spn.valueChanged.connect(self._recompute_floor_area)

        return page

    def _on_shape_changed(self, shape: str):
        x1y1, x2y2, x3, y3 = _SHAPE_FIELD_VISIBILITY.get(shape, (True, False, False, False))
        is_polygon = shape in _POLYGON_SHAPES
        for label, widget in (self.row_x1,):
            label.setVisible(x1y1 and not is_polygon)
            widget.setVisible(x1y1 and not is_polygon)
        for label, widget in (self.row_y1,):
            label.setVisible(x1y1)
            widget.setVisible(x1y1)
        for label, widget in (self.row_x2, self.row_y2):
            label.setVisible(x2y2)
            widget.setVisible(x2y2)
        self.row_x3[0].setVisible(x3)
        self.row_x3[1].setVisible(x3)
        self.row_y3[0].setVisible(y3)
        self.row_y3[1].setVisible(y3)
        _set_illustration(self.lbl_shape_image, _SHAPE_IMAGE_FILES.get(shape, ""))
        self._recompute_floor_area()

    def _recompute_floor_area(self):
        from tunbeec.calc import shape as shape_calc
        shape = self.cmb_bldg_shape.currentText()
        try:
            area = shape_calc.calc_floor_area(
                shape, self.spn_x1.value(), self.spn_y1.value(),
                self.spn_x2.value(), self.spn_y2.value(), self.spn_x3.value(), self.spn_y3.value(),
            )
            self.txt_floor_area.setText(f"{area:.2f}")
        except Exception:
            self.txt_floor_area.setText("")

    # -- Tab 2: Envelope ----------------------------------------------------------------------
    def _build_tab_envelope(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)

        gb_const = QGroupBox("Building Envelope Constructions")
        f = QFormLayout(gb_const)
        self.cmb_south_wall = QComboBox()
        self.cmb_north_wall = QComboBox()
        self.cmb_east_wall = QComboBox()
        self.cmb_west_wall = QComboBox()
        self.cmb_roof = QComboBox()
        wall_names = list(self.ref.constructions_wall.keys())
        roof_names = list(self.ref.constructions_roof.keys())
        for cmb in (self.cmb_south_wall, self.cmb_north_wall, self.cmb_east_wall, self.cmb_west_wall):
            cmb.addItem("-Create-")
            cmb.addItems(wall_names)
        self.cmb_roof.addItem("-Create-")
        self.cmb_roof.addItems(roof_names)

        def _wall_row(label, combo, all_wall_combos):
            row = QHBoxLayout()
            row.addWidget(combo, 1)
            btn = QPushButton("Edit")
            btn.clicked.connect(lambda: self._create_construction("Wall", all_wall_combos))
            row.addWidget(btn)
            container = QWidget()
            container.setLayout(row)
            f.addRow(label, container)
            combo.currentTextChanged.connect(
                lambda text: self._on_construction_combo_changed("Wall", text, all_wall_combos)
            )

        wall_combos = (self.cmb_south_wall, self.cmb_north_wall, self.cmb_east_wall, self.cmb_west_wall)
        _wall_row("South Wall:", self.cmb_south_wall, wall_combos)
        _wall_row("North Wall:", self.cmb_north_wall, wall_combos)
        _wall_row("East Wall:", self.cmb_east_wall, wall_combos)
        _wall_row("West Wall:", self.cmb_west_wall, wall_combos)

        roof_row = QHBoxLayout()
        roof_row.addWidget(self.cmb_roof, 1)
        btn_roof = QPushButton("Edit")
        btn_roof.clicked.connect(lambda: self._create_construction("Roof", (self.cmb_roof,)))
        roof_row.addWidget(btn_roof)
        roof_container = QWidget()
        roof_container.setLayout(roof_row)
        f.addRow("Roof:", roof_container)
        self.cmb_roof.currentTextChanged.connect(
            lambda text: self._on_construction_combo_changed("Roof", text, (self.cmb_roof,))
        )
        self.cmb_first_floor_contact = QComboBox()
        self.cmb_first_floor_contact.addItems(_FIRST_FLOOR_CONTACTS)
        f.addRow("First Floor Exposure:", self.cmb_first_floor_contact)
        v.addWidget(gb_const)
        v.addStretch(1)
        return page

    # -- Tab 3: Windows (split out of the original Envelope tab, which overflowed the screen) --
    def _build_tab_windows(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)

        gb_win = QGroupBox("Windows — conditioned zones only")
        vw = QVBoxLayout(gb_win)
        radio_row = QHBoxLayout()
        self.rdb_wwr = QRadioButton("Window-to-Wall Ratio (%)")
        self.rdb_area = QRadioButton("Window Area (m2)")
        self.rdb_wwr.setChecked(True)
        grp = QButtonGroup(gb_win)
        grp.addButton(self.rdb_wwr)
        grp.addButton(self.rdb_area)
        radio_row.addWidget(self.rdb_wwr)
        radio_row.addWidget(self.rdb_area)
        vw.addLayout(radio_row)

        self.tbl_win = QTableWidget(5, 6)
        self.tbl_win.setHorizontalHeaderLabels(["South", "North", "East", "West", "Glass Type", ""])
        self.tbl_win.setVerticalHeaderLabels([f"#{i+1}" for i in range(5)])
        self.win_glass_combos: list[QComboBox] = []
        glass_names = list(self.ref.glass.keys())
        for row in range(5):
            combo = QComboBox()
            combo.addItems(["", "-Create-"] + glass_names)
            combo.currentTextChanged.connect(lambda text, r=row: self._on_glass_combo_changed(r, text))
            self.tbl_win.setCellWidget(row, 4, combo)
            self.win_glass_combos.append(combo)
            for col in range(4):
                self.tbl_win.setItem(row, col, QTableWidgetItem("0"))
            btn = QPushButton("Edit")
            btn.clicked.connect(lambda checked=False, r=row: self._edit_glass(r))
            self.tbl_win.setCellWidget(row, 5, btn)
        self.tbl_win.horizontalHeader().setStretchLastSection(True)
        vw.addWidget(self.tbl_win)

        overhang_group = QHBoxLayout()
        overhang_fields = QWidget()
        overhang_row = QFormLayout(overhang_fields)
        self.spn_overhang = _float_field(0.0, decimals=2, maximum=10.0)
        self.spn_fp = _float_field(0.0, decimals=2, maximum=5.0)
        overhang_row.addRow("South Overhang Depth (m):", self.spn_overhang)
        overhang_row.addRow("South Projection Factor:", self.spn_fp)
        overhang_group.addWidget(overhang_fields, 1)
        lbl_shading_image = QLabel()
        lbl_shading_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_shading_image.setMinimumSize(200, 180)
        _set_illustration(lbl_shading_image, _SHADING_IMAGE_FILE)
        overhang_group.addWidget(lbl_shading_image)
        vw.addLayout(overhang_group)

        sky_row = QFormLayout()
        self.cmb_skylight_type = QComboBox()
        self.cmb_skylight_type.addItems(_SKYLIGHT_TYPES)
        self.spn_skylight_cvr = _float_field(0.0, decimals=1, maximum=100.0)
        sky_row.addRow("Skylight Type:", self.cmb_skylight_type)
        sky_row.addRow("Coverage (%):", self.spn_skylight_cvr)
        vw.addLayout(sky_row)

        v.addWidget(gb_win)
        v.addStretch(1)
        return page

    # -- Tab 4: Spaces -------------------------------------------------------------------------
    def _build_tab_spaces(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)

        gb = QGroupBox("Space Conditioning")
        vb = QVBoxLayout(gb)
        self.tbl_space = QTableWidget(8, 8)
        self.tbl_space.setHorizontalHeaderLabels([
            "Space Type", "% Area", "Occupancy (m2/person)", "Infiltration (ACH)",
            "Lighting (W/m2)", "Equipment (W/m2)", "Conditioned", "Unconditioned",
        ])
        self.tbl_space.horizontalHeader().setStretchLastSection(True)
        self.space_radio_groups: list[QButtonGroup] = []
        vb.addWidget(self.tbl_space)

        self.lbl_space_sum = QLabel("Total: 0%")
        vb.addWidget(self.lbl_space_sum)
        v.addWidget(gb)
        v.addStretch(1)
        return page

    # -- Tab 5: HVAC System ---------------------------------------------------------------------
    def _build_tab_hvac(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        gb = QGroupBox("System")
        gb_row = QHBoxLayout(gb)
        fields = QWidget()
        f = QFormLayout(fields)
        self.cmb_bldg_system = QComboBox()
        self.cmb_bldg_system.addItems(self.ref.bldg_systems)
        self.spn_heat_temp = _float_field(20.0, decimals=1, maximum=40.0)
        self.spn_cool_temp = _float_field(24.0, decimals=1, maximum=40.0)
        f.addRow("HVAC System:", self.cmb_bldg_system)
        f.addRow("Heating Setpoint (°C):", self.spn_heat_temp)
        f.addRow("Cooling Setpoint (°C):", self.spn_cool_temp)
        gb_row.addWidget(fields, 1)

        self.lbl_hvac_image = QLabel()
        self.lbl_hvac_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hvac_image.setMinimumSize(300, 200)
        gb_row.addWidget(self.lbl_hvac_image)

        self.cmb_bldg_system.currentTextChanged.connect(
            lambda text: _set_illustration(self.lbl_hvac_image, _HVAC_SYSTEM_IMAGE_FILES.get(text, ""))
        )
        v.addWidget(gb)

        gb_eff = QGroupBox("Energy Efficiency")
        f_eff = QFormLayout(gb_eff)
        self.spn_cool_cop = _float_field(2.6, decimals=2, maximum=10.0)
        self.spn_cool_cop.setMinimum(0.5)
        self.spn_heat_eff = _float_field(75.0, decimals=1, maximum=500.0)
        self.spn_heat_eff.setMinimum(10.0)
        f_eff.addRow("Cooling Efficiency — COP:", self.spn_cool_cop)
        f_eff.addRow("Heating Efficiency (%):", self.spn_heat_eff)
        f_eff.addRow(QLabel(
            "<i>Defaults match the reference systems (COP 2.6, 75%). "
            "Heating efficiency above 100% represents a heat pump.</i>"))
        v.addWidget(gb_eff)

        gb_dhw = QGroupBox("Domestic Hot Water")
        f_dhw = QFormLayout(gb_dhw)
        self.cmb_hot_water = QComboBox()
        self.cmb_hot_water.addItems(_HOT_WATER_SYSTEMS)
        f_dhw.addRow("System:", self.cmb_hot_water)
        v.addWidget(gb_dhw)
        v.addStretch(1)
        return page

    # -- state sync: BuildingInput <-> widgets ---------------------------------------------------
    def _sync_user_library_combos(self):
        """Ensure project-local user-defined constructions/glass appear in the relevant combos
        (GuiConst.btnOk / GuiGlass.btnSave add newly-created names to GuiMain's comboboxes)."""
        wall_names = {self.cmb_south_wall.itemText(i) for i in range(self.cmb_south_wall.count())}
        for c in self.bi.user_constructions_wall:
            if c.user_name not in wall_names:
                for cmb in (self.cmb_south_wall, self.cmb_north_wall, self.cmb_east_wall, self.cmb_west_wall):
                    cmb.addItem(c.user_name)
        roof_names = {self.cmb_roof.itemText(i) for i in range(self.cmb_roof.count())}
        for c in self.bi.user_constructions_roof:
            if c.user_name not in roof_names:
                self.cmb_roof.addItem(c.user_name)
        glass_names = {self.win_glass_combos[0].itemText(i) for i in range(self.win_glass_combos[0].count())}
        for g in self.bi.user_glass:
            if g.user_name not in glass_names:
                for combo in self.win_glass_combos:
                    combo.addItem(g.user_name)

    def _refresh_all(self):
        self._sync_user_library_combos()
        bi = self.bi
        self.txt_bldg_name.setText(bi.txtBldgName)
        self.txt_bldg_address.setText(bi.txtBldgAddress)
        # Block signals: setting this combo fires _on_bldg_type_changed, which snapshots every
        # other widget via _collect_from_widgets() -- the rest of this method hasn't refreshed
        # them from `bi` yet, so that snapshot would clobber bi with stale/placeholder widget
        # state (e.g. the wall/roof combos still on their "-Create-" placeholder item).
        self.cmb_bldg_type.blockSignals(True)
        self._set_combo(self.cmb_bldg_type, bi.cmbBldgType)
        self.cmb_bldg_type.blockSignals(False)
        self._set_combo(self.cmb_bldg_location, bi.cmbBldgLocation)
        self.spn_num_floor.setValue(bi.txtBldgNumFloor)
        self.spn_cond_area.setValue(bi.txtBldgCondArea)
        self._set_combo(self.cmb_bldg_shape, bi.cmbBldgShape)
        self.spn_x1.setValue(bi.txtLengX1)
        self.spn_y1.setValue(bi.txtLengY1)
        self.spn_x2.setValue(bi.txtLengX2)
        self.spn_y2.setValue(bi.txtLengY2)
        self.spn_x3.setValue(bi.txtLengX3)
        self.spn_y3.setValue(bi.txtLengY3)
        self.spn_azimuth.setValue(bi.txtBldgAzi)
        self.spn_floor_height.setValue(bi.txtFloorHeight)
        self._on_shape_changed(bi.cmbBldgShape)

        self._set_combo(self.cmb_south_wall, bi.cmbSouthWall)
        self._set_combo(self.cmb_north_wall, bi.cmbNorthWall)
        self._set_combo(self.cmb_east_wall, bi.cmbEastWall)
        self._set_combo(self.cmb_west_wall, bi.cmbWestWall)
        self._set_combo(self.cmb_roof, bi.cmbRoof)
        self._set_combo(self.cmb_first_floor_contact, bi.cmbFirstFloorContact)
        self.rdb_wwr.setChecked(bi.rdbtnWinWwr)
        self.rdb_area.setChecked(not bi.rdbtnWinWwr)
        self._refresh_window_table()
        self.spn_overhang.setValue(bi.txtWinSouthOverhang)
        self.spn_fp.setValue(bi.txtWinSouthFp)
        self._set_combo(self.cmb_skylight_type, bi.txtSkyltType)
        self.spn_skylight_cvr.setValue(bi.txtSkyltCvr)

        self._refresh_space_table()
        self._set_combo(self.cmb_hot_water, bi.cmbHotWaterSystem)

        self._set_combo(self.cmb_bldg_system, bi.cmbBldgSystem)
        _set_illustration(self.lbl_hvac_image, _HVAC_SYSTEM_IMAGE_FILES.get(bi.cmbBldgSystem, ""))
        self.spn_heat_temp.setValue(bi.txtHeatSetTemp)
        self.spn_cool_temp.setValue(bi.txtCoolSetTemp)
        self.spn_cool_cop.setValue(bi.txtCoolCOP)
        self.spn_heat_eff.setValue(bi.txtHeatEff)

        self._update_compliance_buttons()

    @staticmethod
    def _set_combo(combo: QComboBox, value: str):
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _refresh_window_table(self):
        for row, wr in enumerate(self.bi.window_rows[:5]):
            self.tbl_win.item(row, 0).setText(str(wr.south_percent))
            self.tbl_win.item(row, 1).setText(str(wr.north_percent))
            self.tbl_win.item(row, 2).setText(str(wr.east_percent))
            self.tbl_win.item(row, 3).setText(str(wr.west_percent))
            self._set_combo(self.win_glass_combos[row], wr.glass_type)

    def _refresh_space_table(self):
        self.tbl_space.clearContents()
        self.space_radio_groups = []
        rows = self.bi.space_rows[:8]
        self.tbl_space.setRowCount(max(8, len(rows)))
        for row in range(self.tbl_space.rowCount()):
            if row < len(rows):
                r = rows[row]
                self.tbl_space.setItem(row, 0, QTableWidgetItem(r.area_type))
                self.tbl_space.setItem(row, 1, QTableWidgetItem(str(r.percent_area)))
                self.tbl_space.setItem(row, 2, QTableWidgetItem(str(r.occupant)))
                self.tbl_space.setItem(row, 3, QTableWidgetItem(str(r.infiltration)))
                self.tbl_space.setItem(row, 4, QTableWidgetItem(str(r.lighting)))
                self.tbl_space.setItem(row, 5, QTableWidgetItem(str(r.plug_load)))
                rb_cond = QRadioButton()
                rb_uncond = QRadioButton()
                rb_cond.setChecked(r.conditioned)
                rb_uncond.setChecked(not r.conditioned)
            else:
                for col in range(6):
                    self.tbl_space.setItem(row, col, QTableWidgetItem(""))
                rb_cond = QRadioButton()
                rb_uncond = QRadioButton()
            grp = QButtonGroup(self.tbl_space)
            grp.addButton(rb_cond)
            grp.addButton(rb_uncond)
            self.space_radio_groups.append(grp)
            self.tbl_space.setCellWidget(row, 6, rb_cond)
            self.tbl_space.setCellWidget(row, 7, rb_uncond)
        self._update_space_sum()

    def _update_space_sum(self):
        total = 0.0
        for row in range(self.tbl_space.rowCount()):
            item = self.tbl_space.item(row, 1)
            if item and item.text():
                try:
                    total += float(item.text())
                except ValueError:
                    pass
        self.lbl_space_sum.setText(f"Total: {total:.0f}%")

    def _collect_from_widgets(self) -> None:
        """Pull current widget state back into self.bi (GuiMain.setUserBldgKV_WinAllocation)."""
        bi = self.bi
        bi.txtBldgName = self.txt_bldg_name.text()
        bi.txtBldgAddress = self.txt_bldg_address.text()
        bi.cmbBldgType = self.cmb_bldg_type.currentText()
        bi.cmbBldgLocation = self.cmb_bldg_location.currentText()
        bi.txtBldgNumFloor = self.spn_num_floor.value()
        bi.txtBldgCondArea = self.spn_cond_area.value()
        bi.cmbBldgShape = self.cmb_bldg_shape.currentText()
        bi.txtLengX1 = self.spn_x1.value()
        bi.txtLengY1 = self.spn_y1.value()
        bi.txtLengX2 = self.spn_x2.value()
        bi.txtLengY2 = self.spn_y2.value()
        bi.txtLengX3 = self.spn_x3.value()
        bi.txtLengY3 = self.spn_y3.value()
        bi.txtBldgAzi = self.spn_azimuth.value()
        bi.txtFloorHeight = self.spn_floor_height.value()
        try:
            bi.txtFloorArea = float(self.txt_floor_area.text())
        except ValueError:
            bi.txtFloorArea = 0.0

        bi.cmbSouthWall = self.cmb_south_wall.currentText()
        bi.cmbNorthWall = self.cmb_north_wall.currentText()
        bi.cmbEastWall = self.cmb_east_wall.currentText()
        bi.cmbWestWall = self.cmb_west_wall.currentText()
        bi.cmbRoof = self.cmb_roof.currentText()
        bi.cmbFirstFloorContact = self.cmb_first_floor_contact.currentText()
        bi.rdbtnWinWwr = self.rdb_wwr.isChecked()

        rows = []
        for row in range(5):
            def _num(col):
                item = self.tbl_win.item(row, col)
                try:
                    return float(item.text()) if item and item.text() else 0.0
                except ValueError:
                    return 0.0
            rows.append(WindowAllocationRow(
                south_percent=_num(0), north_percent=_num(1), east_percent=_num(2), west_percent=_num(3),
                glass_type=self.win_glass_combos[row].currentText(),
            ))
        bi.window_rows = rows

        bi.txtWinSouthOverhang = self.spn_overhang.value()
        bi.txtWinSouthFp = self.spn_fp.value()
        bi.txtSkyltType = self.cmb_skylight_type.currentText()
        bi.txtSkyltCvr = self.spn_skylight_cvr.value()

        space_rows = []
        for row in range(self.tbl_space.rowCount()):
            type_item = self.tbl_space.item(row, 0)
            if not type_item or not type_item.text():
                continue

            def _sval(col):
                item = self.tbl_space.item(row, col)
                try:
                    return float(item.text()) if item and item.text() else 0.0
                except ValueError:
                    return 0.0
            rb_cond = self.tbl_space.cellWidget(row, 6)
            space_rows.append(SpaceConditionRow(
                area_type=type_item.text(), percent_area=_sval(1), occupant=_sval(2),
                infiltration=_sval(3), lighting=_sval(4), plug_load=_sval(5),
                conditioned=rb_cond.isChecked() if rb_cond else True,
            ))
        bi.space_rows = space_rows

        bi.cmbHotWaterSystem = self.cmb_hot_water.currentText()
        bi.cmbBldgSystem = self.cmb_bldg_system.currentText()
        bi.txtHeatSetTemp = self.spn_heat_temp.value()
        bi.txtCoolSetTemp = self.spn_cool_temp.value()
        bi.txtCoolCOP = self.spn_cool_cop.value()
        bi.txtHeatEff = self.spn_heat_eff.value()

    # -- construction/glass "-Create-" library editing -------------------------------------------
    def _create_construction(self, kind: str, combos: tuple[QComboBox, ...]):
        dlg = ConstructionDialog(kind, self.ref, self.bi, self)
        if not dlg.exec() or dlg.new_construction is None:
            for combo in combos:
                if combo.currentText() == "-Create-":
                    combo.setCurrentIndex(0)
            return
        target_const = self.bi.user_constructions_wall if kind == "Wall" else self.bi.user_constructions_roof
        target_const.append(dlg.new_construction)
        if dlg.new_layer is not None:
            target_layer = self.bi.user_layers_wall if kind == "Wall" else self.bi.user_layers_roof
            target_layer.append(dlg.new_layer)
        for combo in combos:
            combo.blockSignals(True)
            combo.addItem(dlg.new_construction.user_name)
            combo.setCurrentText(dlg.new_construction.user_name)
            combo.blockSignals(False)

    def _on_construction_combo_changed(self, kind: str, text: str, combos: tuple[QComboBox, ...]):
        if text == "-Create-":
            self._create_construction(kind, combos)

    def _on_glass_combo_changed(self, row: int, text: str):
        if text == "-Create-":
            self._create_glass(row)

    def _create_glass(self, row: int):
        dlg = GlassDialog(self)
        combo = self.win_glass_combos[row]
        if not dlg.exec() or dlg.result_entry is None:
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)
            return
        self.bi.user_glass.append(dlg.result_entry)
        for c in self.win_glass_combos:
            c.blockSignals(True)
            c.addItem(dlg.result_entry.user_name)
            c.blockSignals(False)
        combo.blockSignals(True)
        combo.setCurrentText(dlg.result_entry.user_name)
        combo.blockSignals(False)

    def _edit_glass(self, row: int):
        current = self.win_glass_combos[row].currentText()
        if not current or current == "-Create-":
            QMessageBox.information(self, "Edit", "Please select a glass type first.")
            return
        QMessageBox.information(
            self, "Edit",
            f"Selected glass: {current}\n(editing an existing glass type is not supported -- "
            "use \"-Create-\" to add a new type).",
        )

    def _on_bldg_type_changed(self, _text: str):
        self._collect_from_widgets()
        apply_building_type_defaults(self.bi, self.ref)
        self._refresh_window_table()
        self._refresh_space_table()
        self._set_combo(self.cmb_bldg_system, self.bi.cmbBldgSystem)
        _set_illustration(self.lbl_hvac_image, _HVAC_SYSTEM_IMAGE_FILES.get(self.bi.cmbBldgSystem, ""))
        self._update_compliance_buttons()

    def _update_compliance_buttons(self):
        """btnSave/btnSaveAs handler logic: Hotel/Hospital -> Prescriptive disabled."""
        type_row = self.ref.bldg_type_row(self.cmb_bldg_type.currentText())
        cat = type_row.cat if type_row else ""
        prescriptive_ok = cat not in ("Hotel", "Hospital")
        self.btn_prescriptive.setEnabled(prescriptive_ok)

    # -- file actions -----------------------------------------------------------------------
    def on_new(self):
        self.bi = new_building_input(self.ref)
        self.current_path = None
        self._refresh_all()

    def on_open(self):
        PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        path_str, _ = QFileDialog.getOpenFileName(self, "Open", str(PROJECT_DIR), "TUNBEEC Project (*.tct)")
        if not path_str:
            return
        try:
            self.bi = load_project(Path(path_str))
            populate_space_rows(self.bi, self.ref)  # tblSpaceCond is never persisted, see app_state.py
            self.current_path = Path(path_str)
            self._refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to open file:\n{e}")

    def on_save(self):
        self._collect_from_widgets()
        if self.current_path is None:
            self.on_save_as()
            return
        save_project(self.current_path, self.bi)
        self._update_compliance_buttons()

    def on_save_as(self):
        self._collect_from_widgets()
        PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        path_str, _ = QFileDialog.getSaveFileName(self, "Save As", str(PROJECT_DIR), "TUNBEEC Project (*.tct)")
        if not path_str:
            return
        if not path_str.endswith(".tct"):
            path_str += ".tct"
        save_project(Path(path_str), self.bi)
        self.current_path = Path(path_str)
        self._update_compliance_buttons()

    # -- compliance checks --------------------------------------------------------------------
    def on_run_prescriptive(self):
        self._collect_from_widgets()
        try:
            geo = calc_bldg_geometry(self.bi, self.ref, self.bi.space_rows)
            result = run_prescriptive(self.bi, self.ref, geo)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Calculation failed:\n{e}")
            return
        dlg = PrescriptiveResultDialog(result, self)
        dlg.exec()

    def on_run_performance(self):
        self._collect_from_widgets()
        if self.current_path is None:
            QMessageBox.warning(self, "Performance Approach", "Please save the project first.")
            return
        if self.bi.rdbtnWinWwr:
            for orientation, attr in (("South", "south_percent"), ("North", "north_percent"),
                                       ("East", "east_percent"), ("West", "west_percent")):
                total = sum(getattr(row, attr) for row in self.bi.window_rows)
                if total > 100.0:
                    QMessageBox.warning(
                        self, "Performance Approach",
                        f"The window rows on the {orientation} wall add up to {total:.0f}% of the "
                        "wall area. The combined Window-to-Wall Ratio per orientation cannot "
                        "exceed 100% -- DOE-2.2 would reject the building (windows larger than "
                        "the wall). Please reduce the window percentages.",
                    )
                    return
        try:
            geo = calc_bldg_geometry(self.bi, self.ref, self.bi.space_rows)
            envelope = resolve_envelope_info(self.ref, self.bi, geo)
            lines, area = generate_bdl(self.bi, self.ref, geo)
            file_stem = self.current_path.stem
            inp_path = write_inp(self.current_path.parent, file_stem, lines)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"BDL file generation failed:\n{e}")
            return

        wait_dlg = QProgressDialog("Running DOE-2.2 simulation, please wait...", "", 0, 0, self)
        wait_dlg.setWindowTitle("Performance Approach")
        wait_dlg.setCancelButton(None)
        wait_dlg.setWindowModality(Qt.WindowModal)
        wait_dlg.setMinimumDuration(0)
        wait_dlg.show()
        QApplication.processEvents()
        try:
            run_result = run_doe22(DOE22_DIR, self.current_path.parent, file_stem, self.bi.cmbBldgLocation)
        finally:
            wait_dlg.close()
        sim_path = run_result.sim_path
        if sim_path is None:
            candidate = self.current_path.parent / f"{file_stem}.sim"
            if candidate.exists() and candidate.stat().st_size > 0:
                sim_path = candidate  # reuse a .sim produced by a prior Windows run of RUN22.exe

        if sim_path is None:
            if sys.platform != "win32":
                QMessageBox.information(
                    self, "Performance Approach",
                    f"BDL file generated: {inp_path}\n\n"
                    "The DOE-2.2 simulation engine (doe22/RUN22.exe) is a Windows binary and cannot "
                    "be run on this platform. Run this .inp file through the original Windows "
                    f"installation to produce {file_stem}.sim, then re-run this check "
                    "(the .sim file will be detected automatically in the project folder).\n\n"
                    f"Detail: {run_result.message}",
                )
            else:
                QMessageBox.critical(
                    self, "Performance Approach",
                    f"DOE-2.2 simulation failed:\n\n{run_result.message}",
                )
            return

        try:
            thermal = parse_bec_th(sim_path, area.cond_area_si, geo.skylt_clg_cor, geo.skylt_htg_cor,
                                    geo.flr_shape_clg_cor, geo.flr_shape_htg_cor)
            energy = parse_bldg_energy(sim_path)
            perf = determine_performance_result(geo, thermal.bec_th)
            report = assemble_report(self.bi.txtBldgName, self.bi.txtBldgAddress, self.bi.cmbBldgType,
                                      geo, envelope, area, thermal, energy, perf)
            report.bldg_loc = self.bi.cmbBldgLocation
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Simulation result analysis failed:\n{e}")
            return

        dlg = PerformanceReportDialog(report, self)
        dlg.exec()


def main():
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    icon_path = IMAGE_DIR / "CU.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
