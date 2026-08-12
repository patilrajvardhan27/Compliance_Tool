"""Conversions between api/schemas.py (Pydantic, wire format) and tunbeec/models.py +
tunbeec/data/reference.py (plain dataclasses, the domain objects the calc pipeline consumes).

Field names match verbatim on both sides, so every conversion here is a straight copy -- no
renaming/remapping logic to maintain.
"""
from __future__ import annotations

from tunbeec.calc.performance_report import ClassRow, PerformanceReport
from tunbeec.calc.prescriptive import EnvelopeResult, PrescriptiveResult
from tunbeec.data.reference import ReferenceData
from tunbeec.models import (
    BuildingInput,
    ConstructionEntry,
    GlassEntry,
    LayerEntry,
    MaterialEntry,
    SpaceConditionRow,
    WindowAllocationRow,
)

from api import schemas


def building_input_from_schema(s: schemas.BuildingInputSchema) -> BuildingInput:
    bi = BuildingInput()
    for field in bi.__dataclass_fields__:
        if field in ("window_rows", "space_rows", "user_constructions_wall", "user_constructions_roof",
                     "user_layers_wall", "user_layers_roof", "user_materials", "user_glass"):
            continue
        setattr(bi, field, getattr(s, field))
    bi.window_rows = [WindowAllocationRow(**r.model_dump()) for r in s.window_rows]
    bi.space_rows = [SpaceConditionRow(**r.model_dump()) for r in s.space_rows]
    bi.user_constructions_wall = [ConstructionEntry(**c.model_dump()) for c in s.user_constructions_wall]
    bi.user_constructions_roof = [ConstructionEntry(**c.model_dump()) for c in s.user_constructions_roof]
    bi.user_layers_wall = [LayerEntry(**l.model_dump()) for l in s.user_layers_wall]
    bi.user_layers_roof = [LayerEntry(**l.model_dump()) for l in s.user_layers_roof]
    bi.user_materials = [MaterialEntry(**m.model_dump()) for m in s.user_materials]
    bi.user_glass = [GlassEntry(**g.model_dump()) for g in s.user_glass]
    return bi


def schema_from_building_input(bi: BuildingInput) -> schemas.BuildingInputSchema:
    data = {f: getattr(bi, f) for f in bi.__dataclass_fields__
            if f not in ("window_rows", "space_rows", "user_constructions_wall", "user_constructions_roof",
                          "user_layers_wall", "user_layers_roof", "user_materials", "user_glass")}
    data["window_rows"] = [schemas.WindowAllocationRowSchema(**vars(r)) for r in bi.window_rows]
    data["space_rows"] = [schemas.SpaceConditionRowSchema(**vars(r)) for r in bi.space_rows]
    data["user_constructions_wall"] = [schemas.ConstructionEntrySchema(**vars(c)) for c in bi.user_constructions_wall]
    data["user_constructions_roof"] = [schemas.ConstructionEntrySchema(**vars(c)) for c in bi.user_constructions_roof]
    data["user_layers_wall"] = [schemas.LayerEntrySchema(**vars(l)) for l in bi.user_layers_wall]
    data["user_layers_roof"] = [schemas.LayerEntrySchema(**vars(l)) for l in bi.user_layers_roof]
    data["user_materials"] = [schemas.MaterialEntrySchema(**vars(m)) for m in bi.user_materials]
    data["user_glass"] = [schemas.GlassEntrySchema(**vars(g)) for g in bi.user_glass]
    return schemas.BuildingInputSchema(**data)


def reference_snapshot(ref: ReferenceData) -> schemas.ReferenceSnapshot:
    return schemas.ReferenceSnapshot(
        bldg_types=[schemas.BldgTypeSchema(**vars(t)) for t in ref.bldg_types],
        bldg_locations=ref.bldg_locations,
        bldg_shapes=ref.bldg_shapes,
        bldg_systems=ref.bldg_systems,
        gui_defaults=ref.gui_defaults,
        constructions_wall={k: schemas.ConstructionEntrySchema(**vars(v)) for k, v in ref.constructions_wall.items()},
        constructions_roof={k: schemas.ConstructionEntrySchema(**vars(v)) for k, v in ref.constructions_roof.items()},
        layers_wall={k: schemas.LayerEntrySchema(**vars(v)) for k, v in ref.layers_wall.items()},
        layers_roof={k: schemas.LayerEntrySchema(**vars(v)) for k, v in ref.layers_roof.items()},
        materials={k: schemas.MaterialEntrySchema(**vars(v)) for k, v in ref.materials.items()},
        glass={k: schemas.GlassEntrySchema(**vars(v)) for k, v in ref.glass.items()},
    )


def prescriptive_result_schema(r: PrescriptiveResult) -> schemas.PrescriptiveResultSchema:
    return schemas.PrescriptiveResultSchema(
        climate=r.climate, bldg_zone=r.bldg_zone, x1=r.x1, x2=r.x2, grade=r.grade,
        code_thresholds=r.code_thresholds, ext_wall_u=r.ext_wall_u, roof_u=r.roof_u,
        glass_weighted_u=r.glass_weighted_u, glass_weighted_sc=r.glass_weighted_sc,
        rows=[schemas.EnvelopeResultSchema(**vars(row)) for row in r.rows],
        compliant=r.compliant, needs_performance_path=r.needs_performance_path,
        report_variant=r.report_variant,
    )


def performance_report_schema(r: PerformanceReport) -> schemas.PerformanceReportSchema:
    return schemas.PerformanceReportSchema(
        bldg_name=r.bldg_name, bldg_address=r.bldg_address, bldg_type=r.bldg_type,
        bldg_category=r.bldg_category, bldg_sector=r.bldg_sector, bldg_star=r.bldg_star,
        bldg_loc=r.bldg_loc,
        ext_wall_const_u=r.ext_wall_const_u, ext_wall_const_south_u=r.ext_wall_const_south_u,
        ext_wall_const_north_u=r.ext_wall_const_north_u, ext_wall_const_east_u=r.ext_wall_const_east_u,
        ext_wall_const_west_u=r.ext_wall_const_west_u, roof_const_u=r.roof_const_u,
        glass_u=r.glass_u, glass_sc=r.glass_sc,
        min_bec_th=r.min_bec_th, bldg_bec_th=r.bldg_bec_th, min_class=r.min_class,
        bldg_class=r.bldg_class, result=r.result,
        h_load=r.h_load, c_load=r.c_load, a_load=r.a_load,
        h_energy=r.h_energy, c_energy=r.c_energy, a_energy=r.a_energy,
        a_src_energy=r.a_src_energy, a_co2=r.a_co2,
        class_rows=[schemas.ClassRowSchema(**vars(cr)) for cr in r.class_rows],
    )
