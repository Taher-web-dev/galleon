from fastapi import status
from typing import Dict, Any
from api.user.models.response import (
    InvalidRefreshTokenErrorResponse,
    UserExistsErrorResponse,
    InvalidOtpErrorResponse,
    InvalidCredentialsErrorResponse,
    InvalidTokenErrorResponse,
    ValidationErrorResponse,
)
from api.models import examples as api_examples

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

get_user_profile: Dict[int | str, Dict[str, Any]] = {**api_examples.not_authenticated}

update_profile: Dict[int | str, Dict[str, Any]] = {**api_examples.not_authenticated}

login: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidCredentialsErrorResponse,
        "description": "Invalid credentials",
    },
}

logout: Dict[int | str, Dict[str, Any]] = {**api_examples.not_authenticated}

token: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidTokenErrorResponse,
        "description": "Invalid token.",
    },
}

refresh_token: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidRefreshTokenErrorResponse,
        "description": "Invalid token.",
    },
}

delete: Dict[int | str, Dict[str, Any]] = {**api_examples.not_authenticated}
