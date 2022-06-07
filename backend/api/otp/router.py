""" OTP api set """

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from api.models.response import ApiResponse
from api.models.errors import ELIGIBILITY_ERR
from db.main import get_db
from .utils import gen_alphanumeric, gen_numeric, slack_notify
from api.number.zend import zend_send_sms, zend_sim
from db.models import Otp
from api.models.response import ApiException
from api.otp.models import examples
from api.otp.models.errors import INVALID_CONFIRMATION, INVALID_OTP
from api.otp.models.request import (
    ConfirmOTPRequest,
    SendOTPRequest,
    VerifyOTPRequest,
)
from api.otp.models.response import Confirmation, ConfirmationResponse

router = APIRouter()


@router.post(
    "/request",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.request_otp,
)
async def send_otp(
    user_request: SendOTPRequest, db: Session = Depends(get_db)
) -> ApiResponse:
    """Request new Otp"""
    if not zend_sim(user_request.msisdn)["is_eligible"]:
        raise ApiException(status.HTTP_403_FORBIDDEN, error=ELIGIBILITY_ERR)
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
    return ApiResponse()


@router.post(
    "/confirm",
    response_model=ConfirmationResponse,
    response_model_exclude_none=True,
    responses=examples.confirm_otp,
)
async def confirm(
    user_request: ConfirmOTPRequest, db: Session = Depends(get_db)
) -> ConfirmationResponse:
    """Confirm Otp"""
    if otp := db.query(Otp).filter(Otp.msisdn == user_request.msisdn).first():
        otp.tries += 1
        db.commit()
        db.refresh(otp)
        if otp.code == user_request.code:
            otp.confirmation = gen_alphanumeric()
            db.commit()
            db.refresh(otp)
            return ConfirmationResponse(
                data=Confirmation(confirmation=otp.confirmation),
            )
    raise ApiException(status.HTTP_400_BAD_REQUEST, INVALID_OTP)


@router.post(
    "/verify",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.verify_otp,
)
async def verify_otp(
    user_request: VerifyOTPRequest, db: Session = Depends(get_db)
) -> ApiResponse:
    """Verify otp status (internal use)"""
    otp = db.query(Otp).filter(Otp.msisdn == user_request.msisdn).first()
    # TODO detail more errors here: no confirmation, invalid confirmation
    if otp and otp.confirmation and otp.confirmation == user_request.confirmation:
        return ApiResponse()
    raise ApiException(status.HTTP_400_BAD_REQUEST, INVALID_CONFIRMATION)
