from fastapi import status
from typing import Dict, Any

from api.otp.models.response import (
    InvalidMSISDNResponse,
    SMSErrorResponse,
    InvalidRequestIdResponse,
    InvalidConfirmationResponse,
    InvalidFormatResponse,
)
from api.models.response import EligibilityErrorResponse

request_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidMSISDNResponse,
        "description": "Invalid MSISDN or Email.",
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "model": SMSErrorResponse,
        "description": "SMS GW server down or not configured.",
    },
    status.HTTP_403_FORBIDDEN: {
        "model": EligibilityErrorResponse,
        "description": "User Eligibility",
    },
}

confirm_otp: Dict[int | str, Dict[str, Any]] = {
    **request_otp,
    status.HTTP_400_BAD_REQUEST: {
        "model": InvalidRequestIdResponse,
        "description": "Invalid OTP request Id.",
    },
    status.HTTP_400_BAD_REQUEST: {
        "model": InvalidFormatResponse,
        "description": "Invalid OTP format.",
    },
}

verify_otp: Dict[int | str, Dict[str, Any]] = {
    **request_otp,
    status.HTTP_400_BAD_REQUEST: {
        "model": InvalidConfirmationResponse,
        "description": "Invalid OTP confirmation Id",
    },
}
