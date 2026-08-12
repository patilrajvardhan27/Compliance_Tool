"""DOE-2.2 performance-path BDL generation + engine invocation.

Python port of method/PerformanceOld.java's runPerformance() pipeline. The reference DB stores
BDL text fragments as literal lines (one row = one line, in the `Inp_*`/`<Cat>_Sch` tables); this
module pulls those out, substitutes in the building's actual values via the same plain
substring-replace mechanism as the original (`fillVariableToInp`), concatenates them in the same
fixed order, and writes a `.inp` file identical in spirit to the one the original app produced.

DOE-2.2 itself (`doe22/RUN22.exe`) is a bundled Windows Fortran binary -- this does not
reimplement the building-energy simulation, it shells out to the same binary the Java app used,
exactly like the original did (see run_doe22()).
"""
from __future__ import annotations

import math
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tunbeec import constants as C
from tunbeec.calc.bldg_info import BldgGeometry
from tunbeec.calc.envelope import resolve_construction_u, resolve_glass_props
from tunbeec.data.reference import ReferenceData
from tunbeec.models import BuildingInput

_FIRST_FLOOR_CONTACT_TOKENS = {
    "Ground": "Ground[GroundFloor]",
    "Conditioned Space": "Condition[ConditionFloor]",
    "Unconditioned Space": "Uncondition[UnconditionFloor]",
}

_SPACEZONE_KV_ATTR = {"Office": "office", "Hotel": "hotel", "Hospital": "hospital", "Apartment": "apartment"}

# method/PerformanceOld.java's own hardcoded VAVS fan schedule, appended after every category's
# DB-sourced <Cat>_Sch template lines (readInpBldgSch()) -- literal, not templated.
_VAVS_FAN_SCHEDULE_LINES = [
    '"Sys1 (VAVS) Fans D1-1" = DAY-SCHEDULE-PD',
    "   TYPE              = ON/OFF/FLAG",
    "   VALUES            = ( 0, &D, &D, &D, &D, &D, &D, 1, &D, &D, &D, &D, &D, &D,",
    "                        &D, &D, &D, &D, 0 )",
    "   ..",
    '"Sys1 (VAVS) Fans D1-2" = DAY-SCHEDULE-PD',
    "   TYPE              = ON/OFF/FLAG",
    "   VALUES            = ( 0 )",
    "   ..",
    '"Sys1 (VAVS) Fans W1"  = WEEK-SCHEDULE-PD',
    "   TYPE             = ON/OFF/FLAG",
    '   DAY-SCHEDULES    = ( "Sys1 (VAVS) Fans D1-1", &D, &D, &D, &D,',
    '                        "Sys1 (VAVS) Fans D1-2" )',
    "   ..",
    '"Sys1 (VAVS) Fan Sch"  = SCHEDULE-PD',
    "   TYPE             = ON/OFF/FLAG",
    "   MONTH            = ( 12 )",
    "   DAY              = ( 31 )",
    '   WEEK-SCHEDULES   = ( "Sys1 (VAVS) Fans W1" )',
    "   ..",
]

_SYSTEM_NAME_TO_LIST_KEY = {
    "Packaged Variable Air Volume System": "pvavs",
    "Split System with Baseboard": "split",
    "Residential System": "residential",
    "Fan Coil System": "fcu",
    "Central Variable Air Volume System": "vav",
}
# These 3 (near-identical, non-accented) strings gate whether the Chw pump/loop/chiller blocks
# are injected. Reproduced verbatim from PerformanceOld.java:906 -- note the source itself uses
# "Systeme" without accents there (unlike the accented comparisons above), which the earlier
# decompiled-code review flagged as a possible latent inconsistency in the original app; kept
# as-is rather than "fixed" so this port's behavior matches the original bytecode exactly.
_NO_CHW_SYSTEMS = {
    "Systeme Monobloc Volume d’Air Variable",
    "Systeme Monozone a Detente Direct avec Plinthes",
    "Systeme Residentiel ",
}


@dataclass
class AreaResult:
    one_floor_area_si: float
    one_floor_area_ip: float
    total_area_si: float
    total_area_ip: float
    cond_area_si: float
    cond_area_ip: float
    vf: float  # villa template scale factor


@dataclass
class EnvelopeInfo:
    """Formatted %.2f envelope U-value strings for the report (Report.fillGeneralData)."""
    ext_wall_u: float
    ext_wall_u_south: float
    ext_wall_u_north: float
    ext_wall_u_east: float
    ext_wall_u_west: float
    roof_u: float
    glass_u: dict[int, float] = field(default_factory=dict)   # 1..5 -> U
    glass_sc: dict[int, float] = field(default_factory=dict)  # 1..5 -> SC


