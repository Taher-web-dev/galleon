from doctest import Example
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from sqlalchemy import null
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
    id: int = Field(..., example= 1)
    name: str = Field(..., example= "Ahmed Shahwan")
    msisdn: str = Field(..., regex= rgx.MSISDN, example= "12345678933")
    email: EmailStr | None = Field(None, example="ahmed.shahwan@startappz.com")
    profile_pic_url: HttpUrl | None = Field(None, example="https://example.com/fake_pic.jpg")


class UserProfileResponse(ApiResponse):
    data: UserProfile
    status: Status = Field(Status.success, example='success')
    error: None = Field(None, example= null)

class ValidationErrorResponse(ApiResponse):
  status: Status = Status.failed
  error= Error(type="validation", code="422", message="Body request data is not valid!")
  data : None = Field(None, example=null)