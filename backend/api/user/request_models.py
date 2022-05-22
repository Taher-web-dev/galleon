from pydantic import BaseModel, Field
import utils.regex as rgx


class UserCreateRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN, max_length=20, example="12345678933")
    name: str = Field(..., regex=rgx.TITLE, max_length=120, example="Ahmed Shahwan")
    password: str = Field(..., regex=rgx.PASSWORD, max_length=40, example="So secret")
    email: str | None = Field(
        None, regex=rgx.EMAIL, max_length=40, example="ahmed.shahwan@startappz.com"
    )
    profile_pic_url: str | None = Field(
        None, regex=rgx.URL, example="https://example.com/fake_pic.jpg"
    )
    otp_confirmation: str = Field(
        ..., regex=rgx.STRING, max_length=30, example="123456"
    )


class UserUpdateRequest(BaseModel):
    name: str = Field(None, regex=rgx.TITLE, example="jhone")
    password: str = Field(None, regex=rgx.PASSWORD, example="azeqsdwxc")
    profile_pic_url: str = Field(None, regex=rgx.URL, example="jhone@gmail.com")
    email: str = Field(None, regex=rgx.EMAIL, example="https://pic.com")
