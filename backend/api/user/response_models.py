from typing import Optional
from pydantic import BaseModel, Field
from utils.api_responses import Status, ApiResponse, Error
import utils.regex as rgx
import api.user.app_errors as err


class Tokens(BaseModel):
    refresh_token: str
    access_token: str

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "refresh_token": "ey...3kc",
                    "access_token": "ey...OLc",
                },
            }
        }


class LoginResponse(ApiResponse):
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
    id: int
    name: str
    msisdn: str = Field(..., regex=rgx.MSISDN, max_length=20)
    email: str | None = Field(None, regex=rgx.EMAIL, max_length=40)
    profile_pic_url: str | None = Field(None, regex=rgx.URL)


class UserProfileResponse(ApiResponse):
    data: UserProfile

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id": 1,
                    "name": "Ahmed Shahwan",
                    "msisdn": "12345678933",
                    "email": "ahmed.shahwan@startappz.com",
                    "profile_pic_url": "https://example.com/fake_pic.jpg",
                },
            }
        }
