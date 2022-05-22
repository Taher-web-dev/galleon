from doctest import Example
import math
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from uuid import UUID
import utils.regex as rgx


class UserCreateRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN)
    name: str = Field(..., max_length=120, example="Ahmed Shahwan")
    password: str = Field(..., regex=rgx.PASSWORD, max_length=40, example="So secret")
    email: EmailStr | None = Field(None, example="ahmed.shahwan@startappz.com")
    profile_pic_url: HttpUrl | None = Field(
        None, example="https://example.com/fake_pic.jpg"
    )
    otp_confirmation: str = Field(..., max_length=30, example="1234")


class UserUpdateRequest(BaseModel):
    name: str = Field(None, max_length=120, example="Ahmed Shahwan")
    password: str = Field(None, regex=rgx.PASSWORD, max_length=40, example="So secret")
    profile_pic_url: HttpUrl = Field(None, example="https://example.com/fake_pic.jpg")
    email: EmailStr = Field(None, example="ahmed.shahwan@startappz.com")
