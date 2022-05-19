from utils.api_responses import Status, ApiResponse, Error


INVALID_MSISDN = Error(
    type="otp",
    code=400,
    message="Sorry the MSISDN or Email you requested the OTP to send to is invalid.",
)

ERROR_SMS = Error(
    type="otp",
    code=503,
    message="There are no SMS GateWay to fulfill your request.",
)

ERROR_SMTP = Error(
    type="otp",
    code=503,
    message="There are no Email SMTP to fulfill your request.",
)

INVALID_OTP_REQUEST_ID = Error(
    type="otp",
    code=400,
    message="Something is the wrong! the OTP request you submitted is invalid.",
)

INVALID_OTP_REQUEST_FORMAT = Error(
    type="otp",
    code=400,
    message="The submitted OTP format you shared is invalid format.",
)

OTP_MISMATCH_ERROR = Error(
    type="otp",
    code=400,
    message="Something is wrong! the OTP request you confirmation does not match the request.",
)


class OTPRequestErrorResponseInvalidMSISDN(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_MSISDN]


class OTPRequestErrorResponseErrorSMS(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [ERROR_SMS]


class OTPRequestErrorResponseErrorSMTP(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [ERROR_SMTP]


class OTPRequestErrorResponseInvalidRequestID(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_OTP_REQUEST_ID]


class OTPRequestErrorResponseInvalidOTPFormat(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_OTP_REQUEST_FORMAT]


class OTPRequestErrorResponseMissmatchOTPCOnfirmation(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [OTP_MISMATCH_ERROR]
