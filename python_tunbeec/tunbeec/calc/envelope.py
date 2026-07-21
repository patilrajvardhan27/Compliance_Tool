"""Wall/Roof/Glass U-value resolution shared by the prescriptive and performance paths.

Ported from the (byte-for-byte identical) `setData()` methods of method/Prescriptive.java and
method/PerformanceOld.java.
"""
from __future__ import annotations

from tunbeec.data.reference import ReferenceData
from tunbeec.models import BuildingInput


def resolve_construction_u(ref: ReferenceData, bi: BuildingInput, kind: str, name: str) -> float:
    user_entries = bi.user_constructions_wall if kind == "Wall" else bi.user_constructions_roof
    entry = ref.find_construction(kind, name, {c.user_name: c for c in user_entries})
    if entry is None:
        raise ValueError(f"Unknown {kind} construction: {name!r}")
    if entry.type == "LAYERS":
        user_layers = bi.user_layers_wall if kind == "Wall" else bi.user_layers_roof
        layer = ref.find_layer(kind, entry.layer_name, {l.user_name: l for l in user_layers})
        if layer is None:
            raise ValueError(f"Unknown {kind} layer: {entry.layer_name!r}")
        return layer.u_value
    return entry.u_value


def resolve_glass_props(ref: ReferenceData, bi: BuildingInput) -> dict[str, tuple[float, float, float]]:
    """glass_type name -> (glass_conduct [W/m2.K], sc, vt), for every glass type used in window_rows."""
    props: dict[str, tuple[float, float, float]] = {}
    user_glass_by_name = {g.user_name: g for g in bi.user_glass}
    for row in bi.window_rows:
        if not row.glass_type or row.glass_type in props:
            continue
        g = ref.find_glass(row.glass_type, user_glass_by_name)
        if g is not None:
            props[row.glass_type] = (g.glass_conduct, g.sc, g.vt)
    return props
