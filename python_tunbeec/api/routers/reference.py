from __future__ import annotations

from fastapi import APIRouter, Depends

from api import convert, schemas
from api.deps import get_reference
from tunbeec.data.reference import ReferenceData

router = APIRouter(prefix="/api/reference", tags=["reference"])


@router.get("", response_model=schemas.ReferenceSnapshot)
def get_reference_snapshot(ref: ReferenceData = Depends(get_reference)) -> schemas.ReferenceSnapshot:
    return convert.reference_snapshot(ref)
