from fastapi import APIRouter
from routes.pet import router as pet_router

router = APIRouter()
router.include_router(pet_router)
