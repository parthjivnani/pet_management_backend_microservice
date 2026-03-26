from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from core.database import get_database
from core.response import ApiResponse
from core.messages import (
    SPECIES_CREATED_SUCCESSFULLY,
    SPECIES_FETCHED_SUCCESSFULLY,
    SPECIES_UPDATED_SUCCESSFULLY,
    SPECIES_DELETED_SUCCESSFULLY,
    SPECIES_NOT_FOUND,
    INTERNAL_SERVER,
)
from schema.species import CreateSpecies, UpdateSpecies


def doc_to_species(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


async def get_species(page: int = 1, limit: int = 100) -> ApiResponse:
    print(f"Fetching species with page={page} and limit={limit}")  # Debugging statement
    db = get_database()
    skip = (page - 1) * limit
    match = {"isDeleted": {"$ne": True}}
    cursor = db.species.find(match).sort("name", 1).skip(skip).limit(limit)
    list_ = []
    async for doc in cursor:
        list_.append(doc_to_species(dict(doc)))
    total = await db.species.count_documents(match)
    result = {"list": list_, "total": total, "page": page, "limit": limit, "totalPages": (total + limit - 1) // limit}
    print(f"Fetched {len(list_)} species {result}" )  # Debugging statement
    return ApiResponse(statusCode=200, success=True, message=SPECIES_FETCHED_SUCCESSFULLY, result=result)


async def get_species_by_id(id: str) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=SPECIES_NOT_FOUND)
    doc = await db.species.find_one({"_id": oid, "isDeleted": {"$ne": True}})
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=SPECIES_NOT_FOUND)
    return ApiResponse(statusCode=200, success=True, message=SPECIES_FETCHED_SUCCESSFULLY, result=doc_to_species(dict(doc)))


async def create_species(body: CreateSpecies) -> ApiResponse:
    db = get_database()
    now = datetime.utcnow()
    doc = {"name": body.name, "isDeleted": False, "createdOn": now, "modifiedOn": now}
    r = await db.species.insert_one(doc)
    doc["_id"] = r.inserted_id
    return ApiResponse(statusCode=201, success=True, message=SPECIES_CREATED_SUCCESSFULLY, result=doc_to_species(dict(doc)))


async def update_species(id: str, body: UpdateSpecies) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=SPECIES_NOT_FOUND)
    updates = {"modifiedOn": datetime.utcnow()}
    if body.name is not None:
        updates["name"] = body.name
    doc = await db.species.find_one_and_update({"_id": oid, "isDeleted": {"$ne": True}}, {"$set": updates}, return_document=ReturnDocument.AFTER)
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=SPECIES_NOT_FOUND)
    return ApiResponse(statusCode=200, success=True, message=SPECIES_UPDATED_SUCCESSFULLY, result=doc_to_species(dict(doc)))


async def delete_species(id: str) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=SPECIES_NOT_FOUND)
    doc = await db.species.find_one_and_update(
        {"_id": oid, "isDeleted": {"$ne": True}},
        {"$set": {"isDeleted": True, "modifiedOn": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=SPECIES_NOT_FOUND)
    return ApiResponse(statusCode=200, success=True, message=SPECIES_DELETED_SUCCESSFULLY, result=doc_to_species(dict(doc)))
