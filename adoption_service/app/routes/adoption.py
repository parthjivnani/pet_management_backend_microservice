from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from controller.adoption_controller import apply_adoption, get_my_applications, get_all, get_by_id, approve, reject
from middlewares.auth import get_current_user, require_admin
from schema.adoption import ApplyAdoption
from core.response import ApiResponse

router = APIRouter(prefix="/adoptions", tags=["adoptions"])


def with_status(r: ApiResponse) -> JSONResponse:
    return JSONResponse(status_code=r.statusCode, content=r.model_dump())


@router.post("/", dependencies=[Depends(get_current_user)])
async def apply(body: ApplyAdoption, user: dict = Depends(get_current_user)):
    return with_status(await apply_adoption(user["id"], body))


@router.get("/my", dependencies=[Depends(get_current_user)])
async def my_applications(user: dict = Depends(get_current_user)):
    return with_status(await get_my_applications(user["id"]))


@router.get("/", dependencies=[Depends(require_admin)])
async def list_all(page: int = 1, limit: int = 20, status: str | None = None):
    return with_status(await get_all(page=page, limit=limit, status=status))


@router.get("/{id}", dependencies=[Depends(require_admin)])
async def get_one(id: str):
    return with_status(await get_by_id(id))


@router.patch("/{id}/approve", dependencies=[Depends(require_admin)])
async def approve_one(id: str):
    return with_status(await approve(id))


@router.patch("/{id}/reject", dependencies=[Depends(require_admin)])
async def reject_one(id: str):
    return with_status(await reject(id))
