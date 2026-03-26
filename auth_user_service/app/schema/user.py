from pydantic import BaseModel, Field, EmailStr


class UserRegister(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=200)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class ForgotPasswordBody(BaseModel):
    password: str = Field(..., min_length=6)


class ResetPasswordBody(BaseModel):
    token: str
    password: str = Field(..., min_length=6)


class SendVerificationBody(BaseModel):
    email: EmailStr
    path: str = Field(default="reset-password", max_length=100)
