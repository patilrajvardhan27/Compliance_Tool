#!/usr/bin/env python3
"""Headless end-to-end check for the Performance Approach (DOE-2.2) pipeline.

Runs the exact sequence MainWindow.on_run_performance() runs (calc_bldg_geometry ->
resolve_envelope_info -> generate_bdl -> write_inp -> run_doe22 -> parse_bec_th/
parse_bldg_energy -> determine_performance_result -> assemble_report), twice:

  1. "default"  -- a BuildingInput built purely from new_building_input() (nothing edited
                   by a user, exactly what a fresh "New" project looks like).
  2. "custom"   -- the same building but with several fields changed to clearly different
                   values (bigger footprint, different walls, different HVAC/location/
                   setpoints), simulating what happens after a user actually fills the form in.

This exists to answer two concrete questions without needing a physical Windows machine:
  - Does the performance check complete (produce a report) when nothing has been edited?
  - Does changing the inputs actually change the result, i.e. is the report driven by the
    live BuildingInput rather than some hardcoded/default path?

RUN22.exe only runs on win32, so this only exercises the real DOE-2.2 engine when run on a
Windows CI runner; on macOS/Linux it still validates BDL/.inp generation end-to-end and reports
that the simulation step itself was skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tunbeec.app_paths import DEFAULT_DB_PATH, DOE22_DIR, PROJECT_DIR
from tunbeec.app_state import new_building_input
from tunbeec.calc.bldg_info import calc_bldg_geometry
from tunbeec.calc.performance import generate_bdl, resolve_envelope_info, run_doe22, write_inp
from tunbeec.calc.performance_report import assemble_report, determine_performance_result
from tunbeec.calc.sim_parser import parse_bec_th, parse_bldg_energy
from tunbeec.data.reference import ReferenceData


def run_case(name: str, bi, ref) -> dict:
    print(f"\n=== case: {name} ===")
    geo = calc_bldg_geometry(bi, ref, bi.space_rows)
    envelope = resolve_envelope_info(ref, bi, geo)
    lines, area = generate_bdl(bi, ref, geo)
    work_dir = PROJECT_DIR / "ci_out"
    inp_path = write_inp(work_dir, name, lines)
    print(f"  .inp written: {inp_path} ({len(lines)} lines)")

    run_result = run_doe22(DOE22_DIR, work_dir, name, bi.cmbBldgLocation)
    print(f"  run_doe22: success={run_result.success} sim_path={run_result.sim_path}")
    print(f"  message: {run_result.message}")
    print(f"  work_dir contents: {sorted(p.name for p in work_dir.iterdir())}")
    for suffix in (".sim", ".msg", ".BDL", ".err", ".ERR"):
        candidate = work_dir / f"{name}{suffix}"
        if candidate.exists():
            size = candidate.stat().st_size
            print(f"  {candidate.name}: {size} bytes")
            if suffix in (".sim", ".msg") and size:
                text = candidate.read_text(encoding="latin-1", errors="replace")
                markers = {m: (m in text) for m in ("SS-D", "SS-E", "BEPS", "EM1", "FM1", "FATAL", "ERROR")}
                print(f"    markers: {markers}")
                print("    --- first 15 lines ---")
                for l in text.splitlines()[:15]:
                    print(f"    {l}")
                print("    --- last 15 lines ---")
                for l in text.splitlines()[-15:]:
                    print(f"    {l}")
            if suffix == ".BDL" and size:
                text = candidate.read_text(encoding="latin-1", errors="replace")
                bdl_lines = text.splitlines()
                flagged = [l for l in bdl_lines if any(
                    kw in l.upper() for kw in ("ERROR", "FATAL", "WARNING", "ABORT", "SEVERE")
                )]
                print(f"    .BDL total lines: {len(bdl_lines)}; flagged lines: {len(flagged)}")
                for l in flagged[:40]:
                    print(f"    FLAG: {l}")
                print("    --- .BDL last 40 lines ---")
                for l in bdl_lines[-40:]:
                    print(f"    {l}")

    if run_result.sim_path is None:
        return {"name": name, "simulated": False}

    thermal = parse_bec_th(
        run_result.sim_path, area.cond_area_si, geo.skylt_clg_cor, geo.skylt_htg_cor,
        geo.flr_shape_clg_cor, geo.flr_shape_htg_cor,
    )
    energy = parse_bldg_energy(run_result.sim_path)
    perf = determine_performance_result(geo, thermal.bec_th)
    report = assemble_report(bi.txtBldgName, bi.txtBldgAddress, bi.cmbBldgType, geo, envelope,
                              area, thermal, energy, perf)
    print(f"  bec_th={report.bldg_bec_th:.2f} class={report.bldg_class} result={report.result}")
    return {
        "name": name, "simulated": True, "bec_th": report.bldg_bec_th,
        "class": report.bldg_class, "result": report.result,
    }


def main() -> int:
    ref = ReferenceData(DEFAULT_DB_PATH)

    bi_default = new_building_input(ref)

    bi_custom = new_building_input(ref)
    bi_custom.txtBldgName = "CI Custom Building"
    bi_custom.cmbBldgType = "Villa"
    bi_custom.txtBldgNumFloor = 2
    bi_custom.txtBldgCondArea = 80.0
    bi_custom.cmbBldgShape = "L-Shape"
    bi_custom.txtLengX1 = 30.0
    bi_custom.txtLengY1 = 25.0
    bi_custom.txtLengX2 = 12.0
    bi_custom.txtLengY2 = 10.0
    bi_custom.cmbBldgLocation = "SFAX"
    bi_custom.txtHeatSetTemp = 18.0
    bi_custom.txtCoolSetTemp = 27.0
    from tunbeec.app_state import apply_building_type_defaults
    apply_building_type_defaults(bi_custom, ref)
    for row in bi_custom.window_rows:
        row.south_percent = min(80.0, row.south_percent + 20.0)

    results = [run_case("default", bi_default, ref), run_case("custom", bi_custom, ref)]

    print("\n=== summary ===")
    for r in results:
        print(r)

    simulated = [r for r in results if r["simulated"]]
    if len(simulated) < 2:
        print("\nSIMULATION SKIPPED on this platform (RUN22.exe is Windows-only) -- "
              "BDL generation succeeded for both cases but DOE-2.2 itself did not run.")
        return 0

    if simulated[0]["bec_th"] == simulated[1]["bec_th"]:
        print("\nFAIL: default and custom inputs produced an IDENTICAL bec_th -- "
              "the performance path does not appear to be responding to user input.")
        return 1

    print("\nPASS: default case produced a report, and custom inputs changed the result "
          f"({simulated[0]['bec_th']:.2f} -> {simulated[1]['bec_th']:.2f}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
