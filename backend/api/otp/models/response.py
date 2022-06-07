from api.models.response import ApiResponse
from api.models.data import Status, Error
from .data import Confirmation

from api.otp.models.errors import INVALID_CONFIRMATION, INVALID_OTP


class ConfirmationResponse(ApiResponse):
    data: Confirmation


class InvalidConfirmationResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_CONFIRMATION


class InvalidOTPResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = INVALID_OTP
