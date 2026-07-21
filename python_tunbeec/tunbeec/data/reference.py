"""Reference/library data loader -- Python port of dao.DbData + the individual dao.*TableDao classes.

Reads the shipped reference database (lib1/DefaultDB.tct) and exposes it as simple in-memory
lookups by name, merged with a project's own user-defined constructions/layers/materials/glass
(the equivalent of DbData.totConstTableWall etc., which merge library + user entries).

All UI-facing text in the reference DB (BldgType.Cat/BldgType, BldgShape, Bldg_System,
construction/material/glass names, category-suffixed table names like Office_AreaAllocation)
has been translated to English; BldgType.Cat now already matches the canonical English category
codes (Office/Hotel/Hospital/Apartment/Villa) used by the DOE-2.2 BDL-template tables (Inp_*),
so no separate French->English translation layer is needed anymore.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from tunbeec.models import ConstructionEntry, GlassEntry, LayerEntry, MaterialEntry


@dataclass
class BldgTypeRow:
    bldg_type: str   # cmbBldgType label, e.g. "Hotel, 3 Stars"
    cat: str         # e.g. "Hotel" -- used throughout the calc engine as bldgType
    use: str         # "Residential" | "Commercial"
    sector: str      # "Private" | "Public"
    star: str        # "" | "ThreeStar" | "FourStar" | "FiveStar"


@dataclass
class SpaceCondRowRef:
    area_type: str
    percent_area: float
    occupant: float
    ventilation: float
    lighting: float
    plug_load: float
    cond_space: str  # "yes" | "no"


@dataclass
class WinAllocRowRef:
    south_percent: float
    north_percent: float
    east_percent: float
    west_percent: float
    glass_type: str


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, params)
    return cur.fetchall()


def _float(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class ReferenceData:
    """Loaded once from lib1/DefaultDB.tct. Equivalent of DbData's static library-side state."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.bldg_types: list[BldgTypeRow] = []
        self.bldg_locations: list[str] = []                # BldgLoc names, for combobox population.
        # NOTE: the live reference DB's BldgLocation table carries no climate-zone column (confirmed
        # against lib1/DefaultDB_1.tct's schema) -- climate zone is instead determined the same way
        # method.Prescriptive.java does it, via the hardcoded constants.CLIMATE_LOCATIONS table.
        self.bldg_shapes: dict[str, str] = {}              # BldgShape (French label) -> Form (R/L/T/U/Hexagon/...)
        self.bldg_systems: list[str] = []
        self.gui_defaults: dict[str, str] = {}              # Bldg_GuiInit: GuiName -> Value

        self.constructions_wall: dict[str, ConstructionEntry] = {}
        self.constructions_roof: dict[str, ConstructionEntry] = {}
        self.layers_wall: dict[str, LayerEntry] = {}
        self.layers_roof: dict[str, LayerEntry] = {}
        self.materials: dict[str, MaterialEntry] = {}
        self.glass: dict[str, GlassEntry] = {}

        self._load()

    # -- loading -----------------------------------------------------------------
    def _load(self) -> None:
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        try:
            self._load_bldg_types(conn)
            self._load_locations(conn)
            self._load_shapes(conn)
            self._load_systems(conn)
            self._load_gui_defaults(conn)
            self._load_constructions(conn, "Wall")
            self._load_constructions(conn, "Roof")
            self._load_layers(conn, "Wall")
            self._load_layers(conn, "Roof")
            self._load_materials(conn)
            self._load_glass(conn)
        finally:
            conn.close()

    def _load_bldg_types(self, conn):
        for r in _rows(conn, "SELECT BldgType, Cat, Use, Sector, Star FROM BldgType"):
            self.bldg_types.append(BldgTypeRow(r["BldgType"], r["Cat"], r["Use"], r["Sector"], r["Star"] or ""))

    def _load_locations(self, conn):
        self.bldg_locations = [r["BldgLoc"] for r in _rows(conn, "SELECT BldgLoc FROM BldgLocation")]

    def _load_shapes(self, conn):
        for r in _rows(conn, "SELECT BldgShape, Form FROM BldgShape"):
            self.bldg_shapes[r["BldgShape"]] = r["Form"]

    def _load_systems(self, conn):
        self.bldg_systems = [r["SystemName"] for r in _rows(conn, "SELECT SystemName FROM Bldg_System")]

    def _load_gui_defaults(self, conn):
        for r in _rows(conn, "SELECT GuiName, Value FROM Bldg_GuiInit"):
            self.gui_defaults[r["GuiName"]] = r["Value"]

    def _load_constructions(self, conn, kind: str):
        table = f"Bldg_Construction_{kind}"
        target = self.constructions_wall if kind == "Wall" else self.constructions_roof
        for r in _rows(conn, f'SELECT UserName, TYPE, ABSORPTANCE, ROUGHNESS, LAYERS, UVALUE FROM "{table}"'):
            target[r["UserName"]] = ConstructionEntry(
                user_name=r["UserName"],
                type=r["TYPE"],
                absorptance=_float(r["ABSORPTANCE"], 0.6),
                roughness=int(_float(r["ROUGHNESS"], 4)),
                layer_name=r["LAYERS"] or "",
                u_value=_float(r["UVALUE"], 0.0),
            )

    def _load_layers(self, conn, kind: str):
        table = f"Bldg_Layer_{kind}"
        target = self.layers_wall if kind == "Wall" else self.layers_roof
        for r in _rows(conn, f'SELECT * FROM "{table}"'):
            mats = [r[f"MAT{i}"] for i in range(1, 8) if r[f"MAT{i}"]]
            target[r["UserName"]] = LayerEntry(user_name=r["UserName"], materials=mats, u_value=_float(r["Uvalue"], 0.0))

    def _load_materials(self, conn):
        for r in _rows(conn, 'SELECT * FROM "Bldg_Material"'):
            self.materials[r["UserName"]] = MaterialEntry(
                user_name=r["UserName"],
                type=r["TYPE"],
                thickness=_float(r["THICKNESS"]) if r["THICKNESS"] not in (None, "") else None,
                conductivity=_float(r["CONDUCTIVITY"]) if r["CONDUCTIVITY"] not in (None, "") else None,
                density=_float(r["DENSITY"]) if r["DENSITY"] not in (None, "") else None,
                spec_heat=_float(r["SPECIFIC-HEAT"]) if r["SPECIFIC-HEAT"] not in (None, "") else None,
                resistance=_float(r["RESISTANCE"], 0.0),
            )

    def _load_glass(self, conn):
        for r in _rows(conn, 'SELECT * FROM "Bldg_Glass"'):
            self.glass[r["UserName"]] = GlassEntry(
                user_name=r["UserName"],
                user_type=r["UserType"],
                type=r["TYPE"],
                glass_conduct=_float(r["GLASS-CONDUCT"]),
                sc=_float(r["SHADING-COEF"]),
                vt=_float(r["VIS-TRANS"]),
            )

    # -- category-scoped lookups (Bldg_System / *_AreaAllocation / *_WinAllocation) --------------
    def space_cond_rows(self, bldg_cat: str) -> list[SpaceCondRowRef]:
        """bldg_cat: 'Office' | 'Hotel' | 'Hospital' | 'Apartment' | 'Villa' (BldgType.Cat)."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        try:
            table = f"{bldg_cat}_AreaAllocation"
            out = []
            for r in _rows(conn, f'SELECT * FROM "{table}"'):
                out.append(SpaceCondRowRef(
                    area_type=r["AreaType"],
                    percent_area=_float(r["PercentArea"]),
                    occupant=_float(r["Occupant"]),
                    ventilation=_float(r["Ventilation"]),
                    lighting=_float(r["Lighting"]),
                    plug_load=_float(r["PlugLoad"]),
                    cond_space=r["CondSpace"],
                ))
            return out
        finally:
            conn.close()

    def win_alloc_rows(self, bldg_cat: str) -> list[WinAllocRowRef]:
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        try:
            table = f"{bldg_cat}_WinAllocation"
            out = []
            for r in _rows(conn, f'SELECT * FROM "{table}"'):
                out.append(WinAllocRowRef(
                    south_percent=_float(r["SouthPercent"]),
                    north_percent=_float(r["NorthPercent"]),
                    east_percent=_float(r["EastPercent"]),
                    west_percent=_float(r["WestPercent"]),
                    glass_type=r["GlassType"],
                ))
            return out
        finally:
            conn.close()

    def spacezone_kv(self, bldg_cat: str) -> dict[str, str]:
        """Bldg_SpaceZoneKV: Key -> per-category BDL schedule-name/value tokens for occupancy/
        lighting/infiltration schedules. Columns are Office/Hotel/Hospital/Apartment (no Villa
        -- method.PerformanceOld.readInpSpaceZone() skips this lookup entirely for Villa)."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        try:
            out = {}
            for r in _rows(conn, f'SELECT Key, "{bldg_cat}" FROM Bldg_SpaceZoneKV'):
                out[r["Key"]] = r[bldg_cat]
            return out
        finally:
            conn.close()

    def line_table(self, table_name: str) -> list[str]:
        """Generic reader for the 'Line'-per-row BDL-template tables (Inp_*, <Cat>_Sch)."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        try:
            return [r[0] for r in conn.execute(f'SELECT Line FROM "{table_name}"').fetchall()]
        finally:
            conn.close()

    # -- combined library + user (equivalent of DbData.find*) ------------------------------------
    def find_construction(self, kind: str, name: str, user_entries: dict[str, ConstructionEntry]) -> ConstructionEntry | None:
        lib = self.constructions_wall if kind == "Wall" else self.constructions_roof
        return user_entries.get(name) or lib.get(name)

    def find_layer(self, kind: str, name: str, user_entries: dict[str, LayerEntry]) -> LayerEntry | None:
        lib = self.layers_wall if kind == "Wall" else self.layers_roof
        return user_entries.get(name) or lib.get(name)

    def find_material(self, name: str, user_entries: dict[str, MaterialEntry]) -> MaterialEntry | None:
        return user_entries.get(name) or self.materials.get(name)

    def find_glass(self, name: str, user_entries: dict[str, GlassEntry]) -> GlassEntry | None:
        return user_entries.get(name) or self.glass.get(name)

    def bldg_type_row(self, bldg_type_label: str) -> BldgTypeRow | None:
        for row in self.bldg_types:
            if row.bldg_type == bldg_type_label:
                return row
        return None
