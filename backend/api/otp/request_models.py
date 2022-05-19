from pydantic import BaseModel, Field
import utils.regex as rgx


class OTPSendRequest(BaseModel):
    msisdn: str = Field(..., embed=True, regex=rgx.MSISDN)

    class Config:
        schema_extra = {
            "example": {
                "msisdn": "599196408674300",
            }
        }


class OTPConfirmation(BaseModel):
    confirmation: str

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "confirmation": "O3Dxzx9llkfUdt85",
                },
            }
        }


class OTPConfirmationRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN)
    code: str = Field(..., regex=rgx.DIGITS)

    class Config:
        schema_extra = {
            "example": {
                "msisdn": "599196408674300",
                "code": "165132",
            }
        }


class OTPVerifyRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN)
    confirmation: str = Field(..., regex=rgx.STRING)

    class Config:
        schema_extra = {
            "example": {
                "msisdn": "599196408674300",
                "confirmation": "I22Q564JqsdSD",
            }
        }
