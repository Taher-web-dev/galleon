from pydantic import BaseModel, Field
from api.models.response import ApiResponse
from api.models.data import Status, Error

import api.otp.app_errors as err


class OTPConfirmation(BaseModel):
    confirmation: str = Field(..., example="O3Dxzx9llkfUdt85")


class OTPConfirmationResponse(ApiResponse):
    data: OTPConfirmation


class OTPInvalidMSISDNResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_MSISDN


class OTPSMSErrorResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.SMS_ERROR


class OTPInvalidRequestIDResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_OTP_REQUEST_ID


class OTPInvalidOTPFormatResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_OTP_REQUEST_FORMAT


class OTPInvalidOTPConfirmationResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.INVALID_OTP_CONFIRMATION


class OTPMismatchOTPConfirmationResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = err.OTP_MISMATCH
