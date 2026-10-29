from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from api import convert, schemas
from api.deps import get_reference
from tunbeec.app_state import populate_space_rows
from tunbeec.data.project import load_project, save_project
from tunbeec.data.reference import ReferenceData

router = APIRouter(prefix="/api/projects", tags=["projects"])
log = logging.getLogger("tunbeec.api")
MAX_PROJECT_BYTES = 20 * 1024 * 1024


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
    if len(data) > MAX_PROJECT_BYTES:
        raise HTTPException(status_code=413, detail="File is too large (20 MB max).")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "project.tct"
        path.write_bytes(data)
        try:
            bi = load_project(path)
            populate_space_rows(bi, ref)  # tblSpaceCond is never persisted; re-derive on open
        except Exception as e:
            log.exception("Could not open uploaded .tct file")
            raise HTTPException(
                status_code=400, detail="Unable to open this file. Make sure it is a TUNBEEC .tct project."
            ) from e
    return convert.schema_from_building_input(bi)
