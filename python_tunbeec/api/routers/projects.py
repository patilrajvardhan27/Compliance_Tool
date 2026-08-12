from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from api import convert, schemas
from api.deps import get_reference
from tunbeec.app_state import populate_space_rows
from tunbeec.data.project import load_project, save_project
from tunbeec.data.reference import ReferenceData

router = APIRouter(prefix="/api/projects", tags=["projects"])


# The .tct file lives on the user's machine (browser file pickers); the server only converts
# between JSON and file bytes, stateless -- it never stores a project.
@router.post("/serialize")
def serialize_project(req: schemas.SaveProjectRequest) -> Response:
    """BuildingInput JSON -> .tct (SQLite) bytes, for the browser to save to the user's disk."""
    bi = convert.building_input_from_schema(req.building_input)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "project.tct"
        save_project(path, bi)
        data = path.read_bytes()
    return Response(content=data, media_type="application/octet-stream")


@router.post("/parse", response_model=schemas.BuildingInputSchema)
async def parse_project(
    request: Request, ref: ReferenceData = Depends(get_reference)
) -> schemas.BuildingInputSchema:
    """.tct (SQLite) bytes uploaded from the user's disk -> BuildingInput JSON."""
    data = await request.body()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "project.tct"
        path.write_bytes(data)
        try:
            bi = load_project(path)
            populate_space_rows(bi, ref)  # tblSpaceCond is never persisted; re-derive on open
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Unable to open file: {e}") from e
    return convert.schema_from_building_input(bi)
