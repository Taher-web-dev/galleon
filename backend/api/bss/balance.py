from pydantic.main import BaseModel
from typing import Any

from .cms import negcred_lookup
from .zend import zend_balance, zend_subcriptions


class WalletEntry(BaseModel):
    value: int | None
    expiry: str | None

class Wallet(BaseModel) :
    balance: WalletEntry 
    loan: WalletEntry 

def get_wallet(msisdn: str) -> Wallet:
    """ Main wallet balance + negative credit subscription """

    raw_balance: dict[str, Any] = zend_balance(msisdn)
    """{"amount": 100000, "validity":"20220801"}"""
    raw_subscriptions: list[dict[str,Any]] = zend_subcriptions(msisdn) 
    """[{"id": "123", "cyle_end": "20220426000000", "expire_time":"20370101000000"}]""" 
    loan = WalletEntry(value=None, expiry=None)
    for sub in raw_subscriptions: 
        if sub["id"] in negcred_lookup:
            loan.value= negcred_lookup[sub["id"]]
            loan.expiry=sub["cycle_end"] # expiry_time timestamp?
            break

    amount = int(int(raw_balance["amount"])/ 1000) # convert from Fils to IQD
    balance = WalletEntry(value = amount, expiry = str(raw_balance["validity"]))
    return Wallet(balance=balance, loan=loan)
