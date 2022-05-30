""" OTP api set """

from fastapi import APIRouter, status, Request

from api.models.response import ApiResponse
from .utils import gen_alphanumeric, gen_numeric, slack_notify
from api.number.zend import zend_send_sms
from db.models import Otp
from api.models.response import ApiException
from api.otp.models import examples
from api.otp.models.errors import INVALID_OTP
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
async def send_otp(request: Request, user_request: SendOTPRequest) -> ApiResponse:
    """Request new Otp"""

    # If a prior otp exists, delete it.
    otp = request.state.db.query(Otp).filter(Otp.msisdn == user_request.msisdn).first()
    if otp:
        request.state.db.delete(otp)
        request.state.db.commit()

    code = "123456"  # FIXME this should be used  in production: gen_numeric()
    otp = Otp(msisdn=user_request.msisdn, code=code)
    request.state.db.add(otp)
    request.state.db.commit()
    request.state.db.refresh(otp)
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
    request: Request, user_request: ConfirmOTPRequest
) -> ConfirmationResponse:
    """Confirm Otp"""
    if (
        otp := request.state.db.query(Otp)
        .filter(Otp.msisdn == user_request.msisdn)
        .first()
    ):
        otp.tries += 1
        request.state.db.commit()
        request.state.db.refresh(otp)
        if otp.code == user_request.code:
            otp.confirmation = gen_alphanumeric()
            request.state.db.commit()
            request.state.db.refresh(otp)
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
async def verify_otp(request: Request, user_request: VerifyOTPRequest) -> ApiResponse:
    """Verify otp status (internal use)"""
    otp = request.state.db.query(Otp).filter(Otp.msisdn == user_request.msisdn).first()
    # TODO detail more errors here: no confirmation, invalid confirmation
    if otp and otp.confirmation and otp.confirmation == user_request.confirmation:
        return ApiResponse()
    raise ApiException(status.HTTP_400_BAD_REQUEST, INVALID_OTP)
