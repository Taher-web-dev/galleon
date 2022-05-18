from fastapi import status
from api.user.response_models import (
    UserExistsErrorResponse,
    InvalidOtpErrorResponse,
    InvalidCredentialsErrorResponse,
    InvalidTokenErrorResponse,
)

create_user = {
    status.HTTP_403_FORBIDDEN: {
        "model": UserExistsErrorResponse,
        "description": "User already exists.",
    },
    status.HTTP_409_CONFLICT: {
        "model": InvalidOtpErrorResponse,
        "description": "Invalid OTP Confirmation.",
    },
}

login = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidCredentialsErrorResponse,
        "description": "Invalid credentials",
    },
}

token = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidTokenErrorResponse,
        "description": "Invalid token.",
    },
}
