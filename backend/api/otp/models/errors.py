from api.models.data import Error


INVALID_CONFIRMATION = Error(
    type="otp",
    code=306,
    message="Invalid confirmation",
)

INVALID_OTP = Error(
    type="otp",
    code=307,
    message="Invalid OTP",
)
