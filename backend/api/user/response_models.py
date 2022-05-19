from typing import Optional
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


class Tokens(BaseModel):
    refresh_token: str
    access_token: str


class LoginResponse(ApiResponse):
    data: Tokens


class UserExistsErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = USER_EXISTS_ERROR


class InvalidOtpErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_OTP_ERROR


class InvalidTokenErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_TOKEN_ERROR


class InvalidCredentialsErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_CREDENTIALS_ERROR


class UserProfile(BaseModel):
    id: int
    name: str
    msisdn: str = Field(..., regex=rgx.MSISDN)
    email: Optional[str] = Field(None, regex=rgx.EMAIL)
    profile_pic_url: Optional[str] = Field(None, regex=rgx.URL)
