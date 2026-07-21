"""Class-threshold assignment, compliance verdict, and final report field assembly.

Port of the tail of method/PerformanceOld.writeResult() (class selection) and
method/Report.java's fillGeneralData()/fillPerformanceData() (report parameter list) --
this is what lib1/ReportPerformance.jrxml renders (the "Performance Compliance Report").
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tunbeec import constants as C
from tunbeec.calc.bldg_info import BldgGeometry
from tunbeec.calc.performance import AreaResult, EnvelopeInfo
from tunbeec.calc.sim_parser import EnergyResult, ThermalLoadResult

_CLASS_TABLES = {
    "Residential": C.CLASS_THRESHOLDS_RESIDENTIAL,
    ("Office",): C.CLASS_THRESHOLDS_OFFICE,
    ("Hotel",): C.CLASS_THRESHOLDS_HOTEL,
    ("Hospital",): C.CLASS_THRESHOLDS_HOSPITAL,
}


@dataclass
class ClassRow:
    class_name: str
    class_value: float
    class_bldg: str = ""  # "%.1f" BecTh string, filled only on the matched row


@dataclass
class PerformanceResult:
    class_rows: list[ClassRow]
    bldg_class: str
    bldg_value: float
    min_class: str
    min_value: float
    result: str  # "Compliant" | "Non-Compliant" | "ERROR"


def _select_class_table(bldg_category: str, bldg_type_cat: str) -> list[float]:
    if bldg_category == "Residential":
        return C.CLASS_THRESHOLDS_RESIDENTIAL
    if bldg_type_cat == "Office":
        return C.CLASS_THRESHOLDS_OFFICE
    if bldg_type_cat == "Hotel":
        return C.CLASS_THRESHOLDS_HOTEL
    if bldg_type_cat == "Hospital":
        return C.CLASS_THRESHOLDS_HOSPITAL
    raise ValueError(f"No class table for category={bldg_category!r} type={bldg_type_cat!r}")


def _min_class(geo: BldgGeometry) -> tuple[int, str]:
    """Returns (1-based min-class-index, label) -- the writeResult() lookup table."""
    if geo.bldg_category == "Residential":
        return 5, "Class 5"
    if geo.bldg_type_cat == "Office":
        return (3, "Class 3") if geo.bldg_sector == "Public" else (5, "Class 5")
    if geo.bldg_type_cat == "Hotel":
        if geo.bldg_star == "ThreeStar":
            return 3, "Class 3"
        if geo.bldg_star == "FourStar":
            return 4, "Class 4"
        if geo.bldg_star == "FiveStar":
            return 3, "Class 3"
        raise ValueError(f"Unknown hotel star rating: {geo.bldg_star!r}")
    if geo.bldg_type_cat == "Hospital":
        return (3, "Class 3") if geo.bldg_sector == "Public" else (5, "Class 5")
    raise ValueError(f"No minimum-class rule for type={geo.bldg_type_cat!r}")


def determine_performance_result(geo: BldgGeometry, bec_th: float) -> PerformanceResult:
    thresholds = _select_class_table(geo.bldg_category, geo.bldg_type_cat)
    rows = [ClassRow(f"Class {i + 1}", v) for i, v in enumerate(thresholds)]

    matched_j = None  # 1-based index into rows, matching Java's classSelected[1..8]
    for j, v in enumerate(thresholds, start=1):
        if bec_th <= v:
            matched_j = j
            break
    if matched_j is None:
        matched_j = 8  # PerformanceOld.java's post-loop fallback

    rows[matched_j - 1].class_bldg = f"{bec_th:.1f}"
    bldg_class = rows[matched_j - 1].class_name

    min_idx, min_class = _min_class(geo)
    min_value = thresholds[min_idx - 1]

    if bec_th == 0.0:
        result = "ERROR"
        bldg_class = "ERROR"
    elif matched_j >= min_idx + 1:
        result = "Non-Compliant"
    else:
        result = "Compliant"

    return PerformanceResult(
        class_rows=rows, bldg_class=bldg_class, bldg_value=bec_th,
        min_class=min_class, min_value=min_value, result=result,
    )


@dataclass
class PerformanceReport:
    """Flat field set mirroring Report.fillGeneralData()+fillPerformanceData() -- what
    ReportPerformance.jrxml (image.png) renders."""
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

    class_rows: list[ClassRow] = field(default_factory=list)


def assemble_report(
    bi_name: str, bi_address: str, bi_type_label: str, geo: BldgGeometry, envelope: EnvelopeInfo,
    area: AreaResult, thermal: ThermalLoadResult, energy: EnergyResult, perf: PerformanceResult,
) -> PerformanceReport:
    cond_area = area.cond_area_si
    total_area = area.total_area_si
    return PerformanceReport(
        bldg_name=bi_name, bldg_address=bi_address, bldg_type=geo.bldg_type_cat,
        bldg_category=geo.bldg_category, bldg_sector=geo.bldg_sector, bldg_star=geo.bldg_star,
        bldg_loc="",
        ext_wall_const_u=envelope.ext_wall_u, ext_wall_const_south_u=envelope.ext_wall_u_south,
        ext_wall_const_north_u=envelope.ext_wall_u_north, ext_wall_const_east_u=envelope.ext_wall_u_east,
        ext_wall_const_west_u=envelope.ext_wall_u_west, roof_const_u=envelope.roof_u,
        glass_u=envelope.glass_u, glass_sc=envelope.glass_sc,
        min_bec_th=perf.min_value, bldg_bec_th=perf.bldg_value, min_class=perf.min_class,
        bldg_class=perf.bldg_class, result=perf.result,
        h_load=thermal.bec_h / cond_area if cond_area else 0.0,
        c_load=thermal.bec_ref / cond_area if cond_area else 0.0,
        a_load=thermal.bec_th,
        h_energy=energy.heat_energy / total_area if total_area else 0.0,
        c_energy=energy.cool_energy / total_area if total_area else 0.0,
        a_energy=energy.ann_energy / total_area if total_area else 0.0,
        a_src_energy=energy.ann_source_energy / total_area if total_area else 0.0,
        a_co2=energy.ann_co2 / total_area if total_area else 0.0,
        class_rows=perf.class_rows,
    )
