from __future__ import annotations

import re
import sys
import traceback

from fastapi import APIRouter, Depends, HTTPException

from api import convert, schemas
from api.deps import get_reference
from tunbeec.app_paths import DOE22_DIR, PROJECT_DIR
from tunbeec.calc.bldg_info import calc_bldg_geometry
from tunbeec.calc.performance import generate_bdl, resolve_envelope_info, run_doe22, write_inp
from tunbeec.calc.performance_report import assemble_report, determine_performance_result
from tunbeec.calc.prescriptive import run_prescriptive
from tunbeec.calc.sim_parser import parse_bec_th, parse_bldg_energy
from tunbeec.data.reference import ReferenceData

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


def _wwr_violations(building_input: schemas.BuildingInputSchema) -> list[str]:
    """Mirrors main_window.py's on_run_performance() per-orientation WWR>100% guard."""
    if not building_input.rdbtnWinWwr:
        return []
    violations = []
    for orientation, attr in (
        ("South", "south_percent"), ("North", "north_percent"),
        ("East", "east_percent"), ("West", "west_percent"),
    ):
        total = sum(getattr(row, attr) for row in building_input.window_rows)
        if total > 100.0:
            violations.append(
                f"The window rows on the {orientation} wall add up to {total:.0f}% of the wall "
                "area. The combined Window-to-Wall Ratio per orientation cannot exceed 100% -- "
                "DOE-2.2 would reject the building (windows larger than the wall). Please reduce "
                "the window percentages."
            )
    return violations


@router.post("/prescriptive", response_model=schemas.PrescriptiveResultSchema)
def run_prescriptive_check(
    building_input: schemas.BuildingInputSchema, ref: ReferenceData = Depends(get_reference)
) -> schemas.PrescriptiveResultSchema:
    bi = convert.building_input_from_schema(building_input)
    try:
        geo = calc_bldg_geometry(bi, ref, bi.space_rows)
        result = run_prescriptive(bi, ref, geo)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Calculation failed: {e}") from e
    return convert.prescriptive_result_schema(result)


@router.post("/performance", response_model=schemas.PerformanceRunResponse)
def run_performance_check(
    req: schemas.PerformanceRunRequest, ref: ReferenceData = Depends(get_reference)
) -> schemas.PerformanceRunResponse:
    violations = _wwr_violations(req.building_input)
    if violations:
        raise HTTPException(status_code=400, detail=violations[0])

    bi = convert.building_input_from_schema(req.building_input)

    try:
        geo = calc_bldg_geometry(bi, ref, bi.space_rows)
        envelope = resolve_envelope_info(ref, bi, geo)
        lines, area = generate_bdl(bi, ref, geo)
        work_dir = PROJECT_DIR
        work_dir.mkdir(parents=True, exist_ok=True)
        # The stem names the DOE-2.2 scratch files (.inp/.sim) inside PROJECT_DIR only -- the
        # project itself lives on the user's machine, so any display name is accepted here but
        # must be reduced to a safe filename component.
        file_stem = re.sub(r"[^A-Za-z0-9 _\-]", "", req.project_name).strip() or "building"
        inp_path = write_inp(work_dir, file_stem, lines)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"BDL file generation failed: {e}") from e

    run_result = run_doe22(DOE22_DIR, work_dir, file_stem, bi.cmbBldgLocation)
    sim_path = run_result.sim_path
    if sim_path is None:
        candidate = work_dir / f"{file_stem}.sim"
        if candidate.exists() and candidate.stat().st_size > 0:
            sim_path = candidate  # reuse a .sim produced by a prior Windows run of RUN22.exe

    if sim_path is None:
        if sys.platform != "win32":
            return schemas.PerformanceRunResponse(
                status="simulation_unavailable",
                message=(
                    f"BDL file generated: {inp_path}. The DOE-2.2 simulation engine "
                    "(doe22/RUN22.exe) is a Windows binary and cannot be run on this platform. "
                    "Run this .inp file through a Windows deployment of this backend to produce "
                    f"{file_stem}.sim, then re-run this check (the .sim file will be detected "
                    f"automatically). Detail: {run_result.message}"
                ),
                inp_path=str(inp_path),
            )
        return schemas.PerformanceRunResponse(
            status="simulation_failed",
            message=f"DOE-2.2 simulation failed: {run_result.message}",
            inp_path=str(inp_path),
        )

    try:
        thermal = parse_bec_th(
            sim_path, area.cond_area_si, geo.skylt_clg_cor, geo.skylt_htg_cor,
            geo.flr_shape_clg_cor, geo.flr_shape_htg_cor,
        )
        energy = parse_bldg_energy(sim_path)
        perf = determine_performance_result(geo, thermal.bec_th)
        report = assemble_report(
            bi.txtBldgName, bi.txtBldgAddress, bi.cmbBldgType, geo, envelope, area, thermal, energy, perf,
        )
        report.bldg_loc = bi.cmbBldgLocation
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Simulation result analysis failed: {e}") from e

    return schemas.PerformanceRunResponse(
        status="ok", inp_path=str(inp_path), report=convert.performance_report_schema(report),
    )
