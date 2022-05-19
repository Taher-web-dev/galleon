from utils.api_responses import Status, ApiResponse, Error

from api.otp import app_errors as err


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
    error: Error = err.OTP_MISMATCH_ERROR
