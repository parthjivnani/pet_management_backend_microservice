from pydantic import BaseModel, Field


class CreateSpecies(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class UpdateSpecies(BaseModel):
    name: str | None = Field(None, max_length=100)
