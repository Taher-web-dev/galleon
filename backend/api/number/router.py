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
from api.number.models.response import (
    ChargeVoucherResponse,
    RetrieveStatusResponse,
    SubscriptionsResponse,
    WalletResponse,
)
from api.models import examples as api_examples
from api.models.response import ApiResponse

router = APIRouter()


@router.get(
    "/status",
    response_model=RetrieveStatusResponse,
    responses=api_examples.not_authenticated,
)
async def retrieve_status(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="308080703257")
) -> RetrieveStatusResponse:
    """Retrieve SIM status"""
    return RetrieveStatusResponse(data=get_sim_details(msisdn))


@router.get(
    "/subscriptions",
    response_model=SubscriptionsResponse,
    responses=api_examples.not_authenticated,
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
    responses=api_examples.not_authenticated,
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
    response_model=ApiResponse,
    responses=api_examples.not_authenticated,
)
async def redeem_registration_gift(
    msisdn: str = Body(..., embed=True, regex=rgx.MSISDN),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    assert msisdn == session_msisdn
    return change_supplementary_offering(
        msisdn, settings.registration_gift_offer_id, True
    )


@router.post(
    "/charge-voucher",
    response_model=ApiResponse,
    responses=api_examples.not_authenticated,
)
async def charge_voucher(
    msisdn: str = Body(..., regex=rgx.MSISDN),
    pincode: str = Body(..., regex=rgx.DIGITS),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    assert msisdn == session_msisdn
    return recharge_voucher(msisdn, pincode)
