from fastapi import status
from typing import Dict, Any
from api.user.response_models import (
    UserExistsErrorResponse,
    InvalidOtpErrorResponse,
    InvalidCredentialsErrorResponse,
    InvalidTokenErrorResponse,
    ValidationErrorResponse,
)

create_user: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_403_FORBIDDEN: {
        "model": UserExistsErrorResponse,
        "description": "User already exists.",
    },
    status.HTTP_409_CONFLICT: {
        "model": InvalidOtpErrorResponse,
        "description": "Invalid OTP Confirmation.",
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ValidationErrorResponse,
        "description": "Validation Error",
    },
}

login: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidCredentialsErrorResponse,
        "description": "Invalid credentials",
    },
}

token: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidTokenErrorResponse,
        "description": "Invalid token.",
    },
}
