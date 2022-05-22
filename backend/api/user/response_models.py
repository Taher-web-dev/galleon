from typing import Any
from pydantic import BaseModel, Field
from utils.api_responses import Status, ApiResponse, Error
import utils.regex as rgx
import api.user.app_errors as err


class Tokens(BaseModel):
    refresh_token: str = Field(..., example="ey...3kc")
    access_token: str = Field(..., example="ey...OLc")


class TokensResponse(ApiResponse):
    data: Tokens


class UserExistsErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.USER_EXISTS


class InvalidOtpErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_OTP


class InvalidTokenErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_TOKEN


class InvalidCredentialsErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_CREDENTIALS


class UserProfile(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Ahmed Shahwan")
    msisdn: str = Field(..., regex=rgx.MSISDN, max_length=20, example="12345678933")
    email: str | None = Field(
        None, regex=rgx.EMAIL, max_length=40, example="https://example.com/fake_pic.jpg"
    )
    profile_pic_url: str | None = Field(None, regex=rgx.URL)


class UserProfileResponse(ApiResponse):
    data: UserProfile
