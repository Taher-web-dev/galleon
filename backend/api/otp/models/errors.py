from api.models.data import Error

INVALID_MSISDN = Error(
    type="otp",
    code=301,
    message="Sorry the MSISDN or Email you requested the OTP to send to is invalid.",
)

SMS_ERROR = Error(
    type="otp",
    code=302,
    message="There are no SMS GateWay to fulfill your request.",
)

INVALID_REQUEST_ID = Error(
    type="otp",
    code=304,
    message="Something is the wrong! the OTP request you submitted is invalid.",
)

INVALID_REQUEST_FORMAT = Error(
    type="otp",
    code=305,
    message="The submitted OTP format you shared is invalid format.",
)

INVALID_CONFIRMATION = Error(
    type="otp",
    code=306,
    message="Something is wrong! the OTP request you confirmation is invalid.",
)

INVALID_OTP = Error(
    type="otp",
    code=307,
    message="Something is wrong! msisdn or code is wrong",
)
