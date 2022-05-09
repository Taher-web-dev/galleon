""" 
BSS : Business Support Systems
This is the middle-ware that connects with
zain backend systems (aka zain-backend)
"""

from fastapi import APIRouter, Body
from fastapi import Depends

from .balance import get_wallet, Wallet
from .sim import get_sim_details, Sim 
from .subscriptions import get_subscriptions, Subscription
from .zend import recharge_voucher
from ..user.router import JWTBearer

router = APIRouter()

@router.get('/sim_status', response_model=Sim)
async def retrieve_status(msisdn = Depends(JWTBearer())) -> Sim:
    """ Retrieve SIM status """
    return get_sim_details(msisdn)

@router.get('/subscriptions', response_model = list[Subscription])
async def retrieve_subscriptions(msisdn = Depends(JWTBearer())) -> list[Subscription]:
    """ Retrieve subscriptions list """
    return get_subscriptions(msisdn)

@router.get('/wallet', response_model = Wallet)
async def retrieve_wallet(msisdn = Depends(JWTBearer())):
    """ Retrieve customer wallet's details (balance and load) """
    return get_wallet(msisdn)

@router.post('/charge_voucher')
async def api_charge_voucher(msisdn = Depends(JWTBearer()), pin : str = Body(...)):
    return recharge_voucher(msisdn, pin)
