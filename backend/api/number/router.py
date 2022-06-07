"""
BSS : Business Support Systems
This is the middle-ware that connects with
zain backend systems (aka zain-backend)
"""

from fastapi import APIRouter, Body, Query, Depends
from api.number.models.response import SubaccountsResponse
from .balance import get_wallet
from .sim import get_sim_details
from .subscriptions import get_subscriptions
from .zend import (
    recharge_voucher,
    change_supplementary_offering,
    get_free_units,
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
from api.models.response import ApiResponse

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
    return SubscriptionsResponse(data=get_subscriptions(msisdn))


@router.get("/subaccounts", response_model=SubaccountsResponse)
async def retrieve_subaccounts(
    msisdn: str = Query(..., regex=rgx.MSISDN, example="7839921514"),
    session_msisdn=Depends(JWTBearer()),
) -> SubaccountsResponse:
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
    return change_supplementary_offering(
        msisdn, settings.registration_gift_offer_id, True
    )


@router.post(
    "/charge-voucher",
    response_model=ApiResponse,
)
async def charge_voucher(
    msisdn: str = Body(..., regex=rgx.MSISDN, example="7839921514"),
    pincode: str = Body(..., regex=rgx.DIGITS, max_length=20, example="123456"),
    session_msisdn=Depends(JWTBearer()),
) -> ApiResponse:
    return recharge_voucher(msisdn, pincode)
