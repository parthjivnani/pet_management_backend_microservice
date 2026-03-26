import re
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from core.database import get_database
from core.response import ApiResponse
from core.messages import (
    PET_CREATED_SUCCESSFULLY,
    PET_FETCHED_SUCCESSFULLY,
    PET_UPDATED_SUCCESSFULLY,
    PET_DELETED_SUCCESSFULLY,
    PET_NOT_FOUND,
)
from schema.pet import CreatePet, UpdatePet


def doc_to_pet(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


async def get_pets(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    species: str | None = None,
    breed: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    status: str | None = None,
) -> ApiResponse:
    db = get_database()
    skip = (page - 1) * limit
    match = {"isDeleted": {"$ne": True}}
    if status == "all":
        pass
    elif status:
        match["status"] = status
    else:
        match["status"] = "Available"
    if species:
        match["species"] = re.compile(re.escape(species), re.I)
    if breed:
        match["breed"] = re.compile(re.escape(breed), re.I)
    if search:
        match["$or"] = [
            {"name": re.compile(re.escape(search), re.I)},
            {"breed": re.compile(re.escape(search), re.I)},
        ]
    if age_min is not None:
        match.setdefault("age", {})["$gte"] = age_min
    if age_max is not None:
        match.setdefault("age", {})["$lte"] = age_max
    # Normalize age match if it became {"$gte": x, "$lte": y}
    if isinstance(match.get("age"), dict):
        pass
    cursor = db.pets.find(match).sort("createdOn", -1).skip(skip).limit(limit)
    list_ = []
    async for doc in cursor:
        list_.append(doc_to_pet(dict(doc)))
    total = await db.pets.count_documents(match)
    result = {"list": list_, "total": total, "page": page, "limit": limit, "totalPages": (total + limit - 1) // limit}
    return ApiResponse(statusCode=200, success=True, message=PET_FETCHED_SUCCESSFULLY, result=result)


async def get_pet_by_id(id: str) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=PET_NOT_FOUND)
    doc = await db.pets.find_one({"_id": oid, "isDeleted": {"$ne": True}})
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=PET_NOT_FOUND)
    return ApiResponse(statusCode=200, success=True, message=PET_FETCHED_SUCCESSFULLY, result=doc_to_pet(dict(doc)))


async def create_pet(body: CreatePet) -> ApiResponse:
    db = get_database()
    now = datetime.utcnow()
    doc = {
        "name": body.name,
        "species": body.species,
        "breed": body.breed,
        "age": body.age,
        "description": body.description or "",
        "imageUrl": body.imageUrl or "",
        "status": "Available",
        "isDeleted": False,
        "createdOn": now,
        "modifiedOn": now,
    }
    r = await db.pets.insert_one(doc)
    doc["_id"] = r.inserted_id
    return ApiResponse(statusCode=201, success=True, message=PET_CREATED_SUCCESSFULLY, result=doc_to_pet(dict(doc)))


async def update_pet(id: str, body: UpdatePet) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=PET_NOT_FOUND)
    updates = {"modifiedOn": datetime.utcnow()}
    if body.name is not None:
        updates["name"] = body.name
    if body.species is not None:
        updates["species"] = body.species
    if body.breed is not None:
        updates["breed"] = body.breed
    if body.age is not None:
        updates["age"] = body.age
    if body.description is not None:
        updates["description"] = body.description
    if body.imageUrl is not None:
        updates["imageUrl"] = body.imageUrl
    if body.status is not None:
        updates["status"] = body.status
    doc = await db.pets.find_one_and_update(
        {"_id": oid, "isDeleted": {"$ne": True}},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=PET_NOT_FOUND)
    return ApiResponse(statusCode=200, success=True, message=PET_UPDATED_SUCCESSFULLY, result=doc_to_pet(dict(doc)))


async def delete_pet(id: str) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=PET_NOT_FOUND)
    doc = await db.pets.find_one_and_update(
        {"_id": oid, "isDeleted": {"$ne": True}},
        {"$set": {"isDeleted": True, "modifiedOn": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=PET_NOT_FOUND)
    return ApiResponse(statusCode=200, success=True, message=PET_DELETED_SUCCESSFULLY, result=doc_to_pet(dict(doc)))
