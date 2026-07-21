"""Port of method/BldgElement.java's calcGap() -- the perimeter offset ("gap", in ft since all
inputs are pre-converted to ft by the caller) that separates the conditioned perimeter zone from
an unconditioned core, sized so the conditioned area matches condAreaPercentDbl/100 of the floor.
"""
from __future__ import annotations

import math


def calc_gap(form: str, ratio: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> float:
    if form == "R":
        return (2.0 * x1 + 2.0 * y1 - math.sqrt((2.0 * x1 + 2.0 * y1) ** 2 - 16.0 * ratio * x1 * y1)) / 8.0
    if form == "L":
        return (2.0 * x1 + 2.0 * y1 - math.sqrt(
            (2.0 * x1 + 2.0 * y1) ** 2 - 16.0 * ratio * (x1 * y1 - (x1 - x2) * (y1 - y2))
        )) / 8.0
    if form == "T":
        return (2.0 * x1 + 2.0 * y1 - math.sqrt(
            (2.0 * x1 + 2.0 * y1) ** 2 - 16.0 * ratio * (x1 * y1 - x2 * y2 - (x1 - x2 - x3) * y2)
        )) / 8.0
    if form == "U":
        if y1 >= y2:
            large_y, small_y, small_x = y1, y2, x3
        else:
            large_y, small_y, small_x = y2, y1, x2
        perimeter = 2.0 * x1 + 2.0 * y1 + 2.0 * y2 - 2.0 * y3
        area_term = x1 * large_y - (x1 - x2 - x3) * (large_y - y3) - small_x * (large_y - small_y)
        return (perimeter - math.sqrt(perimeter ** 2 - 16.0 * ratio * area_term)) / 8.0
    raise ValueError(f"Unknown structural form: {form!r}")
