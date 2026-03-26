from pydantic import BaseModel, Field


class ApplyAdoption(BaseModel):
    petId: str = Field(..., min_length=1)
    message: str = Field(default="", max_length=500)
