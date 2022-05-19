from utils.api_responses import Error

INVALID_MSISDN = Error(
    type="otp",
    code=301,
    message="Sorry the MSISDN or Email you requested the OTP to send to is invalid.",
)

ERROR_SMS = Error(
    type="otp",
    code=302,
    message="There are no SMS GateWay to fulfill your request.",
)

INVALID_OTP_REQUEST_ID = Error(
    type="otp",
    code=304,
    message="Something is the wrong! the OTP request you submitted is invalid.",
)

INVALID_OTP_REQUEST_FORMAT = Error(
    type="otp",
    code=305,
    message="The submitted OTP format you shared is invalid format.",
)

INVALID_OTP_CONFIRMATION = Error(
    type="otp",
    code=306,
    message="Something is wrong! the OTP request you confirmation is invalid.",
)

OTP_MISMATCH_ERROR = Error(
    type="otp",
    code=307,
    message="Something is wrong! the OTP request you confirmation does not match the request.",
)
