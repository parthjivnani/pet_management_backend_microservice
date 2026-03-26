from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from core.database import get_database
from core.response import ApiResponse
from core.messages import (
    ADOPTION_APPLICATION_SUBMITTED,
    ADOPTION_FETCHED_SUCCESSFULLY,
    ADOPTION_APPROVED,
    ADOPTION_REJECTED,
    ADOPTION_NOT_FOUND,
    PET_NOT_AVAILABLE,
    ALREADY_APPLIED,
    INTERNAL_SERVER,
)
from schema.adoption import ApplyAdoption


def doc_to_adoption(doc: dict) -> dict:
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    if "pet" in doc and isinstance(doc["pet"], dict):
        if "_id" in doc["pet"]:
            doc["pet"]["id"] = str(doc["pet"].pop("_id"))
    elif "pet" in doc:
        doc["pet"] = str(doc["pet"]) if doc["pet"] else None
    if "user" in doc and isinstance(doc["user"], dict) and "_id" in doc["user"]:
        doc["user"]["id"] = str(doc["user"].pop("_id"))
    elif "user" in doc and not isinstance(doc["user"], dict):
        doc["user"] = str(doc["user"]) if doc["user"] else None
    return doc


async def apply_adoption(user_id: str, body: ApplyAdoption) -> ApiResponse:
    db = get_database()
    try:
        pet_oid = ObjectId(body.petId)
    except Exception:
        return ApiResponse(statusCode=400, success=False, message=PET_NOT_AVAILABLE)
    pet = await db.pets.find_one({"_id": pet_oid, "isDeleted": {"$ne": True}, "status": "Available"})
    if not pet:
        return ApiResponse(statusCode=500, success=False, message=PET_NOT_AVAILABLE)
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        user_oid = user_id
    existing = await db.adoptions.find_one({"pet": pet_oid, "user": user_oid, "status": "Pending"})
    if existing:
        return ApiResponse(statusCode=500, success=False, message=ALREADY_APPLIED)
    now = datetime.utcnow()
    doc = {"pet": pet_oid, "user": user_oid, "status": "Pending", "message": body.message or "", "createdOn": now, "modifiedOn": now}
    r = await db.adoptions.insert_one(doc)
    doc["_id"] = r.inserted_id
    # Populate pet and user for response
    doc["pet"] = {**dict(pet), "id": str(pet["_id"])}
    doc["pet"].pop("_id", None)
    user_doc = await db.users.find_one({"_id": user_oid})
    doc["user"] = {"firstName": user_doc.get("firstName"), "lastName": user_doc.get("lastName"), "email": user_doc.get("email"), "id": str(user_oid)} if user_doc else str(user_oid)
    return ApiResponse(statusCode=201, success=True, message=ADOPTION_APPLICATION_SUBMITTED, result=doc_to_adoption(doc))


async def get_my_applications(user_id: str) -> ApiResponse:
    db = get_database()
    try:
        user_oid = ObjectId(user_id)
    except Exception:
        user_oid = user_id
    cursor = db.adoptions.find({"user": user_oid}).sort("createdOn", -1)
    list_ = []
    async for doc in cursor:
        d = dict(doc)
        if d.get("pet"):
            pet = await db.pets.find_one({"_id": d["pet"]})
            if pet:
                d["pet"] = {**dict(pet), "id": str(pet["_id"])}
                d["pet"].pop("_id", None)
            else:
                d["pet"] = str(d["pet"])
        list_.append(doc_to_adoption(d))
    return ApiResponse(statusCode=200, success=True, message=ADOPTION_FETCHED_SUCCESSFULLY, result=list_)


