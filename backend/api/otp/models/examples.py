from fastapi import status
from typing import Dict, Any

from api.otp.models.response import (
    InvalidOTPResponse,
    InvalidConfirmationResponse,
)
from api.models.response import EligibilityErrorResponse

request_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_403_FORBIDDEN: {
        "model": EligibilityErrorResponse,
        "description": "User Eligibility",
    },
}

confirm_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "model": InvalidOTPResponse,
        "description": "Invalid OTP",
    },
}

verify_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "model": InvalidConfirmationResponse,
        "description": "Invalid confirmation",
    },
}