def calc_area(bi: BuildingInput, form: str) -> AreaResult:
    x1, y1, x2, y2, x3, y3 = bi.txtLengX1, bi.txtLengY1, bi.txtLengX2, bi.txtLengY2, bi.txtLengX3, bi.txtLengY3
    if form == "R":
        one_floor = x1 * y1
    elif form == "L":
        one_floor = x1 * y1 - (x1 - x2) * (y1 - y2)
    elif form == "T":
        one_floor = x1 * y1 - x2 * y2 - (x1 - x2 - x3) * y2
    elif form == "U":
        if y1 >= y2:
            large_y, small_y, small_x = y1, y2, x3
        else:
            large_y, small_y, small_x = y2, y1, x2
        one_floor = x1 * large_y - (x1 - x2 - x3) * (large_y - y3) - small_x * (large_y - small_y)
    else:
        raise ValueError(f"Unknown structural form: {form!r}")

    total_area = one_floor * bi.txtBldgNumFloor
    cond_area = total_area * bi.txtBldgCondArea / 100.0
    one_floor_ip = one_floor * C.M2_TO_FT2
    vf = math.sqrt(one_floor_ip / C.VILLA_TEMPLATE_ONE_FLOOR_AREA_FT2)
    return AreaResult(
        one_floor_area_si=one_floor, one_floor_area_ip=one_floor_ip,
        total_area_si=total_area, total_area_ip=total_area * C.M2_TO_FT2,
        cond_area_si=cond_area, cond_area_ip=cond_area * C.M2_TO_FT2, vf=vf,
    )


def resolve_envelope_info(ref: ReferenceData, bi: BuildingInput, geo: BldgGeometry) -> EnvelopeInfo:
    wall_u = {
        "S": resolve_construction_u(ref, bi, "Wall", bi.cmbSouthWall),
        "N": resolve_construction_u(ref, bi, "Wall", bi.cmbNorthWall),
        "E": resolve_construction_u(ref, bi, "Wall", bi.cmbEastWall),
        "W": resolve_construction_u(ref, bi, "Wall", bi.cmbWestWall),
    }
    areas = {"S": geo.south.area, "N": geo.north.area, "E": geo.east.area, "W": geo.west.area}
    total_wall_area = sum(areas.values())
    ext_wall_u = sum(wall_u[d] * areas[d] for d in "SNEW") / total_wall_area
    roof_u = resolve_construction_u(ref, bi, "Roof", bi.cmbRoof)
    glass_props = resolve_glass_props(ref, bi)
    glass_u, glass_sc = {}, {}
    for idx, row in enumerate(bi.window_rows, start=1):
        if row.glass_type in glass_props:
            glass_u[idx], glass_sc[idx], _ = glass_props[row.glass_type]
    return EnvelopeInfo(ext_wall_u, wall_u["S"], wall_u["N"], wall_u["E"], wall_u["W"], roof_u, glass_u, glass_sc)


def _weighted_orientation(geo: BldgGeometry, glass_props: dict[str, tuple[float, float, float]], orientation: str):
    """glassWeightedU/SC/VT{South,North,East,West} -- area-weighted across the 5 window rows for one orientation."""
    num_u = num_sc = num_vt = den = 0.0
    for row, ws in zip(_window_rows_glass_types(geo), geo.windows):
        area = getattr(ws, f"{orientation}_area")
        if area <= 0 or row not in glass_props:
            continue
        u, sc, vt = glass_props[row]
        num_u += area * u
        num_sc += area * sc
        num_vt += area * vt
        den += area
    if den == 0:
        return 0.0, 0.0, 0.0
    return num_u / den, num_sc / den, num_vt / den


def _window_rows_glass_types(geo: BldgGeometry):
    return [w.glass_type for w in geo.windows]


def first_floor_contact_token(cmb_value: str) -> str:
    if cmb_value not in _FIRST_FLOOR_CONTACT_TOKENS:
        raise ValueError(f"Unknown first-floor contact: {cmb_value!r}")
    return _FIRST_FLOOR_CONTACT_TOKENS[cmb_value]


