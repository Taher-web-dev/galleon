"""
BSS : Business Support Systems
This is the middle-ware that connects with
zain backend systems (aka zain-backend)
"""

from fastapi import APIRouter, Body, Query
from fastapi import Depends
from .balance import get_wallet
from .sim import get_sim_details
from .subscriptions import get_subscriptions
from .zend import recharge_voucher, change_supplementary_offering
from utils.jwt import JWTBearer
from utils.settings import settings
import utils.regex as rgx
from .response_models import (
    ChargeVoucherResponse,
    RetrieveStatusResponse,
    SubscriptionsResponse,
    WalletResponse,
    RegistrationGiftResponse,
)
from api import shared_responses

router = APIRouter()


@router.get(
    "/status",
    response_model=RetrieveStatusResponse,
    responses=shared_responses.not_authenticated,
)
async def retrieve_status(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="308080703257"),
    session_msisdn=Depends(JWTBearer()),
) -> RetrieveStatusResponse:
    """Retrieve SIM status"""
    assert msisdn == session_msisdn
    return RetrieveStatusResponse(data=get_sim_details(msisdn))


@router.get(
    "/subscriptions",
    response_model=SubscriptionsResponse,
    responses=shared_responses.not_authenticated,
)
async def retrieve_subscriptions(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="308080703257"),
    session_msisdn=Depends(JWTBearer()),
) -> SubscriptionsResponse:
    """Retrieve subscriptions list"""
    assert msisdn == session_msisdn
    return SubscriptionsResponse(data=get_subscriptions(msisdn))


@router.get(
    "/wallet",
    response_model=WalletResponse,
    responses=shared_responses.not_authenticated,
)
async def retrieve_wallet(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="308080703257"),
    session_msisdn=Depends(JWTBearer()),
) -> WalletResponse:
    """Retrieve customer wallet's details (balance and load)"""
    assert msisdn == session_msisdn
    return WalletResponse(data=get_wallet(msisdn))


@router.post(
    "/redeem-registration-gift",
    response_model=RegistrationGiftResponse,
    responses=shared_responses.not_authenticated,
)
async def redeem_registration_gift(
    msisdn: str = Body(..., embed=True, regex=rgx.MSISDN),
    session_msisdn=Depends(JWTBearer()),
) -> RegistrationGiftResponse:
    assert msisdn == session_msisdn
    resp = change_supplementary_offering(
        msisdn, settings.registration_gift_offer_id, True
    )
    return RegistrationGiftResponse(data=resp)


@router.post(
    "/charge-voucher",
    response_model=ChargeVoucherResponse,
    responses=shared_responses.not_authenticated,
)
async def charge_voucher(
    msisdn: str = Body(..., regex=rgx.MSISDN),
    pincode: str = Body(..., regex=rgx.DIGITS),
    session_msisdn=Depends(JWTBearer()),
) -> ChargeVoucherResponse:
    assert msisdn == session_msisdn
    return ChargeVoucherResponse(data=recharge_voucher(msisdn, pincode))
