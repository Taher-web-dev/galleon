from pydantic import BaseModel, Field
import utils.regex as rgx


class UserCreateRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN)
    name: str = Field(..., regex=rgx.TITLE)
    password: str = Field(..., regex=rgx.PASSWORD)
    email: str = Field(None, regex=rgx.EMAIL)
    profile_pic_url: str = Field(None, regex=rgx.URL)
    otp_confirmation: str = Field(..., regex=rgx.STRING)

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
