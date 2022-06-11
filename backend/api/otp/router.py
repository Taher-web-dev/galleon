""" OTP api set """

from fastapi import APIRouter, status
from api.models.response import ApiResponse
from api.models.errors import ELIGIBILITY_ERR
from .utils import slack_notify
from api.number.zend import zend_send_sms, zend_sim
from api.models.response import ApiException
from api.otp.models import examples
from api.otp.models.errors import INVALID_CONFIRMATION, INVALID_OTP
from api.otp.models.request import (
    ConfirmOTPRequest,
    SendOTPRequest,
    VerifyOTPRequest,
)
from api.otp.models.response import Confirmation, ConfirmationResponse
from .repository import (
    create_otp,
    get_otp,
    delete_otp,
    increment_otp_tries,
    gen_otp_confirmation,
)

router = APIRouter()


@router.post(
    "/request",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.request_otp,
)
async def send_otp(user_request: SendOTPRequest) -> ApiResponse:
    """Request new OTP"""
    if not zend_sim(user_request.msisdn)["is_eligible"]:
        raise ApiException(status.HTTP_403_FORBIDDEN, error=ELIGIBILITY_ERR)
    # If a prior otp exists, delete it.
    delete_otp(user_request.msisdn)
    code = "123456"  # gen_numeric()  # FIXME on production
    create_otp(user_request.msisdn, code)
    zend_send_sms(user_request.msisdn, f"Your otp code is {code}")
    slack_notify(user_request.msisdn, code)
    return ApiResponse()


@router.post(
    "/confirm",
    response_model=ConfirmationResponse,
    response_model_exclude_none=True,
    responses=examples.confirm_otp,
)
async def confirm_otp(user_request: ConfirmOTPRequest) -> ConfirmationResponse:
    """Confirm OTP"""
    if otp := get_otp(user_request.msisdn):
        increment_otp_tries(otp)
        if otp.code == user_request.code:
            gen_otp_confirmation(otp)
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
async def verify_otp(user_request: VerifyOTPRequest) -> ApiResponse:
    """Verify the confirmation of OTP"""
    otp = get_otp(user_request.msisdn)
    if otp and otp.confirmation and otp.confirmation == user_request.confirmation:
        return ApiResponse()
    raise ApiException(status.HTTP_400_BAD_REQUEST, INVALID_CONFIRMATION)
