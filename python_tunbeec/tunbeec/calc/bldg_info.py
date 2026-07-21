"""Building geometry / envelope-area / schedule aggregation.

Python port of method/BldgInfo.java's readBldgInfo(). Pure function of (BuildingInput,
ReferenceData, the live space-condition table rows) -> BldgGeometry, rather than the original's
static-field mutation of a shared SimData subclass.

Note: the original app never actually persists the user's edited space-condition table
(tblSpaceCond) into the project .tct file (confirmed -- there is no User_SpaceCond table in
PROJECT/test1..5.tct). Reopening a project always re-derives the 8-row table fresh from
`<cat>_AreaAllocation` for the building's current type. This port reproduces that: callers pass
`space_rows` sourced from `ReferenceData.space_cond_rows()` by default, or from a live edited
GUI table.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from tunbeec import constants as C
from tunbeec.calc import shape as shape_calc
from tunbeec.data.reference import ReferenceData
from tunbeec.models import BuildingInput, SpaceConditionRow

_SILL_HEIGHT_M = 0.25 * C.FT_TO_M
_CEILING_UNDER_HEIGHT_M = 0.25 * C.FT_TO_M
_FRAME_WIDTH_M = 0.0 * C.FT_TO_M

# BldgInfo.java: 10 UI shape names collapse to 4 structural forms for wall-area geometry.
_SHAPE_TO_FORM = {
    "Rectangular": "R", "Hexagon": "R", "Octagon": "R", "Decagon": "R",
    "Dodecagon": "R", "Hexadecagon": "R", "Octadecagon": "R",
    "L-Shape": "L", "T-Shape": "T", "U-Shape": "U",
}

_SKYLT_CVR_LIST = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
_SKYLT_TABLES = {
    (1, "Flat"): {
        "clg": [1.0, 1.09, 1.17, 1.25, 1.32, 1.39, 1.46, 1.51, 1.57, 1.62, 1.65],
        "htg": [1.0, 2.78, 6.53, 11.16, 15.95, 21.14, 26.36, 30.89, 35.89, 40.07, 42.97],
    },
    (1, "Dome"): {
        "clg": [1.0, 1.1, 1.19, 1.28, 1.36, 1.44, 1.51, 1.58, 1.65, 1.7, 1.74],
        "htg": [1.0, 3.25, 7.82, 13.24, 18.92, 24.91, 30.79, 35.8, 41.55, 46.32, 49.39],
    },
    (2, "Flat"): {
        "clg": [1.0, 1.08, 1.15, 1.23, 1.3, 1.37, 1.44, 1.5, 1.56, 1.61, 1.64],
        "htg": [1.0, 2.16, 4.37, 7.55, 11.1, 14.75, 18.32, 21.42, 25.04, 28.02, 30.14],
    },
    (2, "Dome"): {
        "clg": [1.0, 1.09, 1.17, 1.26, 1.35, 1.43, 1.5, 1.56, 1.63, 1.69, 1.73],
        "htg": [1.0, 2.43, 5.17, 9.1, 13.3, 17.42, 21.48, 25.1, 29.25, 32.69, 34.96],
    },
    (3, "Flat"): {
        "clg": [1.0, 1.11, 1.21, 1.3, 1.39, 1.46, 1.54, 1.6, 1.67, 1.73, 1.77],
        "htg": [1.0, 2.38, 4.64, 7.2, 9.82, 12.26, 14.68, 16.75, 19.05, 20.97, 22.31],
    },
    (3, "Dome"): {
        "clg": [1.0, 1.12, 1.23, 1.34, 1.43, 1.52, 1.61, 1.68, 1.76, 1.82, 1.86],
        "htg": [1.0, 2.7, 5.41, 8.39, 11.36, 14.12, 16.85, 19.16, 21.82, 24.02, 25.44],
    },
}

_AVG_WWR_LIST = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
_FLRSHAPE_TABLES = {
    (1, "Hexagon"): {"clg": [1.006, 1.001, 0.999, 0.995, 1.029, 1.026], "htg": [0.783, 0.8, 0.75, 1.111, 1.0, 0.824]},
    (1, "Octagon"): {"clg": [1.007, 1.001, 0.998, 0.993, 1.026, 1.023], "htg": [0.783, 0.733, 0.75, 1.444, 1.0, 0.824]},
    (1, "Decagon"): {"clg": [1.009, 1.001, 0.998, 0.992, 1.025, 1.021], "htg": [0.739, 0.667, 0.75, 1.444, 1.0, 0.824]},
    (1, "Dodecagon"): {"clg": [1.009, 1.001, 0.997, 0.992, 1.024, 1.021], "htg": [0.739, 0.667, 0.75, 1.444, 1.0, 0.824]},
    (1, "Hexadecagon"): {"clg": [1.009, 1.0, 0.997, 0.991, 1.023, 1.019], "htg": [0.696, 0.667, 0.75, 1.333, 1.0, 0.824]},
    (1, "Octadecagon"): {"clg": [1.01, 1.0, 0.997, 0.991, 1.023, 1.019], "htg": [0.696, 0.667, 0.75, 1.333, 1.0, 0.824]},
    (2, "Hexagon"): {"clg": [1.005, 1.002, 0.973, 0.996, 0.996, 0.992], "htg": [0.917, 0.944, 1.111, 1.25, 1.2, 1.286]},
    (2, "Octagon"): {"clg": [1.007, 1.003, 0.972, 0.995, 0.993, 0.989], "htg": [0.833, 0.889, 1.0, 1.25, 1.2, 1.286]},
    (2, "Decagon"): {"clg": [1.008, 1.003, 0.972, 0.969, 0.992, 0.988], "htg": [0.792, 0.833, 1.0, 1.25, 1.2, 1.286]},
    (2, "Dodecagon"): {"clg": [1.008, 1.002, 0.971, 0.969, 0.991, 0.987], "htg": [0.792, 0.889, 1.0, 1.25, 1.2, 1.286]},
    (2, "Hexadecagon"): {"clg": [1.008, 1.002, 0.971, 0.968, 0.99, 0.986], "htg": [0.792, 0.889, 1.0, 1.25, 1.2, 1.286]},
    (2, "Octadecagon"): {"clg": [1.009, 1.002, 0.971, 0.968, 0.99, 0.985], "htg": [0.792, 0.889, 1.0, 1.25, 1.2, 1.286]},
    (3, "Hexagon"): {"clg": [1.003, 0.999, 0.997, 0.994, 0.992, 0.99], "htg": [0.857, 0.918, 0.926, 0.958, 1.0, 1.077]},
    (3, "Octagon"): {"clg": [1.004, 0.999, 0.995, 0.992, 0.989, 0.986], "htg": [0.814, 0.894, 0.897, 0.883, 0.968, 1.103]},
    (3, "Decagon"): {"clg": [1.005, 0.998, 0.995, 0.991, 0.988, 0.984], "htg": [0.81, 0.882, 0.89, 0.883, 0.968, 1.09]},
    (3, "Dodecagon"): {"clg": [1.005, 0.998, 0.994, 0.99, 0.987, 0.984], "htg": [0.805, 0.882, 0.882, 0.875, 0.958, 1.051]},
    (3, "Hexadecagon"): {"clg": [1.005, 0.998, 0.994, 0.989, 0.986, 0.983], "htg": [0.795, 0.882, 0.882, 0.883, 0.968, 1.038]},
    (3, "Octadecagon"): {"clg": [1.005, 0.992, 0.994, 0.989, 0.986, 0.983], "htg": [0.795, 0.894, 0.89, 0.883, 0.968, 1.038]},
}


def _linear_interp(xs: list[float], ys: list[float], xi: float) -> float:
    """Equivalent of BldgInfo.linearInterp (Apache Commons LinearInterpolator), via numpy-free interp."""
    if xi <= xs[0]:
        return ys[0]
    if xi >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= xi <= xs[i + 1]:
            t = (xi - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


def climate_zone(bldg_location: str) -> int:
    """1/2/3, per constants.CLIMATE_LOCATIONS (method/Prescriptive.java's `location` table)."""
    for zone_index, names in enumerate(C.CLIMATE_LOCATIONS, start=1):
        if bldg_location in names:
            return zone_index
    raise ValueError(f"Unknown location: {bldg_location!r}")


@dataclass
class WallGeometry:
    width: float
    area: float


@dataclass
class WindowSet:
    """Areas/WWR for one of the 5 window-allocation rows, per orientation."""
    south_area: float = 0.0
    north_area: float = 0.0
    east_area: float = 0.0
    west_area: float = 0.0
    south_wwr: float = 0.0
    north_wwr: float = 0.0
    east_wwr: float = 0.0
    west_wwr: float = 0.0
    glass_type: str = ""


@dataclass
class SpaceAggregate:
    percent_area: float = 0.0
    area: float = 0.0
    occupant: float = 0.0
    infiltration: float = 0.0
    lighting: float = 0.0
    plug_load: float = 0.0


@dataclass
class BldgGeometry:
    bldg_type_cat: str          # e.g. "Office" (BldgType.Cat)
    bldg_category: str          # "Residential" | "Commercial" (BldgType.Use)
    bldg_sector: str            # "Private" | "Public"
    bldg_star: str
    bldg_shape_form: str        # "R" | "L" | "T" | "U"
    climate: int                # 1 / 2 / 3

    floor_area: float
    cond_area_ratio: float      # capped at 98%, per BldgInfo.java

    south: WallGeometry
    north: WallGeometry
    east: WallGeometry
    west: WallGeometry

    windows: list[WindowSet]    # 5 entries, one per window-allocation row

    cond_space: SpaceAggregate
    uncond_space: SpaceAggregate

    skylt_clg_cor: float = 1.0
    skylt_htg_cor: float = 1.0
    flr_shape_clg_cor: float = 1.0
    flr_shape_htg_cor: float = 1.0


def _wall_geometry(form: str, bi: BuildingInput, ceiling_height: float):
    x1, y1, x2, y2, y3 = bi.txtLengX1, bi.txtLengY1, bi.txtLengX2, bi.txtLengY2, bi.txtLengY3
    if form in ("R", "L", "T"):
        south = north = WallGeometry(x1, x1 * ceiling_height)
        east = west = WallGeometry(y1, y1 * ceiling_height)
    elif form == "U":
        south = north = WallGeometry(x1, x1 * ceiling_height)
        east_width = y1 - y3 + y2
        west_width = y2 - y3 + y1
        east = WallGeometry(east_width, east_width * ceiling_height)
        west = WallGeometry(west_width, west_width * ceiling_height)
    else:
        raise ValueError(f"Unknown structural form: {form!r}")
    return south, north, east, west


def calc_bldg_geometry(bi: BuildingInput, ref: ReferenceData, space_rows: list[SpaceConditionRow]) -> BldgGeometry:
    type_row = ref.bldg_type_row(bi.cmbBldgType)
    if type_row is None:
        raise ValueError(f"Unknown building type: {bi.cmbBldgType!r}")

    if bi.cmbBldgShape not in _SHAPE_TO_FORM:
        raise ValueError(
            f"Unrecognized building shape {bi.cmbBldgShape!r} (expected one of {sorted(_SHAPE_TO_FORM)}); "
            "this is a data-quality issue in the source project, matching how the original Java app "
            "would also fail to match any of its shape checks and leave bldgShape unset."
        )
    form = _SHAPE_TO_FORM[bi.cmbBldgShape]
    ceiling_height = bi.txtFloorHeight
    south, north, east, west = _wall_geometry(form, bi, ceiling_height)

    cond_area_ratio = min(bi.txtBldgCondArea, 98.0)

    windows: list[WindowSet] = []
    for row in bi.window_rows:
        ws = WindowSet(glass_type=row.glass_type)
        if bi.rdbtnWinWwr:
            ws.south_area = row.south_percent / 100.0 * south.area
            ws.north_area = row.north_percent / 100.0 * north.area
            ws.east_area = row.east_percent / 100.0 * east.area
            ws.west_area = row.west_percent / 100.0 * west.area
            ws.south_wwr, ws.north_wwr, ws.east_wwr, ws.west_wwr = (
                row.south_percent, row.north_percent, row.east_percent, row.west_percent,
            )
        else:
            ws.south_area, ws.north_area, ws.east_area, ws.west_area = (
                row.south_percent, row.north_percent, row.east_percent, row.west_percent,
            )
            ws.south_wwr = ws.south_area / south.area * 100.0 if south.area else 0.0
            ws.north_wwr = ws.north_area / north.area * 100.0 if north.area else 0.0
            ws.east_wwr = ws.east_area / east.area * 100.0 if east.area else 0.0
            ws.west_wwr = ws.west_area / west.area * 100.0 if west.area else 0.0
        windows.append(ws)

    cond = SpaceAggregate()
    uncond = SpaceAggregate()
    cond_pct = uncond_pct = 0.0
    for row in space_rows:
        target = cond if row.conditioned else uncond
        pct = row.percent_area
        if row.conditioned:
            cond_pct += pct
        else:
            uncond_pct += pct
        target.occupant += pct * row.occupant
        target.infiltration += pct * row.infiltration
        target.lighting += pct * row.lighting
        target.plug_load += pct * row.plug_load
    cond.percent_area, uncond.percent_area = cond_pct, uncond_pct
    if cond_pct:
        cond.occupant, cond.infiltration, cond.lighting, cond.plug_load = (
            cond.occupant / cond_pct, cond.infiltration / cond_pct, cond.lighting / cond_pct, cond.plug_load / cond_pct,
        )
    if uncond_pct:
        uncond.occupant, uncond.infiltration, uncond.lighting, uncond.plug_load = (
            uncond.occupant / uncond_pct, uncond.infiltration / uncond_pct,
            uncond.lighting / uncond_pct, uncond.plug_load / uncond_pct,
        )
    cond.area = bi.txtFloorArea * cond_pct / 100.0 if cond_pct else 0.0
    uncond.area = bi.txtFloorArea * uncond_pct / 100.0 if uncond_pct else 0.0

    geo = BldgGeometry(
        bldg_type_cat=type_row.cat, bldg_category=type_row.use, bldg_sector=type_row.sector,
        bldg_star=type_row.star, bldg_shape_form=form, climate=climate_zone(bi.cmbBldgLocation),
        floor_area=bi.txtFloorArea, cond_area_ratio=cond_area_ratio,
        south=south, north=north, east=east, west=west, windows=windows,
        cond_space=cond, uncond_space=uncond,
    )

    # Skylight + floor-shape correction factors (used later for BECth in the performance path).
    zt = geo.climate
    if bi.txtSkyltType in ("Flat", "Dome") and (zt, bi.txtSkyltType) in _SKYLT_TABLES:
        tbl = _SKYLT_TABLES[(zt, bi.txtSkyltType)]
        geo.skylt_clg_cor = _linear_interp(_SKYLT_CVR_LIST, tbl["clg"], bi.txtSkyltCvr)
        geo.skylt_htg_cor = _linear_interp(_SKYLT_CVR_LIST, tbl["htg"], bi.txtSkyltCvr)

    total_wwr = [w for w in (
        sum(r.south_wwr for r in windows), sum(r.north_wwr for r in windows),
        sum(r.east_wwr for r in windows), sum(r.west_wwr for r in windows),
    ) if w > 0]
    if total_wwr and bi.cmbBldgShape in ("Hexagon", "Octagon", "Decagon", "Dodecagon", "Hexadecagon", "Octadecagon"):
        avg_wwr = min(sum(total_wwr) / len(total_wwr), 50.0)
        tbl = _FLRSHAPE_TABLES.get((zt, bi.cmbBldgShape))
        if tbl:
            geo.flr_shape_clg_cor = _linear_interp(_AVG_WWR_LIST, tbl["clg"], avg_wwr)
            geo.flr_shape_htg_cor = _linear_interp(_AVG_WWR_LIST, tbl["htg"], avg_wwr)

    return geo
