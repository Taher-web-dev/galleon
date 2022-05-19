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
    msisdn: str = Field(..., regex=rgx.MSISDN)
    email: Optional[str] = Field(None, regex=rgx.EMAIL)
    profile_pic_url: Optional[str] = Field(None, regex=rgx.URL)

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id": 1,
                    "name": "jhone",
                    "msisdn": "599196408674300",
                    "email": "jhone@gmail.com",
                    "profile_pic_url": "https://pic.com",
                },
            }
        }
