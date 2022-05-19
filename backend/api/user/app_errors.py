from utils.api_responses import Error

USER_EXISTS_ERROR = Error(
    type="user", code=201, message="Sorry the msisdn is already registered."
)

INVALID_OTP_ERROR = Error(
    type="otp",
    code=202,
    message="The confirmation provided is not valid please try again.",
)

INVALID_CREDENTIALS_ERROR = Error(
    type="auth",
    code=203,
    message="Invalid credentials",
)

INVALID_TOKEN_ERROR = Error(
    type="auth",
    code=204,
    message="Invalid token",
)
