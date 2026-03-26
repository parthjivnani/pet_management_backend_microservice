from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from controller.pet_controller import get_pets, get_pet_by_id, create_pet, update_pet, delete_pet
from middlewares.auth import require_admin
from schema.pet import CreatePet, UpdatePet
from core.response import ApiResponse

router = APIRouter(prefix="/pets", tags=["pets"])


def with_status(r: ApiResponse) -> JSONResponse:
    return JSONResponse(status_code=r.statusCode, content=r.model_dump())


@router.get("")
async def list_pets(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    species: str | None = None,
    breed: str | None = None,
    ageMin: int | None = None,
    ageMax: int | None = None,
    status: str | None = None,
):
    return with_status(await get_pets(page=page, limit=limit, search=search, species=species, breed=breed, age_min=ageMin, age_max=ageMax, status=status))


@router.get("/{id}")
async def get_one(id: str):
    return with_status(await get_pet_by_id(id))


@router.post("", dependencies=[Depends(require_admin)])
async def create(body: CreatePet):
    return with_status(await create_pet(body))


@router.put("/{id}", dependencies=[Depends(require_admin)])
async def update(id: str, body: UpdatePet):
    return with_status(await update_pet(id, body))


@router.delete("/{id}", dependencies=[Depends(require_admin)])
async def delete(id: str):
    return with_status(await delete_pet(id))
