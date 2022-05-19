from fastapi import status
from typing import Dict, Any

from api.otp.response_models import (
    OTPInvalidMSISDNResponse,
    OTPErrorSMSResponse,
    OTPInvalidOTPConfirmationResponse,
    OTPInvalidOTPFormatResponse,
    OTPInvalidRequestIDResponse,
    OTPMissmatchOTPCOnfirmationResponse,
)

request_otp: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": OTPInvalidMSISDNResponse,
        "description": "Invalid MSISDN or Email.",
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "model": OTPErrorSMSResponse,
        "description": "SMS GW server down or not configured.",
    },
}

confirm_otp: Dict[int | str, Dict[str, Any]] = {
    **request_otp,
    status.HTTP_400_BAD_REQUEST: {
        "model": OTPInvalidRequestIDResponse,
        "description": "Invalid OTP request Id.",
    },
    status.HTTP_400_BAD_REQUEST: {
        "model": OTPInvalidOTPFormatResponse,
        "description": "Invalid OTP format.",
    },
}

verify_otp: Dict[int | str, Dict[str, Any]] = {
    **request_otp,
    status.HTTP_400_BAD_REQUEST: {
        "model": OTPInvalidOTPConfirmationResponse,
        "description": "Invalid OTP confirmation Id",
    },
    status.HTTP_400_BAD_REQUEST: {
        "model": OTPMissmatchOTPCOnfirmationResponse,
        "description": "Missmatch OTP confirmation Id",
    },
}
