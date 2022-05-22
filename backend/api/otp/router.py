""" OTP api set """

from fastapi import APIRouter, status

from api.otp.request_models import (
    ConfirmationOTPRequest,
    SendOTPRequest,
    VerifyOTPRequest,
)
from api.base_response_models import StatusResponse
from api.otp.response_models import OTPConfirmation, OTPConfirmationResponse
from .utils import gen_alphanumeric, gen_numeric, slack_notify
from api.number.zend import zend_send_sms
from utils.db import Otp, db
from utils.api_responses import ApiException, Status
from .additional_responses import request_otp, confirm_otp, verify_otp
import utils.regex as rgx
import api.otp.app_errors as err

router = APIRouter()


@router.post(
    "/request",
    response_model=StatusResponse,
    response_model_exclude_none=True,
    responses=request_otp,
)
async def send_otp(user_request: SendOTPRequest) -> StatusResponse:
    """Request new Otp"""

    # If a prior otp exists, delete it.
    otp = db.query(Otp).filter(Otp.msisdn == user_request.msisdn).first()
    if otp:
        db.delete(otp)
        db.commit()

    code = gen_numeric()
    otp = Otp(msisdn=user_request.msisdn, code=code)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    zend_send_sms(user_request.msisdn, f"Your otp code is {code}")
    slack_notify(user_request.msisdn, code)
    return StatusResponse(status=Status.success)


@router.post(
    "/confirm",
    response_model=OTPConfirmationResponse,
    response_model_exclude_none=True,
    responses=confirm_otp,
)
async def confirm(user_request: ConfirmationOTPRequest) -> OTPConfirmationResponse:
    """Confirm Otp"""
    if otp := db.query(Otp).filter(Otp.msisdn == user_request.msisdn).first():
        otp.tries += 1
        db.commit()
        db.refresh(otp)
        if otp.code == user_request.code:
            otp.confirmation = gen_alphanumeric()
            db.commit()
            db.refresh(otp)
            return OTPConfirmationResponse(
                data=OTPConfirmation(confirmation=otp.confirmation),
            )
    raise ApiException(status.HTTP_400_BAD_REQUEST, err.OTP_MISMATCH)


@router.post(
    "/verify",
    response_model=StatusResponse,
    response_model_exclude_none=True,
    responses=verify_otp,
)
async def api_verify(user_request: VerifyOTPRequest) -> StatusResponse:
    """Verify otp status (internal use)"""
    otp = db.query(Otp).filter(Otp.msisdn == user_request.msisdn).first()
    if otp and otp.confirmation and otp.confirmation == user_request.confirmation:
        return StatusResponse(status=Status.success)
    raise ApiException(status.HTTP_400_BAD_REQUEST, err.OTP_MISMATCH)
