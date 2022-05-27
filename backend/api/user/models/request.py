from pydantic import BaseModel, Field, HttpUrl, EmailStr
import utils.regex as rgx


class UserCreateRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN, max_length=20, example="12345678933")
    name: str = Field(..., regex=rgx.TITLE, max_length=120, example="Ahmed Shahwan")
    password: str = Field(
        None, regex=rgx.PASSWORD, max_length=40, example="$aZeqsdwxc23"
    )
    email: EmailStr | None = Field(None, example="jhone@gmail.com")
    profile_pic_url: HttpUrl | None = Field(
        None, example="https://example.com/fake_pic.jpg"
    )
    otp_confirmation: str = Field(
        ..., regex=rgx.STRING, max_length=30, example="xwerWerQASGASAWasd"
    )


class UserUpdateRequest(BaseModel):
    name: str = Field(None, regex=rgx.TITLE, max_length=120, example="jhone")
    password: str = Field(
        None, regex=rgx.PASSWORD, max_length=40, example="$aZeqsdwxc23"
    )
    email: EmailStr | None = Field(None, example="jhone@gmail.com")
    profile_pic_url: HttpUrl | None = Field(
        None, example="https://example.com/fake_pic.jpg"
    )
    otp_confirmation: str = Field(
        ..., regex=rgx.STRING, max_length=30, example="xwerWerQASGASAWasd"
    )
