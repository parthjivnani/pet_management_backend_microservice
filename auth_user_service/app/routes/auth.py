from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from schema.user import UserRegister, UserLogin, ForgotPasswordBody, ResetPasswordBody, SendVerificationBody
from controller.auth_controller import (
    register_user,
    login_user,
    validate_token,
    send_verification_link,
    forgot_password,
    reset_password_with_token,
)
from core.response import ApiResponse
from utils.jwt import decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


def with_status(r: ApiResponse) -> JSONResponse:
    return JSONResponse(status_code=r.statusCode, content=r.model_dump())


def get_current_user_email(authorization: str = Header(..., alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload.get("email")


@router.get("/test")
async def test():
    return with_status(ApiResponse(statusCode=200, success=True, message="This is a test routing!"))


@router.post("/register")
async def signup(body: UserRegister):
    return with_status(await register_user(body))


@router.post("/login")
async def login(body: UserLogin):
    return with_status(await login_user(body))


@router.get("/validate-token")
async def validate(authorization: str = Header(..., alias="Authorization")):
    return with_status(await validate_token(authorization))


@router.post("/send-verification-link")
async def send_verification(body: SendVerificationBody):
    return with_status(await send_verification_link(body))


@router.post("/forgot-password")
async def forgot_password_route(body: ForgotPasswordBody, email: str = Depends(get_current_user_email)):
    return with_status(await forgot_password(body.password, email))


@router.post("/reset-password")
async def reset_password(body: ResetPasswordBody):
    return with_status(await reset_password_with_token(body))
