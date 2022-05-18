""" OTP api set """

from fastapi import APIRouter, Body
from .utils import gen_alphanumeric, gen_numeric, slack_notify
from ..number.zend import zend_send_sms
from utils.db import Otp, db
from utils.api_responses import ApiResponse, Error, Status
from typing import Any
from utils.regex import DIGITS as RGX_DIGITS, STRING as RGX_STRING

router = APIRouter()


@router.post("/request", response_model=ApiResponse)
async def send_otp(
    msisdn: str = Body(..., embed=True, regex=RGX_DIGITS)
) -> ApiResponse:
    """Request new Otp"""

    # If a prior otp exists, delete it.
    otp = db.query(Otp).filter(Otp.msisdn == msisdn).first()
    if otp:
        db.delete(otp)
        db.commit()

    code = gen_numeric()
    otp = Otp(msisdn=msisdn, code=code)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    zend_send_sms(msisdn, f"Your otp code is {code}")
    slack_notify(msisdn, code)
    return ApiResponse(status=Status.success)


@router.post("/confirm", response_model=ApiResponse, response_model_exclude_none=True)
async def confirm(
    msisdn: str = Body(..., regex=RGX_DIGITS), code: str = Body(..., regex=RGX_DIGITS)
) -> ApiResponse:
    """Confirm Otp"""
    otp = db.query(Otp).filter(Otp.msisdn == msisdn).first()
    if otp:
        otp.tries += 1
        db.commit()
        db.refresh(otp)
        if otp.code == code:
            otp.confirmation = gen_alphanumeric()
            db.commit()
            db.refresh(otp)
            return ApiResponse(
                status=Status.success, data={"confirmation": otp.confirmation}
            )
    return ApiResponse(
        status=Status.failed,
        errors=[Error(type="otp", code=99, message="Bad otp confirmation")],
    )


@router.post("/verify", response_model=ApiResponse)
async def api_verify(
    msisdn: str = Body(..., regex=RGX_DIGITS),
    confirmation: str = Body(..., regex=RGX_STRING),
) -> ApiResponse:
    """Verify otp status (internal use)"""
    otp = db.query(Otp).filter(Otp.msisdn == msisdn).first()
    if otp and otp.confirmation and otp.confirmation == confirmation:
        return ApiResponse(status=Status.success)
    return ApiResponse(
        status=Status.failed,
        errors=[Error(type="otp", code=99, message="Bad otp confirmation")],
    )
