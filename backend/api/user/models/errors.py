from api.models.data import Error

USER_EXISTS = Error(
    type="user", code=201, message="Sorry the msisdn is already registered."
)

INVALID_OTP = Error(
    type="otp",
    code=202,
    message="The confirmation provided is not valid please try again.",
)

INVALID_MSISDN = Error(
    type="number",
    code=100,
    message="Invalid MSISDN",
)

INVALID_CREDENTIALS = Error(
    type="auth",
    code=100,
    message="Phone number or password is incorrect",
)

INVALID_TOKEN = Error(
    type="auth",
    code=103,
    message="Invalid token",
)

INVALID_REFRESH_TOKEN = Error(
    type="auth",
    code=130,
    message="Invalid refresh token",
)
