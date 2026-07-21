"""Domain data model for a TUNBEEC project.

Field names mirror the original Swing component names (txtBldgName, cmbBldgType, ...) because
those exact strings are the keys persisted in the project .tct file's User_Building table
(see dao.GuiInitDao / GuiMain.setUserBldgKV_WinAllocation in the decompiled Java, and the
sample dump in the project's input.txt). Keeping the same keys means .tct files created by the
original Java desktop app and by this Python port stay interchangeable.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WindowAllocationRow:
    """One row of the 5-row window-allocation table (tblWinType in GuiMain)."""

    south_percent: float = 0.0
    north_percent: float = 0.0
    east_percent: float = 0.0
    west_percent: float = 0.0
    glass_type: str = ""


@dataclass
class SpaceConditionRow:
    """One row of the up-to-8-row space/zone table (tblSpaceCond in GuiMain)."""

    area_type: str = ""
    percent_area: float = 0.0
    occupant: float = 0.0     # m2/person
    infiltration: float = 0.0  # ACH
    lighting: float = 0.0      # W/m2
    plug_load: float = 0.0     # W/m2
    conditioned: bool = True   # True -> "Conditioned", False -> "Unconditioned"


@dataclass
class MaterialEntry:
    user_name: str = ""
    type: str = "PROPERTIES"  # "PROPERTIES" or "RESISTANCE"
    thickness: float | None = None       # m
    conductivity: float | None = None    # W/m.K
    density: float | None = None         # kg/m3
    spec_heat: float | None = None       # J/kg.K
    resistance: float = 0.0              # m2.K/W


@dataclass
class LayerEntry:
    """A named stack of up to 7 material layers (Wall or Roof)."""

    user_name: str = ""
    materials: list[str] = field(default_factory=list)  # ordered MaterialEntry.user_name references
    u_value: float = 0.0  # W/m2.K, = 1 / sum(material resistances)


@dataclass
class ConstructionEntry:
    """A named Wall or Roof construction: either a material LAYERS stack or a direct U-VALUE."""

    user_name: str = ""
    type: str = "LAYERS"  # "LAYERS" or "U-VALUE"
    absorptance: float = 0.6
    roughness: int = 4
    layer_name: str = ""    # used when type == "LAYERS"
    u_value: float = 0.5    # used when type == "U-VALUE"


@dataclass
class GlassEntry:
    user_name: str = ""
    user_type: str = "GLASS_TYPE"
    type: str = "SHADING-COEF"
    glass_conduct: float = 0.0  # W/m2.K
    sc: float = 0.0             # shading coefficient
    vt: float = 0.0             # visible transmittance


@dataclass
class BuildingInput:
    """Everything entered across the 4 GuiMain tabs, persisted to a project .tct file."""

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
    txtFloorArea: float = 0.0  # computed (vo.ShapeDimensionVo.calcFloorArea) but also persisted in User_Building

    # Tab 2 - Envelope
    cmbSouthWall: str = ""
    cmbNorthWall: str = ""
    cmbEastWall: str = ""
    cmbWestWall: str = ""
    cmbRoof: str = ""
    cmbFirstFloorContact: str = "Ground"
    rdbtnWinWwr: bool = True
    window_rows: list[WindowAllocationRow] = field(default_factory=lambda: [WindowAllocationRow() for _ in range(5)])
    txtWinSouthOverhang: float = 0.0
    txtWinSouthFp: float = 0.0
    txtSkyltType: str = "None"
    txtSkyltCvr: float = 0.0

    # Tab 3 - Spaces
    space_rows: list[SpaceConditionRow] = field(default_factory=list)
    cmbHotWaterSystem: str = ""

    # Tab 4 - HVAC System
    cmbBldgSystem: str = ""
    txtHeatSetTemp: float = 20.0
    txtCoolSetTemp: float = 24.0

    # User-defined library entries created in this project (GuiConst/GuiGlass/GuiMaterial "-Create-")
    user_constructions_wall: list[ConstructionEntry] = field(default_factory=list)
    user_constructions_roof: list[ConstructionEntry] = field(default_factory=list)
    user_layers_wall: list[LayerEntry] = field(default_factory=list)
    user_layers_roof: list[LayerEntry] = field(default_factory=list)
    user_materials: list[MaterialEntry] = field(default_factory=list)
    user_glass: list[GlassEntry] = field(default_factory=list)
