from pydantic import BaseModel, Field, HttpUrl, EmailStr
from api.models.data import Error, Status
from api.models.response import ApiResponse
import utils.regex as rgx
import api.user.models.errors as err


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


class InvalidRefreshTokenErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_REFRESH_TOKEN


class InvalidCredentialsErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_CREDENTIALS


class UserProfile(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Ahmed Shahwan")
    msisdn: str = Field(..., regex=rgx.MSISDN, max_length=20, example="12345678933")
    email: EmailStr | None = Field(None, example="ahmed.shahwan@startappz.com")
    profile_pic_url: HttpUrl | None = Field(
        None, example="https://example.com/fake_pic.jpg"
    )


class UserProfileResponse(ApiResponse):
    data: UserProfile


class ValidationErrorResponse(ApiResponse):
    status: Status = Status.failed
    error = Error(type="validation", code=422, message="Request body is not valid!")
