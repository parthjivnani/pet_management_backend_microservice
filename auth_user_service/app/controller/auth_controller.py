from datetime import datetime
from bson import ObjectId
from core.database import get_database
from core.response import ApiResponse
from core.messages import (
    ACCOUNT_NOT_EXIST,
    ACCOUNT_DEACTIVATED,
    INCORRECT_PASSWORD,
    LOGIN_SUCCESS,
    SIGNUP_SUCCESS,
    EMAIL_EXIST,
    EMAIL_INVALID,
    PASSWORD_CHANGE_SUCESSFULLY,
    FORGOT_PASSWORD_LINK_EXPIRED,
    FORGOT_PASSWORD_LINK_SEND,
    INAVLID_TOKEN,
    UNAUTHORIZED,
)
from schema.user import UserRegister, UserLogin, ForgotPasswordBody, ResetPasswordBody, SendVerificationBody
from utils.jwt import create_access_token, decode_token
from utils.password import hash_password, verify_password


def _to_json_serializable(obj):
    """Convert dict values (datetime, ObjectId) to JSON-serializable form."""
    if isinstance(obj, dict):
        return {k: _to_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_serializable(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.isoformat() + "Z" if obj.tzinfo is None else obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj


def user_to_dict(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    doc.pop("password", None)
    return _to_json_serializable(doc)


async def register_user(body: UserRegister) -> ApiResponse:
    db = get_database()
    existing = await db.users.find_one({"email": body.email})
    if existing:
        return ApiResponse(statusCode=400, success=False, message=EMAIL_EXIST)
    count = await db.users.count_documents({})
    role = "admin" if count == 0 else "user"
    user = {
        "firstName": body.firstName,
        "lastName": body.lastName,
        "email": body.email,
        "password": hash_password(body.password),
        "role": role,
        "isActive": True,
        "isDeleted": False,
        "isPasswordReset": False,
        "createdOn": datetime.utcnow(),
        "modifiedOn": datetime.utcnow(),
    }
    result = await db.users.insert_one(user)
    user["_id"] = result.inserted_id
    out = user_to_dict(dict(user))
    return ApiResponse(statusCode=201, success=True, message=SIGNUP_SUCCESS, result=out)


async def login_user(body: UserLogin) -> ApiResponse:
    db = get_database()
    user = await db.users.find_one({"email": body.email})
    if not user:
        return ApiResponse(statusCode=403, success=False, message=ACCOUNT_NOT_EXIST)
    if not user.get("isActive", True) or user.get("isDeleted", False):
        return ApiResponse(statusCode=403, success=False, message=ACCOUNT_DEACTIVATED)
    if not verify_password(body.password, user["password"]):
        return ApiResponse(statusCode=403, success=False, message=INCORRECT_PASSWORD)
    token = create_access_token({
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "user"),
    })
    out = user_to_dict(dict(user))
    return ApiResponse(statusCode=200, success=True, message=LOGIN_SUCCESS, result={"user": out, "token": token})


async def validate_token(authorization: str) -> ApiResponse:
    if not authorization or not authorization.startswith("Bearer "):
        return ApiResponse(statusCode=401, success=False, message=UNAUTHORIZED)
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return ApiResponse(statusCode=401, success=False, message=UNAUTHORIZED)
    user_id = payload.get("id")
    email = payload.get("email")
    if not user_id:
        return ApiResponse(statusCode=401, success=False, message=UNAUTHORIZED)
    db = get_database()
    try:
        oid = ObjectId(user_id) if len(user_id) == 24 else user_id
    except Exception:
        oid = user_id
    user = await db.users.find_one({"_id": oid, "isDeleted": {"$ne": True}})
    if not user or str(user["_id"]) != user_id:
        return ApiResponse(statusCode=401, success=False, message=UNAUTHORIZED)
    return ApiResponse(statusCode=200, success=True, message="", result=payload)


async def send_verification_link(body: SendVerificationBody) -> ApiResponse:
    db = get_database()
    user = await db.users.find_one({"email": body.email})
    if not user:
        return ApiResponse(statusCode=404, success=False, message=EMAIL_INVALID)
    await db.users.update_one({"email": body.email}, {"$set": {"isPasswordReset": False, "modifiedOn": datetime.utcnow()}})
    token = create_access_token(
        {"userId": str(user["_id"]), "email": user["email"], "firstName": user.get("firstName"), "lastName": user.get("lastName")},
        expire_minutes=30,
    )
    # In production: send email with f"{configs.SITE_URL}/{body.path}/{token}"
    return ApiResponse(statusCode=200, success=True, message=FORGOT_PASSWORD_LINK_SEND)


async def forgot_password(password: str, email: str) -> ApiResponse:
    db = get_database()
    user = await db.users.find_one({"email": email})
    if not user or user.get("isPasswordReset"):
        return ApiResponse(statusCode=403, success=False, message=FORGOT_PASSWORD_LINK_EXPIRED)
    await db.users.update_one(
        {"email": email},
        {"$set": {"password": hash_password(password), "isPasswordReset": True, "modifiedOn": datetime.utcnow()}},
    )
    return ApiResponse(statusCode=200, success=True, message=PASSWORD_CHANGE_SUCESSFULLY)


async def reset_password_with_token(body: ResetPasswordBody) -> ApiResponse:
    if not body.token or not body.password:
        return ApiResponse(statusCode=400, success=False, message="Token and password are required.")
    payload = decode_token(body.token)
    if not payload:
        return ApiResponse(statusCode=401, success=False, message=INAVLID_TOKEN)
    email = payload.get("email")
    if not email:
        return ApiResponse(statusCode=401, success=False, message=INAVLID_TOKEN)
    db = get_database()
    user = await db.users.find_one({"email": email})
    if not user or user.get("isPasswordReset"):
        return ApiResponse(statusCode=403, success=False, message=FORGOT_PASSWORD_LINK_EXPIRED)
    await db.users.update_one(
        {"email": email},
        {"$set": {"password": hash_password(body.password), "isPasswordReset": True, "modifiedOn": datetime.utcnow()}},
    )
    return ApiResponse(statusCode=200, success=True, message=PASSWORD_CHANGE_SUCESSFULLY)
