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

INVALID_MSISDN_MISSMATCH = Error(
    type="number",
    code=300,
    message="The MSISDN does not match.",
)
