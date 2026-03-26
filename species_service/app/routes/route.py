from fastapi import APIRouter
from routes.species import router as species_router

router = APIRouter()
router.include_router(species_router)