def build_doe22_kv(bi: BuildingInput, geo: BldgGeometry, area: AreaResult, current_year: int) -> dict[str, str]:
    """Ordered substitution-token dict, matching setDoe22KV()+calcArea()'s key insertion order.

    Order matters: fillVariableToInp() applies these as plain (non-regex) substring replaces in
    insertion order, so a shorter key inserted before a longer one that contains it as a substring
    would corrupt the longer key's own replacement text. Preserve the original ordering exactly.
    """
    kv: dict[str, str] = {}
    m = C.M_TO_FT
    x1, y1, x2, y2, x3, y3 = bi.txtLengX1 * m, bi.txtLengY1 * m, bi.txtLengX2 * m, bi.txtLengY2 * m, bi.txtLengX3 * m, bi.txtLengY3 * m
    ceiling_height = bi.txtFloorHeight * m
    frame_width = 0.0

    kv["CurrYear"] = str(current_year)
    kv["BldgAzi"] = str(bi.txtBldgAzi)
    kv["southWallConst"] = bi.cmbSouthWall
    kv["northWallConst"] = bi.cmbNorthWall
    kv["eastWallConst"] = bi.cmbEastWall
    kv["westWallConst"] = bi.cmbWestWall
    kv["roofConst"] = bi.cmbRoof
    kv["FirstFloorContact"] = first_floor_contact_token(bi.cmbFirstFloorContact)
    kv["lengX1"] = str(x1)
    kv["lengY1"] = str(y1)
    kv["lengX2"] = str(x2)
    kv["lengY2"] = str(y2)
    kv["lengX3"] = str(x3)
    kv["lengY3"] = str(y3)
    kv["FloorHeight"] = str(ceiling_height)
    kv["CeilingHeight"] = str(ceiling_height)
    kv["FloorMulti2ndFloor"] = str(bi.txtBldgNumFloor - 2.0) if bi.txtBldgNumFloor >= 3 else "1"
    kv["FloorZpos2ndFloor"] = str(1.0 * ceiling_height)
    kv["FloorZpos3rdFloor"] = str((bi.txtBldgNumFloor - 1.0) * ceiling_height)
    kv["FrameWidth"] = str(frame_width)

    from tunbeec.calc.bldg_element import calc_gap
    gap = calc_gap(geo.bldg_shape_form, bi.txtBldgCondArea / 100.0, x1, y1, x2, y2, x3, y3)
    kv["gap"] = str(gap)
    kv["LengX1-Gap"] = str(x1 - gap)
    kv["LengY1-Gap"] = str(y1 - gap)
    kv["LengX2-Gap"] = str(x2 - gap)
    kv["LengY2-Gap"] = str(y2 - gap)
    kv["LengY2+Gap"] = str(y2 + gap)
    kv["LengX3-Gap"] = str(x3 - gap)
    kv["LengX1-2Gap"] = str(x1 - 2.0 * gap)
    kv["LengY1-2Gap"] = str(y1 - 2.0 * gap)
    kv["LengX2-2Gap"] = str(x2 - 2.0 * gap)
    kv["LengX2+2Gap"] = str(x2 + 2.0 * gap)
    kv["LengY2-2Gap"] = str(y2 - 2.0 * gap)
    kv["LengY3-2Gap"] = str(y3 - 2.0 * gap)
    kv["LengX1-LengX2"] = str(x1 - x2)
    kv["LengX1-LengX3"] = str(x1 - x3)
    kv["LX1-LX2-LX3"] = str(x1 - x2 - x3)
    kv["LX1-LX2-LLX3+Gp"] = str(x1 - x2 - x3 + gap)
    kv["LX1-LX2+Gp"] = str(x1 - x2 + gap)
    kv["LengY1-LengY2"] = str(y1 - y2)
    kv["LY1-LY2-Gp"] = str(y1 - y2 - gap)
    kv["LY1-LY2-2Gp"] = str(y1 - y2 - 2.0 * gap)
    kv["LengY1-LengY3"] = str(y1 - y3)
    kv["LY1-LY3-Gp"] = str(y1 - y3 - gap)
    kv["LY1-LY3-2Gp"] = str(y1 - y3 - 2.0 * gap)
    kv["LengX2+LengX3"] = str(x2 + x3)
    kv["LX2+LX3-2Gp"] = str(x2 + x3 - 2.0 * gap)
    kv["LengY2-LengY3"] = str(y2 - y3)
    kv["LY2-LY3+Gp"] = str(y2 - y3 + gap)
    kv["MinusGap"] = str(-1.0 * gap)

    kv["South1"] = str(geo.south.width * m * C.SOUTH_WALL_RATIO_1_VILLA)
    kv["South2"] = str(geo.south.width * m * C.SOUTH_WALL_RATIO_2_VILLA)
    kv["South3"] = str(geo.south.width * m * C.SOUTH_WALL_RATIO_3_VILLA)
    kv["North1"] = str(geo.north.width * m * C.NORTH_WALL_RATIO_1_VILLA)
    kv["North2"] = str(geo.north.width * m * C.NORTH_WALL_RATIO_2_VILLA)
    kv["North3"] = str(geo.north.width * m * C.NORTH_WALL_RATIO_3_VILLA)
    kv["East1"] = str(geo.east.width * m * C.EAST_WALL_RATIO_1_VILLA)
    kv["East2"] = str(geo.east.width * m * C.EAST_WALL_RATIO_2_VILLA)
    kv["East3"] = str(geo.east.width * m * C.EAST_WALL_RATIO_3_VILLA)
    kv["West1"] = str(geo.west.width * m * C.WEST_WALL_RATIO_1_VILLA)
    kv["West2"] = str(geo.west.width * m * C.WEST_WALL_RATIO_2_VILLA)
    kv["West3"] = str(geo.west.width * m * C.WEST_WALL_RATIO_3_VILLA)
    kv["West4"] = str(geo.west.width * m * C.WEST_WALL_RATIO_4_VILLA)

    kv["EscX"] = str(12.5 * area.vf)
    kv["EscY"] = str(6.4 * area.vf)
    return kv


