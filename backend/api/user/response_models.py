from typing import Any, Dict
from pydantic import BaseModel, Field
from utils.api_responses import Status, ApiResponse, Error
import utils.regex as rgx


USER_EXISTS_ERROR = Error(
    type="user", code=201, message="Sorry the msisdn is already registered."
)
INVALID_OTP_ERROR = Error(
    type="otp",
    code=202,
    message="The confirmation provided is not valid please try again.",
)
INVALID_CREDENTIALS_ERROR = Error(
    type="auth",
    code=203,
    message="Invalid credentials",
)
INVALID_TOKEN_ERROR = Error(
    type="auth",
    code=204,
    message="Invalid token",
)


class LoginSuccessResponseBody(BaseModel):
    refresh_token: str
    access_token: str


class LoginSuccessResponse(BaseModel):
    status: Status = Status.success
    data: LoginSuccessResponseBody


class UserExistsErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [USER_EXISTS_ERROR]


class InvalidOtpErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_OTP_ERROR]


class InvalidTokenErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_TOKEN_ERROR]


class InvalidCredentialsErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_CREDENTIALS_ERROR]


class UserProfile(BaseModel):
    id: int
    name: str
    msisdn: str = Field(..., regex=rgx.MSISDN)
    email: str | None = None
    password: str | None = None
    profile_pic_url: str | None = None
