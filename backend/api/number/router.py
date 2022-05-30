"""
BSS : Business Support Systems
This is the middle-ware that connects with
zain backend systems (aka zain-backend)
"""

from fastapi import APIRouter, Body, Query, status, Depends
from api.models.data import Status
from .balance import get_wallet
from .sim import get_sim_details
from .subscriptions import get_subscriptions
from .zend import recharge_voucher, change_supplementary_offering
from utils.jwt import JWTBearer
from utils.settings import settings
import utils.regex as rgx
from api.number.models.response import (
    ChargeVoucherResponse,
    RegistrationGiftResponse,
    RetrieveStatusResponse,
    SubscriptionsResponse,
    WalletResponse,
)
from api.models.response import ApiException, ApiResponse
import api.user.models.errors as err

router = APIRouter()


@router.get(
    "/status",
    response_model=RetrieveStatusResponse,
)
async def retrieve_status(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="308080703257")
) -> RetrieveStatusResponse:
    """Retrieve SIM status"""
    return RetrieveStatusResponse(status=Status.success, data=get_sim_details(msisdn))


@router.get(
    "/subscriptions",
    response_model=SubscriptionsResponse,
)
async def retrieve_subscriptions(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="308080703257"),
    session_msisdn=Depends(JWTBearer()),
) -> SubscriptionsResponse:
    """Retrieve subscriptions list"""
    if msisdn == session_msisdn:
        return SubscriptionsResponse(
            status=Status.success, data=get_subscriptions(msisdn)
        )
    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_MSISDN)


@router.get(
    "/wallet",
    response_model=WalletResponse,
)
async def retrieve_wallet(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="308080703257"),
    session_msisdn=Depends(JWTBearer()),
) -> WalletResponse:
    """Retrieve customer wallet's details (balance and load)"""
    if msisdn == session_msisdn:
        return WalletResponse(status=Status.success, data=get_wallet(msisdn))
    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_MSISDN)
    # assert msisdn == session_msisdn


@router.post(
    "/redeem-registration-gift",
    response_model=ApiResponse,
)
async def redeem_registration_gift(
    msisdn: str = Body(..., embed=True, regex=rgx.MSISDN),
    session_msisdn=Depends(JWTBearer()),
) -> RegistrationGiftResponse:
    if msisdn == session_msisdn:
        resp = change_supplementary_offering(
            msisdn, settings.registration_gift_offer_id, True
        )
        return RegistrationGiftResponse(status=Status.success, data=resp)
    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_MSISDN)


@router.post(
    "/charge-voucher",
    response_model=ApiResponse,
)
async def charge_voucher(
    msisdn: str = Body(..., regex=rgx.MSISDN),
    pincode: str = Body(..., regex=rgx.DIGITS),
    session_msisdn=Depends(JWTBearer()),
) -> ChargeVoucherResponse:
    if msisdn == session_msisdn:
        return ChargeVoucherResponse(
            status=Status.success, data=recharge_voucher(msisdn, pincode)
        )
    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_MSISDN)
