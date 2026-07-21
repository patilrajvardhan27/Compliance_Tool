"""Material resistance / U-value helpers.

Ported from util/Resistance.java and util/Uvalue.java (identical implementations in the
original code -- both compute thermal resistance R = thickness / conductivity).
"""


def calc_resistance(thickness_m: float, conductivity: float) -> float:
    """R [m2.K/W] = thickness [m] / conductivity [W/m.K], rounded to 3 decimals like the Java version."""
    return round(thickness_m / conductivity, 3)


def calc_u_value_from_layers(resistances: list[float]) -> float:
    """Construction U-value [W/m2.K] = 1 / sum(R) across all material layers (GuiConst.txtCalcU)."""
    total_r = sum(resistances)
    if total_r <= 0:
        raise ValueError("Total resistance must be positive")
    return 1.0 / total_r
