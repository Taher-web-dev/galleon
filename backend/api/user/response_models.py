from typing import Optional
from pydantic import BaseModel, Field
from utils.api_responses import Status, ApiResponse, Error
import utils.regex as rgx
import api.user.app_errors as err


class Tokens(BaseModel):
    refresh_token: str
    access_token: str


class LoginResponse(ApiResponse):
    data: Tokens


class UserExistsErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.USER_EXISTS_ERROR


class InvalidOtpErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_OTP_ERROR


class InvalidTokenErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_TOKEN_ERROR


class InvalidCredentialsErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_CREDENTIALS_ERROR


class UserProfile(BaseModel):
    id: int
    name: str
    msisdn: str = Field(..., regex=rgx.MSISDN)
    email: Optional[str] = Field(None, regex=rgx.EMAIL)
    profile_pic_url: Optional[str] = Field(None, regex=rgx.URL)
