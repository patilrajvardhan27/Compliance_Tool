"""Prescriptive-path compliance check. Python port of method/Prescriptive.java.

Unlike the DOE-2.2 performance path, this needs no external simulation engine, so it runs
identically on every platform -- this is the "offline tool" referred to as the first target
for the Python port.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tunbeec import constants as C
from tunbeec.calc.bldg_info import BldgGeometry
from tunbeec.calc.envelope import resolve_construction_u, resolve_glass_props
from tunbeec.data.reference import ReferenceData
from tunbeec.models import BuildingInput

_GRADE_BY_BRACKET = {
    # bracket index -> label, matches the if/elif chain in Prescriptive.setBldgCodeSelected()
    0: "Low", 1: "Medium", 2: "Medium", 3: "High", 4: "High", 5: "Very High", 6: "Very High",
}


@dataclass
class EnvelopeResult:
    item: str
    unit: str
    comp_value_1: float
    comp_value_2: float
    bldg_value: float
    compliant: bool


@dataclass
class PrescriptiveResult:
    climate: int
    bldg_zone: str
    x1: float
    x2: float
    grade: str
    code_thresholds: list[list[float]]  # 1 or 2 brackets of [wallU, roofU, glassU, glassSC]
    ext_wall_u: float
    roof_u: float
    glass_weighted_u: float
    glass_weighted_sc: float
    rows: list[EnvelopeResult]
    compliant: bool
    needs_performance_path: bool  # True when X1/X2 exceed every prescriptive bracket (Java auto-falls-back)
    report_variant: int  # 1, 2 or 3 -- selects ReportPrescriptive{n}.jrxml, mirrors selectReportPrescriptive


def _south_shading_multiplier(south_fp: float) -> float:
    """Shading factor (FMA) for the south-facing projection factor, method/Prescriptive.calcGlassWeightedSC()."""
    if south_fp <= 0.15:
        return 1.0
    if south_fp <= 0.25:
        return 0.85
    if south_fp <= 0.35:
        return 0.75
    return 0.7


def run_prescriptive(bi: BuildingInput, ref: ReferenceData, geo: BldgGeometry) -> PrescriptiveResult:
    # -- envelope U-values (setData) -------------------------------------------------------
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

    glass_props_full = resolve_glass_props(ref, bi)
    glass_props = {name: (u, sc) for name, (u, sc, _vt) in glass_props_full.items()}

    # -- climate + X1/X2 (setClimate, calcXAnd1X2) ------------------------------------------
    climate = geo.climate
    bldg_zone = f"ZT{climate}"

    total_win_area = sum(w.south_area + w.north_area + w.east_area + w.west_area for w in geo.windows)
    ew_win_area = sum(w.east_area + w.west_area for w in geo.windows)
    ew_wall_area = areas["E"] + areas["W"]
    x1 = total_win_area / total_wall_area * 100.0
    x2 = ew_win_area / ew_wall_area * 100.0 if ew_wall_area else 0.0

    # -- glass area-weighted U / SC (calcGlassWeightedU, calcGlassWeightedSC) ---------------
    weighted_u_num = weighted_sc_num = weighted_den = 0.0
    south_fma = _south_shading_multiplier(bi.txtWinSouthFp)
    for row, ws in zip(bi.window_rows, geo.windows):
        u, sc = glass_props.get(row.glass_type, (0.0, 0.0))
        row_area = ws.south_area + ws.north_area + ws.east_area + ws.west_area
        weighted_u_num += row_area * u
        weighted_sc_num += ws.south_area * sc * south_fma + (ws.north_area + ws.east_area + ws.west_area) * sc
        weighted_den += row_area
    glass_weighted_u = weighted_u_num / weighted_den if weighted_den else 0.0
    glass_weighted_sc = weighted_sc_num / weighted_den if weighted_den else 0.0

    # -- code table selection (setBldgCodeSelected) -----------------------------------------
    thresholds, grade, needs_performance = _select_code_thresholds(geo, x1, x2)
    report_variant = 3 if not thresholds else (1 if len(thresholds) == 1 else 2)

    rows = []
    compliant = True
    for bracket in thresholds:
        wall_ok = ext_wall_u <= bracket[0]
        roof_ok = roof_u <= bracket[1]
        glass_u_ok = glass_weighted_u <= bracket[2]
        glass_sc_ok = glass_weighted_sc <= bracket[3]
        rows = [
            EnvelopeResult("Wall U", "[W/m2.C]", bracket[0], bracket[0], ext_wall_u, wall_ok),
            EnvelopeResult("Roof U", "[W/m2.C]", bracket[1], bracket[1], roof_u, roof_ok),
            EnvelopeResult("Window U", "[W/m2.C]", bracket[2], bracket[2], glass_weighted_u, glass_u_ok),
            EnvelopeResult("SC*", "[n/a]", bracket[3], bracket[3], glass_weighted_sc, glass_sc_ok),
        ]
        compliant = wall_ok and roof_ok and glass_u_ok and glass_sc_ok

    return PrescriptiveResult(
        climate=climate, bldg_zone=bldg_zone, x1=x1, x2=x2, grade=grade,
        code_thresholds=thresholds, ext_wall_u=ext_wall_u, roof_u=roof_u,
        glass_weighted_u=glass_weighted_u, glass_weighted_sc=glass_weighted_sc,
        rows=rows, compliant=compliant if thresholds else False,
        needs_performance_path=needs_performance, report_variant=report_variant,
    )


def _bracket(table, climate_idx: int, i: int) -> list[float]:
    return list(table[climate_idx][i])


def _select_code_thresholds(geo: BldgGeometry, x1: float, x2: float):
    """Returns (thresholds: list of 1 or 2 brackets, grade, needs_performance_path)."""
    ci = geo.climate - 1  # 0-indexed for the code tables

    def brackets(*idxs):
        return [_bracket(table, ci, i) for i in idxs], table_name

    if geo.bldg_category == "Residential":
        table = C.CODE_RESIDENTIAL
        table_name = "residential"
        if ci == 0:
            if x1 <= 15.0 and x2 <= 10.0:
                return [_bracket(table, ci, 0)], "Low", False
            if x1 <= 15.0 and x2 > 10.0:
                return [_bracket(table, ci, 1), _bracket(table, ci, 2)], "Medium", False
            if 15.0 < x1 <= 25.0 and 10.0 < x2 <= 15.0:
                return [_bracket(table, ci, 1), _bracket(table, ci, 2)], "Medium", False
            if 15.0 < x1 <= 25.0 and x2 > 15.0:
                return [_bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and 15.0 < x2 <= 25.0:
                return [_bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and x2 > 25.0:
                return [_bracket(table, ci, 4)], "Very High", False
            if 35.0 < x1 <= 45.0 and 25.0 < x2 <= 35.0:
                return [_bracket(table, ci, 4)], "Very High", False
            if x1 > 45.0 or x2 > 35.0:
                return [], "Very High", True
        elif ci == 1:
            if x1 <= 15.0 and x2 <= 10.0:
                return [_bracket(table, ci, 0), _bracket(table, ci, 1)], "Low", False
            if x1 <= 15.0 and x2 > 10.0:
                return [_bracket(table, ci, 2)], "Medium", False
            if 15.0 < x1 <= 25.0 and 10.0 < x2 <= 15.0:
                return [_bracket(table, ci, 2)], "Medium", False
            if 15.0 < x1 <= 25.0 and x2 > 15.0:
                return [_bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and 15.0 < x2 <= 25.0:
                return [_bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and x2 > 25.0:
                return [_bracket(table, ci, 4)], "Very High", False
            if 35.0 < x1 <= 45.0 and 25.0 < x2 <= 35.0:
                return [_bracket(table, ci, 4)], "Very High", False
            if x1 > 45.0 or x2 > 35.0:
                return [], "Very High", True
        elif ci == 2:
            if x1 <= 15.0 and x2 <= 10.0:
                return [_bracket(table, ci, 0), _bracket(table, ci, 1)], "Low", False
            if x1 <= 15.0 and x2 > 10.0:
                return [_bracket(table, ci, 2)], "Medium", False
            if 15.0 < x1 <= 25.0 and 10.0 < x2 <= 15.0:
                return [_bracket(table, ci, 2)], "Medium", False
            if 15.0 < x1 <= 25.0 and x2 > 15.0:
                return [_bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and 15.0 < x2 <= 25.0:
                return [_bracket(table, ci, 3)], "High", False
            return [], "Very High", True
        return [], "", True

    if geo.bldg_type_cat == "Office" and geo.bldg_category == "Commercial" and geo.bldg_sector == "Private":
        table = C.CODE_COMM_PRIVATE
        if ci in (0, 1):
            if x1 <= 15.0 and x2 <= 10.0:
                return [_bracket(table, ci, 0)], "Low", False
            if x1 <= 15.0 and x2 > 10.0:
                return [_bracket(table, ci, 1)], "Medium", False
            if 15.0 < x1 <= 25.0 and 10.0 < x2 <= 15.0:
                return [_bracket(table, ci, 1)], "Medium", False
            if 15.0 < x1 <= 25.0 and x2 > 15.0:
                return [_bracket(table, ci, 2), _bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and 15.0 < x2 <= 25.0:
                return [_bracket(table, ci, 2), _bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and x2 > 25.0:
                return [_bracket(table, ci, 4)], "Very High", False
            if 35.0 < x1 <= 45.0 and 25.0 < x2 <= 35.0:
                return [_bracket(table, ci, 4)], "Very High", False
            return [], "Very High", True
        if ci == 2:
            if x1 <= 15.0 and x2 <= 10.0:
                return [_bracket(table, ci, 0)], "Low", False
            if x1 <= 15.0 and x2 > 10.0:
                return [_bracket(table, ci, 1)], "Medium", False
            if 15.0 < x1 <= 25.0 and 10.0 < x2 <= 15.0:
                return [_bracket(table, ci, 1)], "Medium", False
            if 15.0 < x1 <= 25.0 and x2 > 15.0:
                return [_bracket(table, ci, 2), _bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and 15.0 < x2 <= 25.0:
                return [_bracket(table, ci, 2), _bracket(table, ci, 3)], "High", False
            if 25.0 < x1 <= 35.0 and x2 > 25.0:
                return [_bracket(table, ci, 4), _bracket(table, ci, 5)], "Very High", False
            if 35.0 < x1 <= 45.0 and 25.0 < x2 <= 35.0:
                return [_bracket(table, ci, 4), _bracket(table, ci, 5)], "Very High", False
            return [], "Very High", True

    if geo.bldg_type_cat == "Office" and geo.bldg_category == "Commercial" and geo.bldg_sector == "Public":
        table = C.CODE_COMM_PUBLIC
        if ci == 0:
            if x1 <= 15.0 and x2 <= 10.0:
                return [_bracket(table, ci, 0)], "Low", False
            if x1 <= 15.0 and x2 > 10.0:
                return [_bracket(table, ci, 1)], "Medium", False
            if 15.0 < x1 <= 25.0 and 10.0 < x2 <= 15.0:
                return [_bracket(table, ci, 1)], "Medium", False
            if 15.0 < x1 <= 25.0 and x2 > 15.0:
                return [_bracket(table, ci, 2)], "High", False
            if 25.0 < x1 <= 35.0 and 15.0 < x2 <= 25.0:
                return [_bracket(table, ci, 2)], "High", False
            return [], "High", True
        if ci in (1, 2):
            if x1 <= 15.0 and x2 <= 10.0:
                return [_bracket(table, ci, 0)], "Low", False
            if x1 <= 15.0 and x2 > 10.0:
                return [_bracket(table, ci, 1)], "Medium", False
            if 15.0 < x1 <= 25.0 and 10.0 < x2 <= 15.0:
                return [_bracket(table, ci, 1)], "Medium", False
            return [], "High", True

    return [], "", True
