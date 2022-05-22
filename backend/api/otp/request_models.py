from pydantic import BaseModel, Field
import utils.regex as rgx


class OTPSendRequest(BaseModel):
    msisdn: str = Field(..., embed=True, regex=rgx.MSISDN, example="599196408674300")


class OTPConfirmationRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN, example="599196408674300")
    code: str = Field(..., regex=rgx.DIGITS, example="165132")


class OTPVerifyRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN, example="599196408674300")
    confirmation: str = Field(..., regex=rgx.STRING, example="I22Q564JqsdSD")
