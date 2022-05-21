from doctest import Example
import math
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from uuid import UUID
import utils.regex as rgx


class UserCreateRequest(BaseModel):
    msisdn: str= Field(..., regex=r'^\d{8,15}$')
    name: str = Field(..., max_length=120, example="Ahmed Shahwan")
    password: str = Field(..., max_length=40, example= "So secret")
    email: EmailStr | None = Field(None, example= "ahmed.shahwan@startappz.com" )
    profile_pic_url: HttpUrl | None = Field(None, example="https://example.com/fake_pic.jpg")
    otp_confirmation: str = Field(..., max_length=30, example= "123456")

   
class UserUpdateRequest(BaseModel):
    name: str = Field(None, max_length=120)
    password: str = Field(None, max_length=40)
    profile_pic_url: HttpUrl = Field(None)
    email: EmailStr = Field(None)
