from fastapi import status
from typing import Dict, Any

from api.otp.models.response import (
    InvalidOTPResponse,
    InvalidConfirmationResponse,
)
from api.models.response import EligibilityErrorResponse
from api.otp.models.errors import INVALID_OTP
from utils.example_error_responses import error_response

request_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_403_FORBIDDEN: {
        "model": EligibilityErrorResponse,
        "description": "User Eligibility",
    },
}

confirm_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "content": error_response(INVALID_OTP),
        "description": "Invalid OTP",
    },
}

verify_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "model": InvalidConfirmationResponse,
        "description": "Invalid confirmation",
    },
}
