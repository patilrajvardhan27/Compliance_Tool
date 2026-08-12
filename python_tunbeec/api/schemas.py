"""Pydantic schemas mirroring tunbeec/models.py field-for-field, plus response wrappers for the
calc-pipeline result dataclasses (PrescriptiveResult, PerformanceReport, ReferenceData snapshot).

Field names intentionally match the dataclasses in tunbeec/models.py verbatim (txtBldgName,
cmbBldgType, window_rows, ...) so the JSON payload is a 1:1 mirror of the desktop app's in-memory
BuildingInput -- easy to debug, easy to keep in sync as the Python domain model evolves.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class WindowAllocationRowSchema(BaseModel):
    south_percent: float = 0.0
    north_percent: float = 0.0
    east_percent: float = 0.0
    west_percent: float = 0.0
    glass_type: str = ""


class SpaceConditionRowSchema(BaseModel):
    area_type: str = ""
    percent_area: float = 0.0
    occupant: float = 0.0
    infiltration: float = 0.0
    lighting: float = 0.0
    plug_load: float = 0.0
    conditioned: bool = True


class MaterialEntrySchema(BaseModel):
    user_name: str = ""
    type: str = "PROPERTIES"
    thickness: float | None = None
    conductivity: float | None = None
    density: float | None = None
    spec_heat: float | None = None
    resistance: float = 0.0


class LayerEntrySchema(BaseModel):
    user_name: str = ""
    materials: list[str] = []
    u_value: float = 0.0


class ConstructionEntrySchema(BaseModel):
    user_name: str = ""
    type: str = "LAYERS"
    absorptance: float = 0.6
    roughness: int = 4
    layer_name: str = ""
    u_value: float = 0.5


class GlassEntrySchema(BaseModel):
    user_name: str = ""
    user_type: str = "GLASS_TYPE"
    type: str = "SHADING-COEF"
    glass_conduct: float = 0.0
    sc: float = 0.0
    vt: float = 0.0


class BuildingInputSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Tab 1 - General Information
    txtBldgName: str = ""
    txtBldgAddress: str = ""
    cmbBldgType: str = ""
    cmbBldgLocation: str = "TUNIS"
    txtBldgNumFloor: int = 1
    txtBldgCondArea: float = 100.0
    cmbBldgShape: str = "Rectangular"
    txtLengX1: float = 10.0
    txtLengY1: float = 10.0
    txtLengX2: float = 0.0
    txtLengY2: float = 0.0
    txtLengX3: float = 0.0
    txtLengY3: float = 0.0
    txtBldgAzi: float = 0.0
    txtFloorHeight: float = 3.0
    txtFloorArea: float = 0.0

    # Tab 2 - Envelope
    cmbSouthWall: str = ""
    cmbNorthWall: str = ""
    cmbEastWall: str = ""
    cmbWestWall: str = ""
    cmbRoof: str = ""
    cmbFirstFloorContact: str = "Ground"
    rdbtnWinWwr: bool = True
    window_rows: list[WindowAllocationRowSchema] = []
    txtWinSouthOverhang: float = 0.0
    txtWinSouthFp: float = 0.0
    txtSkyltType: str = "None"
    txtSkyltCvr: float = 0.0

    # Tab 3 - Spaces
    space_rows: list[SpaceConditionRowSchema] = []

    # Tab 4 - HVAC System
    cmbBldgSystem: str = ""
    txtHeatSetTemp: float = 20.0
    txtCoolSetTemp: float = 24.0
    txtCoolCOP: float = 2.6
    txtHeatEff: float = 75.0
    cmbHotWaterSystem: str = ""

    # User-defined library entries
    user_constructions_wall: list[ConstructionEntrySchema] = []
    user_constructions_roof: list[ConstructionEntrySchema] = []
    user_layers_wall: list[LayerEntrySchema] = []
    user_layers_roof: list[LayerEntrySchema] = []
    user_materials: list[MaterialEntrySchema] = []
    user_glass: list[GlassEntrySchema] = []


# -- reference data snapshot --------------------------------------------------------------------
class BldgTypeSchema(BaseModel):
    bldg_type: str
    cat: str
    use: str
    sector: str
    star: str


class ReferenceSnapshot(BaseModel):
    bldg_types: list[BldgTypeSchema]
    bldg_locations: list[str]
    bldg_shapes: dict[str, str]
    bldg_systems: list[str]
    gui_defaults: dict[str, str]
    constructions_wall: dict[str, ConstructionEntrySchema]
    constructions_roof: dict[str, ConstructionEntrySchema]
    layers_wall: dict[str, LayerEntrySchema]
    layers_roof: dict[str, LayerEntrySchema]
    materials: dict[str, MaterialEntrySchema]
    glass: dict[str, GlassEntrySchema]


# -- small calc request/response bodies ------------------------------------------------------
class FloorAreaRequest(BaseModel):
    shape: str
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    x3: float = 0.0
    y3: float = 0.0


class FloorAreaResponse(BaseModel):
    floor_area: float


class MaterialResistanceRequest(BaseModel):
    thickness: float
    conductivity: float


class MaterialResistanceResponse(BaseModel):
    resistance: float


class ConstructionUValueRequest(BaseModel):
    resistances: list[float]


class ConstructionUValueResponse(BaseModel):
    u_value: float


# -- prescriptive result ------------------------------------------------------------------------
class EnvelopeResultSchema(BaseModel):
    item: str
    unit: str
    comp_value_1: float
    comp_value_2: float
    bldg_value: float
    compliant: bool


class PrescriptiveResultSchema(BaseModel):
    climate: int
    bldg_zone: str
    x1: float
    x2: float
    grade: str
    code_thresholds: list[list[float]]
    ext_wall_u: float
    roof_u: float
    glass_weighted_u: float
    glass_weighted_sc: float
    rows: list[EnvelopeResultSchema]
    compliant: bool
    needs_performance_path: bool
    report_variant: int


# -- performance result --------------------------------------------------------------------------
class PerformanceRunRequest(BaseModel):
    project_name: str
    building_input: BuildingInputSchema


class ClassRowSchema(BaseModel):
    class_name: str
    class_value: float
    class_bldg: str = ""


class PerformanceReportSchema(BaseModel):
    bldg_name: str
    bldg_address: str
    bldg_type: str
    bldg_category: str
    bldg_sector: str
    bldg_star: str
    bldg_loc: str

    ext_wall_const_u: float
    ext_wall_const_south_u: float
    ext_wall_const_north_u: float
    ext_wall_const_east_u: float
    ext_wall_const_west_u: float
    roof_const_u: float
    glass_u: dict[int, float]
    glass_sc: dict[int, float]

    min_bec_th: float
    bldg_bec_th: float
    min_class: str
    bldg_class: str
    result: str

    h_load: float
    c_load: float
    a_load: float
    h_energy: float
    c_energy: float
    a_energy: float
    a_src_energy: float
    a_co2: float

    class_rows: list[ClassRowSchema] = []


class PerformanceRunResponse(BaseModel):
    status: str  # "ok" | "simulation_unavailable" | "simulation_failed"
    message: str = ""
    inp_path: str | None = None
    report: PerformanceReportSchema | None = None


# -- projects -----------------------------------------------------------------------------------
# The .tct file lives on the user's machine (browser file pickers), not on the server -- these
# requests only carry bytes through a stateless JSON<->SQLite conversion. "name" is used solely
# to name DOE-2.2's scratch .inp/.sim files in PROJECT_DIR, not to address stored files.
class SaveProjectRequest(BaseModel):
    name: str
    building_input: BuildingInputSchema
