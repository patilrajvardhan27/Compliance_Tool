"""Load/save a TUNBEEC project (.tct) file -- Python port of GuiMain's btnOpen/setSave logic.

Schema confirmed against the real PROJECT/test1..5.tct sample files (db_inventory.md PART 2):
    User_Building          (GuiName, Value)                              -- one row per form field
    User_Construction_Wall (UserName, TYPE, ABSORPTANCE, ROUGHNESS, LAYERS, UVALUE)
    User_Construction_Roof (same columns)
    User_Layer_Wall        (UserName, Uvalue, MAT1..MAT7)
    User_Layer_Roof        (same columns)
    User_Material          (UserName, TYPE, THICKNESS, CONDUCTIVITY, DENSITY, SPECIFIC-HEAT, RESISTANCE)
    User_Glass             (UserName, UserType, TYPE, GLASS-CONDUCT, SHADING-COEF, VIS-TRANS)
    User_WinAllocation     (SouthPercent, NorthPercent, EastPercent, WestPercent, GlassType) -- fixed 5 rows
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from tunbeec.models import (
    BuildingInput,
    ConstructionEntry,
    GlassEntry,
    LayerEntry,
    MaterialEntry,
    WindowAllocationRow,
)

_BOOL_FIELDS = {"rdbtnWinWwr"}
_INT_FIELDS = {"txtBldgNumFloor"}
_FLOAT_FIELDS = {
    "txtBldgCondArea", "txtLengX1", "txtLengY1", "txtLengX2", "txtLengY2", "txtLengX3", "txtLengY3",
    "txtBldgAzi", "txtFloorHeight", "txtFloorArea", "txtWinSouthOverhang", "txtWinSouthFp",
    "txtHeatSetTemp", "txtCoolSetTemp", "txtSkyltCvr", "txtCoolCOP", "txtHeatEff",
}

_CONST_COLS = '"UserName", "TYPE", "ABSORPTANCE", "ROUGHNESS", "LAYERS", "UVALUE"'
_LAYER_COLS = '"UserName", "Uvalue", "MAT1", "MAT2", "MAT3", "MAT4", "MAT5", "MAT6", "MAT7"'
_MATERIAL_COLS = '"UserName", "TYPE", "THICKNESS", "CONDUCTIVITY", "DENSITY", "SPECIFIC-HEAT", "RESISTANCE"'
_GLASS_COLS = '"UserName", "UserType", "TYPE", "GLASS-CONDUCT", "SHADING-COEF", "VIS-TRANS"'
_WINALLOC_COLS = '"SouthPercent", "NorthPercent", "EastPercent", "WestPercent", "GlassType"'


def _coerce(name: str, value: str):
    if name in _BOOL_FIELDS:
        return value == "true"
    if name in _INT_FIELDS:
        return int(float(value))
    if name in _FLOAT_FIELDS:
        return float(value)
    return value


def load_project(path: Path) -> BuildingInput:
    conn = sqlite3.connect(f"file:{Path(path)}?mode=ro", uri=True)
    try:
        bi = BuildingInput()
        kv = {row[0]: row[1] for row in conn.execute("SELECT GuiName, Value FROM User_Building")}
        for name, value in kv.items():
            if value is None or not hasattr(bi, name):
                continue
            setattr(bi, name, _coerce(name, value))

        win_rows = conn.execute(f"SELECT {_WINALLOC_COLS} FROM User_WinAllocation").fetchall()
        rows = [
            WindowAllocationRow(south_percent=float(r[0] or 0), north_percent=float(r[1] or 0),
                                 east_percent=float(r[2] or 0), west_percent=float(r[3] or 0),
                                 glass_type=r[4] or "")
            for r in win_rows
        ]
        while len(rows) < 5:
            rows.append(WindowAllocationRow())
        bi.window_rows = rows[:5]

        for kind, target_attr in (("Wall", "user_constructions_wall"), ("Roof", "user_constructions_roof")):
            entries = []
            for r in conn.execute(f'SELECT {_CONST_COLS} FROM "User_Construction_{kind}"'):
                entries.append(ConstructionEntry(user_name=r[0], type=r[1], absorptance=float(r[2] or 0.6),
                                                  roughness=int(float(r[3] or 4)), layer_name=r[4] or "",
                                                  u_value=float(r[5]) if r[5] not in (None, "") else 0.0))
            setattr(bi, target_attr, entries)

        for kind, target_attr in (("Wall", "user_layers_wall"), ("Roof", "user_layers_roof")):
            entries = []
            for r in conn.execute(f'SELECT {_LAYER_COLS} FROM "User_Layer_{kind}"'):
                mats = [m for m in r[2:9] if m]
                entries.append(LayerEntry(user_name=r[0], materials=mats, u_value=float(r[1] or 0)))
            setattr(bi, target_attr, entries)

        mats = []
        for r in conn.execute(f'SELECT {_MATERIAL_COLS} FROM "User_Material"'):
            mats.append(MaterialEntry(
                user_name=r[0], type=r[1],
                thickness=float(r[2]) if r[2] not in (None, "") else None,
                conductivity=float(r[3]) if r[3] not in (None, "") else None,
                density=float(r[4]) if r[4] not in (None, "") else None,
                spec_heat=float(r[5]) if r[5] not in (None, "") else None,
                resistance=float(r[6] or 0),
            ))
        bi.user_materials = mats

        glasses = []
        for r in conn.execute(f'SELECT {_GLASS_COLS} FROM "User_Glass"'):
            glasses.append(GlassEntry(user_name=r[0], user_type=r[1], type=r[2],
                                       glass_conduct=float(r[3] or 0), sc=float(r[4] or 0), vt=float(r[5] or 0)))
        bi.user_glass = glasses

        return bi
    finally:
        conn.close()


def save_project(path: Path, bi: BuildingInput) -> None:
    path = Path(path)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("CREATE TABLE User_Building (GuiName, Value)")
        conn.execute(f'CREATE TABLE "User_Construction_Wall" ({_CONST_COLS})')
        conn.execute(f'CREATE TABLE "User_Construction_Roof" ({_CONST_COLS})')
        conn.execute(f'CREATE TABLE "User_Layer_Wall" ({_LAYER_COLS})')
        conn.execute(f'CREATE TABLE "User_Layer_Roof" ({_LAYER_COLS})')
        conn.execute(f'CREATE TABLE "User_Material" ({_MATERIAL_COLS})')
        conn.execute(f'CREATE TABLE "User_Glass" ({_GLASS_COLS})')
        conn.execute(f'CREATE TABLE "User_WinAllocation" ({_WINALLOC_COLS})')

        simple_fields = [
            "txtBldgName", "txtBldgAddress", "cmbBldgType", "cmbBldgLocation", "txtBldgNumFloor",
            "txtBldgCondArea", "cmbBldgShape", "txtBldgAzi", "txtFloorHeight", "txtFloorArea",
            "txtLengX1", "txtLengY1", "txtLengX2", "txtLengY2", "txtLengX3", "txtLengY3", "cmbSouthWall", "cmbNorthWall",
            "cmbEastWall", "cmbWestWall", "cmbRoof", "cmbFirstFloorContact", "rdbtnWinWwr",
            "txtWinSouthOverhang", "txtWinSouthFp", "cmbHotWaterSystem", "cmbBldgSystem",
            "txtHeatSetTemp", "txtCoolSetTemp", "txtSkyltType", "txtSkyltCvr",
            "txtCoolCOP", "txtHeatEff",
        ]
        for name in simple_fields:
            value = getattr(bi, name)
            if isinstance(value, bool):
                value = "true" if value else "false"
            conn.execute("INSERT INTO User_Building VALUES (?, ?)", (name, str(value)))

        for row in bi.window_rows[:5]:
            conn.execute(
                f"INSERT INTO User_WinAllocation VALUES (?, ?, ?, ?, ?)",
                (row.south_percent, row.north_percent, row.east_percent, row.west_percent, row.glass_type),
            )

        for kind, entries in (("Wall", bi.user_constructions_wall), ("Roof", bi.user_constructions_roof)):
            for c in entries:
                conn.execute(
                    f'INSERT INTO "User_Construction_{kind}" VALUES (?, ?, ?, ?, ?, ?)',
                    (c.user_name, c.type, c.absorptance, c.roughness, c.layer_name, c.u_value),
                )

        for kind, entries in (("Wall", bi.user_layers_wall), ("Roof", bi.user_layers_roof)):
            for l in entries:
                mats = (l.materials + [""] * 7)[:7]
                conn.execute(
                    f'INSERT INTO "User_Layer_{kind}" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (l.user_name, l.u_value, *mats),
                )

        for m in bi.user_materials:
            conn.execute(
                'INSERT INTO "User_Material" VALUES (?, ?, ?, ?, ?, ?, ?)',
                (m.user_name, m.type, m.thickness, m.conductivity, m.density, m.spec_heat, m.resistance),
            )

        for g in bi.user_glass:
            conn.execute(
                'INSERT INTO "User_Glass" VALUES (?, ?, ?, ?, ?, ?)',
                (g.user_name, g.user_type, g.type, g.glass_conduct, g.sc, g.vt),
            )

        conn.commit()
    finally:
        conn.close()