def user_material_lines(bi: BuildingInput) -> list[str]:
    lines = []
    for mat in bi.user_materials:
        lines.append(f'"{mat.user_name}" = MATERIAL')
        lines.append(f"   TYPE            = {mat.type}")
        lines.append(f"   THICKNESS       = {mat.thickness}")
        lines.append(f"   CONDUCTIVITY    = {mat.conductivity * C.CONDUCTIVITY_SI_TO_IP}")
        lines.append(f"   DENSITY         = {mat.density * C.DENSITY_SI_TO_IP}")
        lines.append(f"   SPECIFIC-HEAT   = {mat.spec_heat * C.SPEC_HEAT_SI_TO_IP}")
        lines.append("   ..")
    return lines


def user_layer_lines(bi: BuildingInput, kind: str) -> list[str]:
    entries = bi.user_layers_wall if kind == "Wall" else bi.user_layers_roof
    lines = []
    for layer in entries:
        lines.append(f'"{layer.user_name}" = LAYERS')
        lines.append("   MATERIAL    = (")
        for i, mat_name in enumerate(m for m in layer.materials if m):
            prefix = "           " if i == 0 else "          ,"
            lines.append(f'{prefix}"{mat_name}"')
        lines.append("          )")
        lines.append("   ..")
    return lines


def user_construction_lines(bi: BuildingInput, kind: str) -> list[str]:
    entries = bi.user_constructions_wall if kind == "Wall" else bi.user_constructions_roof
    lines = []
    for c in entries:
        lines.append(f'"{c.user_name}" = CONSTRUCTION')
        lines.append(f"   TYPE            = {c.type}")
        if c.type == "LAYERS":
            lines.append(f'   LAYERS          = "{c.layer_name}"')
        elif c.type == "U-VALUE":
            lines.append(f"   U-VALUE         = {c.u_value * C.HEAT_RATE_SI_TO_IP}")
        lines.append(f"   ABSORPTANCE     = {c.absorptance}")
        lines.append(f"   ROUGHNESS       = {c.roughness}")
        lines.append("   ..")
    return lines


def bldg_glass_lines(ref: ReferenceData) -> list[str]:
    lines = ["$ ---------------------------------------------------------",
             "$            Default  Glass Type                           ",
             "$ ---------------------------------------------------------"]
    for glass in ref.glass.values():
        lines.append(f'"{glass.user_name}" = GLASS-TYPE')
        lines.append(f"   TYPE            = {glass.type}")
        lines.append(f"   SHADING-COEF    = {glass.sc}")
        lines.append(f"   GLASS-CONDUCT   = {glass.glass_conduct * C.CONDUCTIVITY_SI_TO_IP}")
        lines.append(f"   VIS-TRANS       = {glass.vt}")
        lines.append("   ..")
    return lines


def user_glass_lines(bi: BuildingInput) -> list[str]:
    lines = ["$ ---------------------------------------------------------",
             "$             User Glass Type                              ",
             "$ ---------------------------------------------------------"]
    for glass in bi.user_glass:
        lines.append(f'"{glass.user_name}" = GLASS-TYPE')
        lines.append(f"   TYPE            = {glass.type}")
        lines.append(f"   SHADING-COEF    = {glass.sc}")
        lines.append(f"   GLASS-CONDUCT   = {glass.glass_conduct * C.CONDUCTIVITY_SI_TO_IP}")
        lines.append(f"   VIS-TRANS       = {glass.vt}")
        lines.append("   ..")
    return lines


def combined_glass_lines(geo: BldgGeometry, glass_props: dict[str, tuple[float, float, float]]) -> list[str]:
    lines = ["$ ---------------------------------------------------------",
              "$             Combined Glass Type                          ",
              "$ ---------------------------------------------------------"]
    for orientation, label in (("south", "South"), ("north", "North"), ("east", "East"), ("west", "West")):
        total_area = sum(getattr(w, f"{orientation}_area") for w in geo.windows)
        if total_area <= 0:
            continue
        u, sc, vt = _weighted_orientation(geo, glass_props, orientation)
        lines.append(f'"Combined {label} Glass" = GLASS-TYPE')
        lines.append("   TYPE            = SHADING-COEF")
        lines.append(f"   SHADING-COEF    = {sc}")
        lines.append(f"   GLASS-CONDUCT   = {u * C.CONDUCTIVITY_SI_TO_IP}")
        lines.append(f"   VIS-TRANS       = {vt}")
        lines.append("   ..")
    return lines


def inp_bldg_sch_lines(ref: ReferenceData, bldg_type_cat: str) -> list[str]:
    return ref.line_table(f"{bldg_type_cat}_Sch") + _VAVS_FAN_SCHEDULE_LINES


def inp_polygon_lines(ref: ReferenceData, bi: BuildingInput, geo: BldgGeometry, area: AreaResult) -> list[str]:
    if geo.bldg_type_cat == "Villa":
        header = ["$ ---------------------------------------------------------",
                   "$              Polygons                                    ",
                   "$ ---------------------------------------------------------"]
        return header + _villa_polygon_lines(area.vf)
    num_floor = str(min(bi.txtBldgNumFloor, 3))
    table = f"Inp_Polygons_{geo.bldg_shape_form}{num_floor}"
    return ref.line_table(table)


