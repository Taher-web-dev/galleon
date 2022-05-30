""" Errors used in the API. """

from xml.dom import VALIDATION_ERR
from api.models.data import Error

NOT_AUTHENTICATED = Error(type="auth", code=10, message="Not authenticated")

EXPIRED_TOKEN = Error(
    type="auth",
    code=105,
    message="You need to renew the Access token using the refresh token",
)

VALIDATION_ERR = Error(
    type="validation", code=100, message="You need to introduce valid data."
)
