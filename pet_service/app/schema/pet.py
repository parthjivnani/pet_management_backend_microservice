from pydantic import BaseModel, Field


class CreatePet(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    species: str = Field(..., max_length=50)
    breed: str = Field(..., max_length=50)
    age: int = Field(..., ge=0)
    description: str = Field(default="", max_length=1000)
    imageUrl: str = Field(default="")


class UpdatePet(BaseModel):
    name: str | None = Field(None, max_length=100)
    species: str | None = Field(None, max_length=50)
    breed: str | None = Field(None, max_length=50)
    age: int | None = Field(None, ge=0)
    description: str | None = Field(None, max_length=1000)
    imageUrl: str | None = None
    status: str | None = Field(None, pattern="^(Available|Adopted)$")
