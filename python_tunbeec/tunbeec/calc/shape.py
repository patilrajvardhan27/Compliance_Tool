"""Floor-area formulas per building shape.

Ported from vo/ShapeDimensionVo.java (calcFloorArea). Dimensions in meters, area in m2.
"""
import math

_POLYGON_HALF_ANGLE_DEG = {
    "Hexagon": 30.0,
    "Octagon": 22.0,
    "Decagon": 18.0,
    "Dodecagon": 15.0,
    "Hexadecagon": 11.0,
    "Octadecagon": 10.0,
}
_POLYGON_SIDES = {
    "Hexagon": 6,
    "Octagon": 8,
    "Decagon": 10,
    "Dodecagon": 12,
    "Hexadecagon": 16,
    "Octadecagon": 18,
}


def calc_floor_area(shape: str, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> float:
    if shape == "Rectangular":
        return x1 * y1
    if shape == "L-Shape":
        return x1 * y1 - (x1 - x2) * (y1 - y2)
    if shape == "T-Shape":
        return x1 * y1 - x2 * y2 - (x1 - x2 - x3) * y2
    if shape == "U-Shape":
        if y1 >= y2:
            large_y, small_y, small_x = y1, y2, x3
        else:
            large_y, small_y, small_x = y2, y1, x2
        return x1 * large_y - (x1 - x2 - x3) * (large_y - y3) - small_x * (large_y - small_y)
    if shape in _POLYGON_SIDES:
        n = _POLYGON_SIDES[shape]
        half_angle = math.radians(_POLYGON_HALF_ANGLE_DEG[shape])
        side = 2.0 * (y1 / 2.0) * math.sin(half_angle)
        return round(n * side ** 2 / (4.0 * math.tan(half_angle)))
    raise ValueError(f"Unknown building shape: {shape!r}")