async def get_all(page: int = 1, limit: int = 20, status: str | None = None) -> ApiResponse:
    db = get_database()
    skip = (page - 1) * limit
    match = {}
    if status:
        match["status"] = status
    cursor = db.adoptions.find(match).sort("createdOn", -1).skip(skip).limit(limit)
    list_ = []
    async for doc in cursor:
        d = dict(doc)
        if d.get("pet"):
            pet = await db.pets.find_one({"_id": d["pet"]})
            d["pet"] = {**dict(pet), "id": str(pet["_id"])} if pet else str(d["pet"])
            if pet and "_id" in d["pet"]:
                d["pet"].pop("_id", None)
        if d.get("user"):
            user = await db.users.find_one({"_id": d["user"]})
            d["user"] = {"firstName": user.get("firstName"), "lastName": user.get("lastName"), "email": user.get("email"), "id": str(d["user"])} if user else str(d["user"])
        list_.append(doc_to_adoption(d))
    total = await db.adoptions.count_documents(match)
    result = {"list": list_, "total": total, "page": page, "limit": limit, "totalPages": (total + limit - 1) // limit}
    return ApiResponse(statusCode=200, success=True, message=ADOPTION_FETCHED_SUCCESSFULLY, result=result)


async def get_by_id(id: str) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=ADOPTION_NOT_FOUND)
    doc = await db.adoptions.find_one({"_id": oid})
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=ADOPTION_NOT_FOUND)
    d = dict(doc)
    if d.get("pet"):
        pet = await db.pets.find_one({"_id": d["pet"]})
        d["pet"] = {**dict(pet), "id": str(pet["_id"])} if pet else str(d["pet"])
        if isinstance(d["pet"], dict) and "_id" in d["pet"]:
            d["pet"].pop("_id", None)
    if d.get("user"):
        user = await db.users.find_one({"_id": d["user"]})
        d["user"] = {"firstName": user.get("firstName"), "lastName": user.get("lastName"), "email": user.get("email"), "id": str(d["user"])} if user else str(d["user"])
    return ApiResponse(statusCode=200, success=True, message=ADOPTION_FETCHED_SUCCESSFULLY, result=doc_to_adoption(d))


async def approve(id: str) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=ADOPTION_NOT_FOUND)
    doc = await db.adoptions.find_one_and_update(
        {"_id": oid},
        {"$set": {"status": "Approved", "modifiedOn": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=ADOPTION_NOT_FOUND)
    await db.pets.update_one({"_id": doc["pet"]}, {"$set": {"status": "Adopted", "modifiedOn": datetime.utcnow()}})
    d = dict(doc)
    if d.get("pet"):
        pet = await db.pets.find_one({"_id": d["pet"]})
        d["pet"] = {**dict(pet), "id": str(pet["_id"])} if pet else str(d["pet"])
        if isinstance(d["pet"], dict):
            d["pet"].pop("_id", None)
    if d.get("user"):
        user = await db.users.find_one({"_id": d["user"]})
        d["user"] = {"firstName": user.get("firstName"), "lastName": user.get("lastName"), "email": user.get("email"), "id": str(d["user"])} if user else str(d["user"])
    return ApiResponse(statusCode=200, success=True, message=ADOPTION_APPROVED, result=doc_to_adoption(d))


async def reject(id: str) -> ApiResponse:
    db = get_database()
    try:
        oid = ObjectId(id)
    except Exception:
        return ApiResponse(statusCode=404, success=False, message=ADOPTION_NOT_FOUND)
    doc = await db.adoptions.find_one_and_update(
        {"_id": oid},
        {"$set": {"status": "Rejected", "modifiedOn": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        return ApiResponse(statusCode=404, success=False, message=ADOPTION_NOT_FOUND)
    d = dict(doc)
    if d.get("pet"):
        pet = await db.pets.find_one({"_id": d["pet"]})
        d["pet"] = {**dict(pet), "id": str(pet["_id"])} if pet else str(d["pet"])
        if isinstance(d["pet"], dict):
            d["pet"].pop("_id", None)
    if d.get("user"):
        user = await db.users.find_one({"_id": d["user"]})
        d["user"] = {"firstName": user.get("firstName"), "lastName": user.get("lastName"), "email": user.get("email"), "id": str(d["user"])} if user else str(d["user"])
    return ApiResponse(statusCode=200, success=True, message=ADOPTION_REJECTED, result=doc_to_adoption(d))
