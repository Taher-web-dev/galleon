"""
BSS : Business Support Systems
This is the middle-ware that connects with
zain backend systems (aka zain-backend)
"""

from fastapi import APIRouter, Body
from fastapi import Depends

from .balance import get_wallet, Wallet
from .sim import get_sim_details
from .subscriptions import get_subscriptions
from .zend import recharge_voucher, change_supplementary_offering
from utils.jwt import JWTBearer
from utils.settings import settings
import utils.regex as rgx
from utils.api_responses import Status
from .response_models import StatusResponse, SubscriptionsResponse

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
async def retrieve_status(
    msisdn: str = Body(..., embed=True), session_msisdn=Depends(JWTBearer())
) -> StatusResponse:
    """Retrieve SIM status"""
    assert msisdn == session_msisdn
    return StatusResponse(status=Status.success, data=get_sim_details(msisdn))


@router.get("/subscriptions", response_model=SubscriptionsResponse)
async def retrieve_subscriptions(
    msisdn: str = Body(..., embed=True), session_msisdn=Depends(JWTBearer())
) -> SubscriptionsResponse:
    """Retrieve subscriptions list"""
    assert msisdn == session_msisdn
    return SubscriptionsResponse(status=Status.success, data=get_subscriptions(msisdn))


@router.get("/wallet", response_model=Wallet)
async def retrieve_wallet(
    msisdn: str = Body(..., embed=True), session_msisdn=Depends(JWTBearer())
):
    """Retrieve customer wallet's details (balance and load)"""
    assert msisdn == session_msisdn
    return get_wallet(msisdn)


@router.post("/redeem-registration-gift")
async def api_registration_gift(
    msisdn: str = Body(..., embed=True, regex=rgx.MSISDN),
    session_msisdn=Depends(JWTBearer()),
):
    assert msisdn == session_msisdn
    return change_supplementary_offering(
        msisdn, settings.registration_gift_offer_id, True
    )


@router.post("/charge-voucher")
async def api_charge_voucher(
    msisdn: str = Body(..., regex=rgx.MSISDN),
    pincode: str = Body(..., regex=rgx.DIGITS),
    session_msisdn=Depends(JWTBearer()),
):
    assert msisdn == session_msisdn
    return recharge_voucher(msisdn, pincode)
