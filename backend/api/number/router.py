"""
BSS : Business Support Systems
This is the middle-ware that connects with
zain backend systems (aka zain-backend)
"""

from fastapi import APIRouter, Body, Query, Depends, status
from api.number.models.response import SubaccountsResponse, nbaResponse
from .balance import get_wallet
from .sim import get_sim_details
from .subscriptions import get_subscriptions
from .zend import (
    recharge_voucher,
    change_supplementary_offering,
    get_free_units,
    query_bill,
    zend_change_subscription,
    zend_sim,
    is_4g_compatible,
)
from sqlalchemy.orm import Session
from db.main import get_db
from utils.jwt import JWTBearer
from utils.settings import settings
import utils.regex as rgx
from db.models import User
from api.number.models.response import (
    RetrieveStatusResponse,
    SubscriptionsResponse,
    WalletResponse,
)
from api.models.response import ApiException, ApiResponse
from .models.errors import MSISDN_MISMATCH
from .sim_helper import get_nba

router = APIRouter()


@router.get(
    "/status",
    response_model=RetrieveStatusResponse,
)
async def retrieve_status(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="7839921514"),
    db: Session = Depends(get_db),
) -> RetrieveStatusResponse:
    """Retrieve SIM status"""
    sim_details = get_sim_details(msisdn)
    sim_details.associated_with_user = (
        db.query(User).filter(User.msisdn == msisdn).first() is not None
    )

    return RetrieveStatusResponse(data=sim_details)


@router.get(
    "/subscriptions",
    response_model=SubscriptionsResponse,
)
async def retrieve_subscriptions(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="7839921514"),
    session_msisdn=Depends(JWTBearer()),
) -> SubscriptionsResponse:
    """Retrieve subscriptions list"""
    if msisdn != session_msisdn:
        raise ApiException(status.HTTP_401_UNAUTHORIZED, error=MSISDN_MISMATCH)
    return SubscriptionsResponse(data=get_subscriptions(msisdn))


@router.get("/subaccounts", response_model=SubaccountsResponse)
async def retrieve_subaccounts(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="7839921514"),
    session_msisdn=Depends(JWTBearer()),
) -> SubaccountsResponse:
    """Retrieves the subaccounts the customer has free units in and the amount in each subaccount."""
    if msisdn != session_msisdn:
        raise ApiException(status.HTTP_401_UNAUTHORIZED, error=MSISDN_MISMATCH)
    return SubaccountsResponse(data=get_free_units(msisdn))


@router.get(
    "/wallet",
    response_model=WalletResponse,
)
async def retrieve_wallet(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="7839921514"),
    session_msisdn=Depends(JWTBearer()),
) -> WalletResponse:
    """Retrieve customer wallet's details (balance and load)"""
    if msisdn != session_msisdn:
        raise ApiException(status.HTTP_401_UNAUTHORIZED, error=MSISDN_MISMATCH)
    return WalletResponse(data=get_wallet(msisdn))
    # assert msisdn == session_msisdn


@router.post(
    "/redeem-registration-gift",
    response_model=ApiResponse,
)
async def redeem_registration_gift(
    msisdn: str = Body(..., embed=True, regex=rgx.MSISDN, example="7839921514"),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    """Redeem registration gift offer"""
    if msisdn != session_msisdn:
        raise ApiException(
            status_code=status.HTTP_401_UNAUTHORIZED, error=MSISDN_MISMATCH
        )
    return change_supplementary_offering(
        msisdn, settings.registration_gift_offer_id, True
    )


@router.post(
    "/charge-voucher",
    response_model=ApiResponse,
)
async def charge_voucher(
    msisdn: str = Body(..., regex=rgx.MSISDN, example="7839921514"),
    pincode: str = Body(..., regex=rgx.VOUCHER_PINCODE, example="1234567891011121"),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    """ Recharge the balance using a voucher"""
    return recharge_voucher(msisdn, pincode)


@router.get("/query-bill", response_model=ApiResponse)
async def query_postpaid_bill(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="7839921514"),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    """Returns a postpaid customer's balance"""
    if msisdn != session_msisdn:
        raise ApiException(status_code=99, error=MSISDN_MISMATCH)
    return query_bill(msisdn)


@router.post("/subscribe", response_model=ApiResponse)
async def subscribe_an_offer(
    msisdn: str = Body(..., regex=rgx.MSISDN, example="7839921514"),
    offer_id: int = Body(..., example=1000),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    """Add a subscription to a Zain customer’s line using the subscriber’s MSISDN."""
    if msisdn != session_msisdn:
        raise ApiException(status.HTTP_401_UNAUTHORIZED, MSISDN_MISMATCH)
    return zend_change_subscription(msisdn, offer_id, True)


@router.delete("/unsubscribe", response_model=ApiResponse)
async def unsubscribe_an_offer(
    msisdn: str = Body(..., regex=rgx.MSISDN, example="7839921514"),
    offer_id: int = Body(..., example=1000),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
# removes a subscription from a Zain customer’s line using its TOMS ID and the subscriber’s MSISDNN
    """Remove a subscription from a Zain customer’s line using the subscriber’s MSISDN."""
    if msisdn != session_msisdn:
        raise ApiException(status.HTTP_401_UNAUTHORIZED, MSISDN_MISMATCH)
    return zend_change_subscription(msisdn, offer_id, False)


@router.get("/welcome-message", response_model=nbaResponse)
async def welcome_message(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="7839921514"),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    """Welcome message aka nba """
    if msisdn != session_msisdn:
        raise ApiException(status.HTTP_401_UNAUTHORIZED, MSISDN_MISMATCH)
    sim_status = zend_sim(msisdn)
    nba = get_nba(
        msisdn, sim_status["unified_sim_status"], is_4g_compatible(msisdn), sim_status
    )
    return nbaResponse(data={"nba": nba})