def inp_space_zone_lines(ref: ReferenceData, bi: BuildingInput, geo: BldgGeometry, kv: dict[str, str]) -> list[str]:
    bldg_type_cat = geo.bldg_type_cat
    if bldg_type_cat != "Villa":
        bldg_type_cat_en = bldg_type_cat
        attr = _SPACEZONE_KV_ATTR[bldg_type_cat]
        conn_table = "Bldg_SpaceZoneKV"
        # Bldg_SpaceZoneKV columns: Key, Office, Hotel, Hospital, Apartment (no Villa column).
        for key, value in ref.spacezone_kv(bldg_type_cat).items():
            kv[key] = value
    else:
        bldg_type_cat_en = "Villa"

    kv["condAreaPerPerson"] = str(geo.cond_space.occupant * C.M2_TO_FT2)
    kv["condAirChangePerHour"] = str(geo.cond_space.infiltration)
    kv["condLightingLoad"] = str(geo.cond_space.lighting / C.M2_TO_FT2)
    kv["condEquipLoad"] = str(geo.cond_space.plug_load / C.M2_TO_FT2)
    kv["unAreaPerPerson"] = str(geo.uncond_space.occupant * C.M2_TO_FT2)
    kv["unAirChangePerHour"] = str(geo.uncond_space.infiltration)
    kv["unLightingLoad"] = str(geo.uncond_space.lighting / C.M2_TO_FT2)
    kv["unEquipLoad"] = str(geo.uncond_space.plug_load / C.M2_TO_FT2)

    num_floor = "3" if bi.txtBldgNumFloor > 3 else str(bi.txtBldgNumFloor)
    if bldg_type_cat == "Villa":
        table = f"Inp_VillaR{num_floor}"
    else:
        table = f"Inp_{bldg_type_cat_en}{geo.bldg_shape_form}{num_floor}"

    if bi.cmbHotWaterSystem == "Tankless Electric DHW System":
        kv["fuelType"] = "ELEC"
    elif bi.cmbHotWaterSystem == "Tank Gas-fired DHW System":
        kv["fuelType"] = "GAS"
    kv["designHeatT"] = str(1.8 * bi.txtHeatSetTemp + 32.0)
    kv["designCoolT"] = str(1.8 * bi.txtCoolSetTemp + 32.0)

    return ref.line_table(table)


def _villa_polygon_lines(vf: float) -> list[str]:
    """Verbatim port of PerformanceOld.addVillaPolygon() -- a hardcoded villa template geometry
    scaled by vf (the sqrt-area ratio to the reference 794.6 ft2 villa template)."""
    def v(x, y):
        return f"( {x * vf}, {y * vf} )"

    def poly(name, verts):
        out = [f'"{name}" =  POLYGON']
        for i, (x, y) in enumerate(verts, start=1):
            out.append(f"  V{i}               = {v(x, y)}")
        out.append("  ..")
        return out

    lines = []
    lines += poly("Floor Polygon", [
        (0.0, 0.0), (12.5, 0.0), (12.5, 6.4), (20.7, 6.4), (20.7, 0.0), (34.7, 0.0),
        (34.7, 14.0), (34.7, 26.5), (20.7, 26.5), (20.7, 23.0), (12.5, 23.0), (0.0, 23.0),
    ])
    lines += poly("Space Polygon 1", [(0.0, 0.0), (3.5, 0.0), (12.5, 0.0), (12.5, 14.0), (0.0, 14.0)])
    lines += poly("Space Polygon 2", [(0.0, 0.0), (8.2, 0.0), (8.2, 9.0), (0.0, 9.0)])
    lines += poly("Space Polygon 3", [(0.0, 0.0), (12.5, 0.0), (12.5, 13.0), (0.0, 13.0), (0.0, 9.0)])
    lines += poly("Space Polygon 4", [(0.0, 0.0), (6.4, 0.0), (6.4, 14.0), (-7.6, 14.0), (-7.6, 0.0)])
    lines += poly("Space Polygon 5", [(0.0, 0.0), (3.6, 0.0), (3.6, 12.5), (-6.4, 12.5), (-6.4, 0.0)])
    lines += poly("Space Polygon 6", [(0.0, 0.0), (8.2, 0.0), (8.2, 7.6), (0.0, 7.6)])
    lines += poly("Space Polygon 1 - SMirro", [(0.0, 0.0), (14.0, 0.0), (14.0, 12.5), (0.0, 12.5), (0.0, 3.5)])
    lines += poly("Space Polygon 2 - SMirro", [(0.0, 0.0), (9.0, 0.0), (9.0, 8.2), (0.0, 8.2)])
    lines += poly("Space Polygon 3 - SMirro", [(0.0, 0.0), (9.0, 0.0), (13.0, 0.0), (13.0, 12.5), (0.0, 12.5)])
    lines += poly("Space Polygon 4 - SMirro", [(0.0, 0.0), (0.0, -7.6), (14.0, -7.6), (14.0, 6.4), (0.0, 6.4)])
    lines += poly("Space Polygon 5 - SMirro", [(0.0, 0.0), (0.0, -6.4), (12.5, -6.4), (12.5, 3.6), (0.0, 3.6)])
    lines += poly("Space Polygon 6 - SMirro", [(0.0, 0.0), (7.6, 0.0), (7.6, 8.2), (0.0, 8.2)])
    return lines


