from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from controller.species_controller import get_species, get_species_by_id, create_species, update_species, delete_species
from middlewares.auth import require_admin
from schema.species import CreateSpecies, UpdateSpecies
from core.response import ApiResponse

router = APIRouter(prefix="/species", tags=["species"])


def with_status(r: ApiResponse) -> JSONResponse:
    return JSONResponse(status_code=r.statusCode, content=r.model_dump(mode="json"))


@router.get("", dependencies=[Depends(require_admin)])
async def list_species(page: int = 1, limit: int = 100):
    return with_status(await get_species(page=page, limit=limit))


@router.get("/{id}", dependencies=[Depends(require_admin)])
async def get_one(id: str):
    return with_status(await get_species_by_id(id))


@router.post("", dependencies=[Depends(require_admin)])
async def create(body: CreateSpecies):
    return with_status(await create_species(body))


@router.put("/{id}", dependencies=[Depends(require_admin)])
async def update(id: str, body: UpdateSpecies):
    return with_status(await update_species(id, body))


@router.delete("/{id}", dependencies=[Depends(require_admin)])
async def delete(id: str):
    return with_status(await delete_species(id))
