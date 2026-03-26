from fastapi import APIRouter
from routes.adoption import router as adoption_router

router = APIRouter()
router.include_router(adoption_router)
