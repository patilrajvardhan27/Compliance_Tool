from __future__ import annotations

from fastapi import APIRouter, Depends

from api import convert, schemas
from api.deps import get_reference
from tunbeec.app_state import apply_building_type_defaults, new_building_input
from tunbeec.calc.shape import calc_floor_area
from tunbeec.calc.uvalue import calc_resistance, calc_u_value_from_layers
from tunbeec.data.reference import ReferenceData

router = APIRouter(prefix="/api/building", tags=["building"])


@router.post("/new", response_model=schemas.BuildingInputSchema)
def create_new_building(ref: ReferenceData = Depends(get_reference)) -> schemas.BuildingInputSchema:
    bi = new_building_input(ref)
    return convert.schema_from_building_input(bi)


@router.post("/apply-type-defaults", response_model=schemas.BuildingInputSchema)
def apply_type_defaults(
    building_input: schemas.BuildingInputSchema, ref: ReferenceData = Depends(get_reference)
) -> schemas.BuildingInputSchema:
    bi = convert.building_input_from_schema(building_input)
    apply_building_type_defaults(bi, ref)
    return convert.schema_from_building_input(bi)


@router.post("/floor-area", response_model=schemas.FloorAreaResponse)
def floor_area(req: schemas.FloorAreaRequest) -> schemas.FloorAreaResponse:
    area = calc_floor_area(req.shape, req.x1, req.y1, req.x2, req.y2, req.x3, req.y3)
    return schemas.FloorAreaResponse(floor_area=area)


@router.post("/material-resistance", response_model=schemas.MaterialResistanceResponse)
def material_resistance(req: schemas.MaterialResistanceRequest) -> schemas.MaterialResistanceResponse:
    return schemas.MaterialResistanceResponse(resistance=calc_resistance(req.thickness, req.conductivity))


@router.post("/construction-uvalue", response_model=schemas.ConstructionUValueResponse)
def construction_uvalue(req: schemas.ConstructionUValueRequest) -> schemas.ConstructionUValueResponse:
    return schemas.ConstructionUValueResponse(u_value=calc_u_value_from_layers(req.resistances))
