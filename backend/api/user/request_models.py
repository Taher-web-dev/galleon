from pydantic import BaseModel, Field
import utils.regex as rgx


class UserCreateRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN, max_length=20)
    name: str = Field(..., regex=rgx.TITLE, max_length=120)
    password: str = Field(..., regex=rgx.PASSWORD, max_length=40)
    email: str | None = Field(None, regex=rgx.EMAIL, max_length=40)
    profile_pic_url: str | None = Field(None, regex=rgx.URL)
    otp_confirmation: str = Field(..., regex=rgx.STRING, max_length=30)

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "msisdn": "12345678933",
                    "name": "Ahmed Shahwan",
                    "password": "So secret",
                    "email": "ahmed.shahwan@startappz.com",
                    "profile_pic_url": "https://example.com/fake_pic.jpg",
                    "otp_confirmation": "123456",
                },
            }
        }

    class Config:
        schema_extra = {
            "example": {
                "msisdn": "599196408674300",
                "name": "jhone",
                "password": "azeqsdwxc",
                "email": "jhone@gmail.com",
                "profile_pic_url": "https://pic.com",
                "otp_confirmation": "JioqshdiySUQHb",
            }
        }


class UserUpdateRequest(BaseModel):
    name: str = Field(None, regex=rgx.TITLE)
    password: str = Field(None, regex=rgx.PASSWORD)
    profile_pic_url: str = Field(None, regex=rgx.URL)
    email: str = Field(None, regex=rgx.EMAIL)

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "name": "jhone",
                    "password": "azeqsdwxc",
                    "email": "jhone@gmail.com",
                    "profile_pic_url": "https://pic.com",
                },
            }
        }
