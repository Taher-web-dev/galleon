from utils.api_responses import Error


EXPIRED_TOKEN = Error(
    type="auth",
    code=105,
    message="You need to renew the Access token using the refresh token",
)
