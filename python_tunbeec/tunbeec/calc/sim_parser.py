"""Parses DOE-2.2 `.sim` output. Port of method/PerformanceOld.calcBecTh()/calcBldgEnergy()."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tunbeec import constants as C

_WS_RUN = re.compile(r" +")


def _normalize(line: str) -> list[str]:
    """Java: line.replaceAll(" ", "#").replaceAll("#+", ":") then split(":")."""
    return _WS_RUN.sub(":", line).split(":")


@dataclass
class ThermalLoadResult:
    bec_h: float    # annual heating, kWh (already sign-flipped positive)
    bec_ref: float  # annual cooling, kWh
    stc: float      # conditioned area, m2 (== cond_area_si)
    bec_th: float   # kWh/m2.year


@dataclass
class EnergyResult:
    cool_energy: float        # actually total annual ELECTRICITY site energy, kWh (naming kept from Java)
    heat_energy: float        # actually total annual GAS site energy, kWh
    ann_energy: float
    ann_source_energy: float
    ann_co2: float


def parse_bec_th(sim_path: Path, cond_area_si: float, skylt_clg_cor: float, skylt_htg_cor: float,
                  flr_shape_clg_cor: float, flr_shape_htg_cor: float) -> ThermalLoadResult:
    lines = sim_path.read_text(encoding="latin-1", errors="replace").splitlines()
    loc_report = False
    bec_h = bec_ref = 0.0
    for line in lines:
        if "SS-D" in line:
            loc_report = True
        if loc_report and "TOTAL" in line:
            parts = _normalize(line)
            bec_ref = float(parts[1]) * C.MBTU_TO_KWH * skylt_clg_cor * flr_shape_clg_cor
            bec_h = float(parts[2]) * -1.0 * C.MBTU_TO_KWH * skylt_htg_cor * flr_shape_htg_cor
        if "SS-E" in line:
            break
    stc = cond_area_si
    bec_th = (bec_h + bec_ref) / stc if stc else 0.0
    return ThermalLoadResult(bec_h=bec_h, bec_ref=bec_ref, stc=stc, bec_th=bec_th)


def parse_bldg_energy(sim_path: Path) -> EnergyResult:
    lines = sim_path.read_text(encoding="latin-1", errors="replace").splitlines()
    loc_report = False
    cool_energy = heat_energy = ann_energy = ann_source_energy = ann_co2 = 0.0
    for i, line in enumerate(lines):
        if "BEPS" in line:
            loc_report = True
        if loc_report:
            if "EM1" in line and i + 1 < len(lines):
                parts = _normalize(lines[i + 1])
                cool_energy = float(parts[14]) * C.MBTU_TO_KWH
            if "FM1" in line and i + 1 < len(lines):
                parts = _normalize(lines[i + 1])
                heat_energy = float(parts[14]) * C.MBTU_TO_KWH
                ann_energy = cool_energy + heat_energy
                ann_co2 = (
                    cool_energy * C.CO2_ELEC_SOURCE_MULTIPLIER * C.CO2_ELEC_FACTOR
                    + heat_energy * C.CO2_GAS_FACTOR
                )
            if "TOTAL SOURCE ENERGY" in line:
                parts = _normalize(line)
                ann_source_energy = float(parts[4]) * C.MBTU_TO_KWH
        if "BEPU" in line:
            break
    return EnergyResult(cool_energy, heat_energy, ann_energy, ann_source_energy, ann_co2)