def fill_variables(lines: list[str], kv: dict[str, str]) -> list[str]:
    """Plain substring replace of every kv key, in insertion order -- fillVariableToInp()."""
    out = list(lines)
    for key, value in kv.items():
        out = [line.replace(key, value) for line in out]
    return out


def _win_wall_width(tag: str, bi: BuildingInput, geo: BldgGeometry) -> float:
    m = C.M_TO_FT
    x1, x2, x3 = bi.txtLengX1 * m, bi.txtLengX2 * m, bi.txtLengX3 * m
    y1, y2, y3 = bi.txtLengY1 * m, bi.txtLengY2 * m, bi.txtLengY3 * m
    simple = {
        "X1": x1, "X1-X2": x1 - x2, "X1-X2-X3": x1 - x2 - x3, "Y1": y1, "Y1-Y2": y1 - y2,
        "Y1-Y3": y1 - y3, "X2": x2, "Y2": y2, "Y2-Y3": y2 - y3, "X3": x3, "Y3": y3,
    }
    if tag in simple:
        return simple[tag]
    villa = {
        "south1": (geo.south.width, C.SOUTH_WALL_RATIO_1_VILLA), "south2": (geo.south.width, C.SOUTH_WALL_RATIO_2_VILLA),
        "south3": (geo.south.width, C.SOUTH_WALL_RATIO_3_VILLA), "north1": (geo.north.width, C.NORTH_WALL_RATIO_1_VILLA),
        "north2": (geo.north.width, C.NORTH_WALL_RATIO_2_VILLA), "north3": (geo.north.width, C.NORTH_WALL_RATIO_3_VILLA),
        "east1": (geo.east.width, C.EAST_WALL_RATIO_1_VILLA), "east2": (geo.east.width, C.EAST_WALL_RATIO_2_VILLA),
        "east3": (geo.east.width, C.EAST_WALL_RATIO_3_VILLA), "west1": (geo.west.width, C.WEST_WALL_RATIO_1_VILLA),
        "west2": (geo.west.width, C.WEST_WALL_RATIO_2_VILLA), "west3": (geo.west.width, C.WEST_WALL_RATIO_3_VILLA),
        "west4": (geo.west.width, C.WEST_WALL_RATIO_4_VILLA),
    }
    width, ratio = villa[tag]
    return width * m * ratio


def _win_block(win_name: str, wall_width: float, ceiling_height: float, glass_name: str, wwr_tot: float,
               overhang_depth: float) -> list[str]:
    ceiling_under_height = C.FT_TO_M * 0.25 * C.M_TO_FT  # sillHeightDbl/ceilingUnderHeightDbl in ft (already *mTOft upstream)
    sill_height = ceiling_under_height
    frame_width = 0.0
    win_height = ceiling_height - ceiling_under_height - sill_height
    win_width = wall_width * ceiling_height * (wwr_tot / 100.0) / win_height if win_height else 0.0
    win_xpos = 0.5 * (wall_width - win_width)
    win_ypos = sill_height
    glass_height = win_height - 2.0 * frame_width
    glass_width = win_width - 2.0 * frame_width
    return [
        f'"{win_name}" = WINDOW',
        f'   GLASS-TYPE    = "{glass_name}"',
        "   MULTIPLIER    = 1.0",
        f"   FRAME-WIDTH   = {frame_width}",
        f"   X             = {win_xpos}",
        f"   Y             = {win_ypos}",
        f"   HEIGHT        = {glass_height}",
        f"   WIDTH         = {glass_width}",
        f"   OVERHANG-D    = {overhang_depth}",
        "   FRAME-CONDUCT = 3.079",
        "   ..",
    ]


