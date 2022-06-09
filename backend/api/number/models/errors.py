from api.models.data import Error

MSISDN_MISMATCH = Error(
    type="number",
    code=300,
    message="The MSISDN does not match.",
)
