""" Errors used in the API. """

from api.models.data import Error

NOT_AUTHENTICATED = Error(type="auth", code=10, message="Not authenticated")

EXPIRED_TOKEN = Error(
    type="auth",
    code=105,
    message="You need to renew the Access token using the refresh token",
)

VALIDATION_ERR = Error(type="validation", code=100, message="")

ELIGIBILITY_ERR = Error(type="eligibility", code=160, message="Not eligible")

InvalidAccessToken = Error(
    type="token", code=101, message="The Access-Token is not valid"
)