def build_inp_lines(bi: BuildingInput, ref: ReferenceData, geo: BldgGeometry, kv: dict[str, str],
                     template_lists: dict[str, list[str]]) -> list[str]:
    """writeInp(): concatenate the filled-in template lists, then resolve the `$ add ...` markers."""
    concatenated: list[str] = []
    for key in (
        "input", "bldg_mat", "bldg_layer", "bldg_const", "user_mat", "user_layer_wall", "user_layer_roof",
        "user_const_wall", "user_const_roof", "bldg_glass", "user_glass", "combined_glass",
        "bldg_sch", "polygon", "space_zone", "utility_output",
    ):
        concatenated.extend(template_lists.get(key, []))

    ceiling_height = bi.txtFloorHeight * C.M_TO_FT
    glass_props = resolve_glass_props(ref, bi)
    out: list[str] = []
    for line in concatenated:
        add_flag = True
        if "$ add, Win" in line:
            add_flag = False
            tmp = line.replace(" ", "").replace("$", "")
            parts = tmp.split(",")
            if parts[1] == "Win":
                orientation = parts[3]
                wall_width = _win_wall_width(parts[4], bi, geo)
                win_name = f"{parts[2]} {parts[3]} Window"
                wwr_tot = sum(getattr(w, f"{orientation.lower()}_wwr") for w in geo.windows)
                out.extend(_win_block(
                    win_name, wall_width, ceiling_height, f"Combined {orientation} Glass", wwr_tot,
                    bi.txtWinSouthOverhang * C.M_TO_FT,
                ))
        if bi.cmbBldgSystem not in _NO_CHW_SYSTEMS:
            # newInpChwPumpList/ChwLoopList/ChillerList are never populated in the original app either
            # (no read*() method builds them) -- these markers are always dropped as a no-op, matching
            # the original's actual (if likely unintended) behavior.
            if "$ add ChwPump" in line or "$ add ChwLoop" in line or "$ add Chiller" in line:
                add_flag = False
        if "$ add system1" in line or "$ add system2" in line or "$ add system3" in line:
            # newInp{Pvavs,Split,Residential,Fcu,Vav}SystemList are likewise never populated anywhere
            # in the decompiled original -- these markers are always dropped as a no-op there too.
            add_flag = False
        if add_flag:
            out.append(line)
    return out


# The BDL templates hardcode every system/plant efficiency: COOLING-EIR and the chiller
# ELEC-INPUT-RATIO are always 0.3846 (= COP 2.6), HEAT-INPUT-RATIO / FURNACE-HIR are 1.3333
# (= 75% efficiency; the villa boiler alone uses 0.3). The GUI now exposes those as inputs
# (txtCoolCOP / txtHeatEff), applied here as a value rewrite on the generated lines.
_COOL_EIR_RE = re.compile(r"^(\s*(?:COOLING-EIR|ELEC-INPUT-RATIO)\s*=\s*)[0-9.]+(\s*)$")
_HEAT_HIR_RE = re.compile(r"^(\s*(?:HEAT-INPUT-RATIO|FURNACE-HIR)\s*=\s*)[0-9.]+(\s*)$")

_DEFAULT_COOL_COP = 2.6
_DEFAULT_HEAT_EFF = 75.0


def apply_hvac_efficiency(lines: list[str], cool_cop: float, heat_eff_pct: float) -> list[str]:
    """Rewrite the hardcoded template efficiencies with the user's HVAC-tab values.

    When a value is still at its default (COP 2.6 / 75%), the corresponding lines are left
    byte-identical to the DB templates (including the villa boiler's special 0.3 HIR) so the
    generated .inp matches the original app's output exactly in the untouched case.
    """
    rewrite_cool = cool_cop > 0 and abs(cool_cop - _DEFAULT_COOL_COP) > 1e-9
    rewrite_heat = heat_eff_pct > 0 and abs(heat_eff_pct - _DEFAULT_HEAT_EFF) > 1e-9
    if not rewrite_cool and not rewrite_heat:
        return lines
    eir = f"{1.0 / cool_cop:.5f}"
    hir = f"{100.0 / heat_eff_pct:.5f}"
    out = []
    for line in lines:
        if rewrite_cool:
            m = _COOL_EIR_RE.match(line)
            if m:
                out.append(f"{m.group(1)}{eir}")
                continue
        if rewrite_heat:
            m = _HEAT_HIR_RE.match(line)
            if m:
                out.append(f"{m.group(1)}{hir}")
                continue
        out.append(line)
    return out


_BDL_LINE_LIMIT = 80  # DOEBDL.EXE silently truncates any physical line past column 80
                       # (a legacy 80-column card-image limit), which corrupts the last quoted
                       # item on a long comma-separated list (MATERIAL=(...), LAYERS=(...), etc.)
                       # into an unterminated string -- an "ABORT-LEVEL DIAGNOSTIC" that aborts
                       # BDL translation and leaves DOESIM.EXE never invoked (empty .sim, BecTh=0
                       # for every project, regardless of the building's actual input values).


def _rewrap_long_line(line: str, limit: int = _BDL_LINE_LIMIT) -> list[str]:
    """Split `line` into <=`limit`-column physical lines, breaking only at a comma that is
    outside any quoted string, with the continuation indented 4 past the original line's indent.
    """
    if len(line) <= limit:
        return [line]
    indent = len(line) - len(line.lstrip(" "))
    cont_prefix = " " * (indent + 4)
    out: list[str] = []
    current = line
    while len(current) > limit:
        quote_count = 0
        break_at = None
        for idx, ch in enumerate(current[:limit]):
            if ch == '"':
                quote_count += 1
            elif ch == "," and quote_count % 2 == 0:
                break_at = idx + 1
        if break_at is None:
            # No safe (outside-quotes) comma to break at within the limit -- leave it long
            # rather than risk corrupting a quoted string ourselves.
            out.append(current)
            current = ""
            break
        out.append(current[:break_at].rstrip())
        current = cont_prefix + current[break_at:].lstrip()
    if current:
        out.append(current)
    return out


