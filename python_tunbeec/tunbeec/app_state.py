"""Builds a fresh/default BuildingInput and keeps its category-dependent tables (window
allocation, space condition) in sync with the currently selected cmbBldgType -- port of
GuiMain.setGuiInit() plus the cmbBldgType change-listener's table-repopulation logic.
"""
from __future__ import annotations

from tunbeec.data.reference import ReferenceData
from tunbeec.models import BuildingInput, SpaceConditionRow, WindowAllocationRow

# gui_inventory.md §6 -- which of the 5 Bldg_System entries are offered per building category,
# and which is pre-selected. Indices are 0-based into ReferenceData.bldg_systems.
SYSTEM_ENABLEMENT = {
    "Villa": ([0, 1, 3, 4], 1),
    "Apartment": ([2, 3, 4], 2),
    "Hospital": ([1, 2, 4], 3),
    "Hotel": ([1, 2, 4], 3),
    "Office": ([1, 2, 3], 4),
}


def new_building_input(ref: ReferenceData) -> BuildingInput:
    bi = BuildingInput()
    d = ref.gui_defaults
    bi.txtBldgName = d.get("txtBldgName", "")
    bi.txtBldgAddress = d.get("txtBldgAddress", "")
    bi.cmbBldgType = d.get("cmbBldgType", ref.bldg_types[0].bldg_type if ref.bldg_types else "")
    bi.cmbBldgLocation = d.get("cmbBldgLocation", "TUNIS")
    bi.txtBldgNumFloor = int(float(d.get("txtBldgNumFloor", 1)))
    bi.txtBldgCondArea = float(d.get("txtBldgCondArea", 100))
    bi.cmbBldgShape = d.get("cmbBldgShape", "Rectangular")
    bi.txtBldgAzi = float(d.get("txtBldgAzi", 0))
    bi.txtFloorHeight = float(d.get("txtFloorHeight", 3))
    bi.txtLengX1 = float(d.get("txtLengX1", 10))
    bi.txtLengY1 = float(d.get("txtLengY1", 10))
    bi.txtLengX2 = float(d.get("txtLengX2", 0))
    bi.txtLengY2 = float(d.get("txtLengY2", 0))
    bi.txtLengX3 = float(d.get("txtLengX3", 0))
    bi.txtLengY3 = float(d.get("txtLengY3", 0))
    bi.cmbFirstFloorContact = d.get("cmbFirstFloorContact", "Ground")
    bi.rdbtnWinWwr = d.get("rdbtnGroupWinUnit", "WWR") == "WWR"
    bi.txtWinSouthOverhang = float(d.get("txtWinSouthOverhang", 0))
    bi.txtWinSouthFp = float(d.get("txtWinSouthFp", 0))
    bi.cmbHotWaterSystem = d.get("cmbHotWaterSystem", "")
    bi.txtHeatSetTemp = float(d.get("txtHeatSetTemp", 20))
    bi.txtCoolSetTemp = float(d.get("txtCoolSetTemp", 24))
    bi.txtCoolCOP = float(d.get("txtCoolCOP", 2.6))
    bi.txtHeatEff = float(d.get("txtHeatEff", 75))
    bi.txtSkyltType = d.get("txtSkyltType", "None")
    bi.txtSkyltCvr = float(d.get("txtSkyltCvr", 0))

    wall_names = list(ref.constructions_wall.keys())
    roof_names = list(ref.constructions_roof.keys())
    default_wall = wall_names[0] if wall_names else ""
    default_roof = roof_names[0] if roof_names else ""
    bi.cmbSouthWall = bi.cmbNorthWall = bi.cmbEastWall = bi.cmbWestWall = default_wall
    bi.cmbRoof = default_roof

    apply_building_type_defaults(bi, ref)
    return bi


def apply_building_type_defaults(bi: BuildingInput, ref: ReferenceData) -> None:
    """Refresh window-allocation and space-condition tables + HVAC system pick for bi.cmbBldgType.

    Mirrors GuiMain's cmbBldgType ActionListener: reloads tblWinType/tblSpaceCond from the DB
    for the new category and re-applies the system enablement/auto-select matrix.
    """
    type_row = ref.bldg_type_row(bi.cmbBldgType)
    if type_row is None:
        return
    cat = type_row.cat

    win_rows = ref.win_alloc_rows(cat)
    rows = [
        WindowAllocationRow(r.south_percent, r.north_percent, r.east_percent, r.west_percent, r.glass_type)
        for r in win_rows
    ]
    while len(rows) < 5:
        rows.append(WindowAllocationRow())
    bi.window_rows = rows[:5]

    space_rows = ref.space_cond_rows(cat)
    bi.space_rows = [
        SpaceConditionRow(r.area_type, r.percent_area, r.occupant, r.ventilation, r.lighting,
                           r.plug_load, r.cond_space == "yes")
        for r in space_rows
    ]

    enabled_idx, selected_idx = SYSTEM_ENABLEMENT.get(cat, (list(range(len(ref.bldg_systems))), 0))
    if ref.bldg_systems:
        idx = selected_idx if selected_idx < len(ref.bldg_systems) else 0
        bi.cmbBldgSystem = ref.bldg_systems[idx]


def populate_space_rows(bi: BuildingInput, ref: ReferenceData) -> None:
    """Refresh only the space-condition table from the DB for bi.cmbBldgType.

    Split out from apply_building_type_defaults() because this is also needed right after
    loading a saved project: tblSpaceCond is never persisted to the .tct file in the original
    app (see calc/bldg_info.py's module docstring), so an opened project must re-derive it here
    while leaving the file's own window_rows/wall selections untouched.
    """
    type_row = ref.bldg_type_row(bi.cmbBldgType)
    if type_row is None:
        return
    space_rows = ref.space_cond_rows(type_row.cat)
    bi.space_rows = [
        SpaceConditionRow(r.area_type, r.percent_area, r.occupant, r.ventilation, r.lighting,
                           r.plug_load, r.cond_space == "yes")
        for r in space_rows
    ]
