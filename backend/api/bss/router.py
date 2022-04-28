""" 
BSS : Business Support Systems
This is the middle-ware that connects with
zain backend systems (aka zain-backend)
"""

from fastapi import APIRouter
from fastapi import Depends

from .balance import get_wallet, Wallet
from .sim import get_sim_details, Sim 
from .subscriptions import get_subscriptions, Subscription
from ..user.router import JWTBearer

router = APIRouter()

@router.get('/status', response_model=Sim)
async def api_status(msisdn = Depends(JWTBearer())) -> Sim:
    return get_sim_details(msisdn)

@router.get('/subscriptions', response_model = list[Subscription])
async def api_subscriptions(msisdn = Depends(JWTBearer())) -> list[Subscription]:
    return get_subscriptions(msisdn)

@router.get('/wallet', response_model = Wallet)
async def api_wallet(msisdn = Depends(JWTBearer())) -> Wallet:
    return get_wallet(msisdn)