def write_inp(work_dir: Path, file_name: str, lines: list[str]) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    target = work_dir / f"{file_name}.inp"
    wrapped = [wrapped_line for line in lines for wrapped_line in _rewrap_long_line(line)]
    target.write_text("\n".join(wrapped) + "\n", encoding="utf-8", newline="\n")
    return target


def generate_bdl(bi: BuildingInput, ref: ReferenceData, geo: BldgGeometry) -> tuple[list[str], AreaResult]:
    """Full runPerformance() pipeline up to (and including) building the .inp line list --
    everything that doesn't require the external DOE-2.2 engine, so it's fully testable here."""
    import datetime
    area = calc_area(bi, geo.bldg_shape_form)
    kv = build_doe22_kv(bi, geo, area, datetime.datetime.now().year)
    space_zone_lines = inp_space_zone_lines(ref, bi, geo, kv)  # mutates kv further (SpaceZoneKV, fuelType, design temps)

    glass_props = resolve_glass_props(ref, bi)
    template_lists = {
        "input": fill_variables(ref.line_table("Inp_Input"), kv),
        "bldg_mat": fill_variables(ref.line_table("Inp_Bldg_Mat"), kv),
        "bldg_layer": fill_variables(ref.line_table("Inp_Bldg_Layer"), kv),
        "bldg_const": fill_variables(ref.line_table("Inp_Bldg_Const"), kv),
        "user_mat": user_material_lines(bi),
        "user_layer_wall": user_layer_lines(bi, "Wall"),
        "user_layer_roof": user_layer_lines(bi, "Roof"),
        "user_const_wall": user_construction_lines(bi, "Wall"),
        "user_const_roof": user_construction_lines(bi, "Roof"),
        "bldg_glass": bldg_glass_lines(ref),
        "user_glass": user_glass_lines(bi),
        "combined_glass": combined_glass_lines(geo, glass_props),
        "bldg_sch": fill_variables(inp_bldg_sch_lines(ref, geo.bldg_type_cat), kv),
        "polygon": fill_variables(inp_polygon_lines(ref, bi, geo, area), kv),
        "space_zone": fill_variables(space_zone_lines, kv),
        "utility_output": fill_variables(ref.line_table("Inp_Utility_Output"), kv),
    }
    lines = build_inp_lines(bi, ref, geo, kv, template_lists)
    lines = apply_hvac_efficiency(lines, bi.txtCoolCOP, bi.txtHeatEff)
    return lines, area


@dataclass
class Doe22RunResult:
    success: bool
    message: str
    sim_path: Path | None = None


def run_doe22(doe22_dir: Path, work_dir: Path, file_name: str, bldg_location: str) -> Doe22RunResult:
    """Shells out to doe22/RUN22[.exe] exactly as runDoe22() did. Windows-only (RUN22.exe is a
    native Windows binary); on other platforms the .inp file is still generated and left for the
    user to run through the original Windows installation if needed.
    """
    if sys.platform != "win32":
        return Doe22RunResult(False, "DOE-2.2 (RUN22.exe) only runs on Windows; .inp file was generated but not simulated on this platform.")

    run22 = doe22_dir / "RUN22.exe"
    exent_dir = doe22_dir / "exent"
    weather_dir = doe22_dir / "weather"
    if not run22.exists():
        return Doe22RunResult(False, f"{run22} not found.")

    try:
        proc = subprocess.run(
            [str(run22), str(work_dir), file_name, str(weather_dir), bldg_location, str(exent_dir)],
            capture_output=True, text=True, cwd=str(doe22_dir),
            creationflags=subprocess.CREATE_NO_WINDOW,  # RUN22.exe is a console binary; suppress its flashing console window
        )
    except OSError as e:
        return Doe22RunResult(False, f"Failed to launch RUN22.exe: {e}")

    sim_path = work_dir / f"{file_name}.sim"
    bdl_path = work_dir / f"{file_name}.BDL"
    if proc.returncode != 0 or not sim_path.exists() or sim_path.stat().st_size == 0:
        detail = f"RUN22.exe exited with code {proc.returncode}.\n{proc.stdout}\n{proc.stderr}"
        if sim_path.exists() and sim_path.stat().st_size == 0 and bdl_path.exists():
            bdl_tail = bdl_path.read_text(encoding="latin-1", errors="replace").splitlines()[-15:]
            detail = (
                "DOE-2.2 produced an empty .sim file, which means DOEBDL rejected the generated "
                ".inp file before the simulation engine ever ran. Last lines of the BDL echo "
                f"({bdl_path.name}):\n" + "\n".join(bdl_tail)
            )
        return Doe22RunResult(False, detail)
    return Doe22RunResult(True, "OK", sim_path)
