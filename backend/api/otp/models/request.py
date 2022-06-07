from pydantic import BaseModel, Field
import utils.regex as rgx


class SendOTPRequest(BaseModel):
    msisdn: str = Field(..., embed=True, regex=rgx.MSISDN, example="7839921514")


class ConfirmOTPRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN, example="7839921514")
    code: str = Field(..., regex=rgx.OTP_CODE, example="165132")


class VerifyOTPRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.MSISDN, example="7839921514")
    confirmation: str = Field(..., regex=rgx.STRING, example="I22Q564JqsdSD")
