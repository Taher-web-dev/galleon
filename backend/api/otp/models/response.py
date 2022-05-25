from pydantic import BaseModel, Field
from api.models.response import ApiResponse
from api.models.data import Status, Error

from api.otp.models.errors import (
    INVALID_MSISDN,
    SMS_ERROR,
    INVALID_REQUEST_ID,
    INVALID_REQUEST_FORMAT,
    INVALID_CONFIRMATION,
    INVALID_OTP,
)

# TODO move to data.py
class Confirmation(BaseModel):
    confirmation: str = Field(..., example="O3Dxzx9llkfUdt85")


class ConfirmationResponse(ApiResponse):
    data: Confirmation


class InvalidMSISDNResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_MSISDN


class SMSErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = SMS_ERROR


class InvalidRequestIdResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_REQUEST_ID


class InvalidFormatResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_REQUEST_FORMAT


class InvalidConfirmationResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_CONFIRMATION


class InvalidOTPResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_OTP
