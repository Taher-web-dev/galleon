from json.decoder import JSONDecodeError
from pydantic.main import BaseModel
from typing import Union, Optional, Any
from utils.error import Error

from .cms import NEGCRED_LOOKUP
from .zend import zend_balance, zend_subcriptions


class WalletEntry(BaseModel):
    value: Optional[int]
    expiry: Optional[str]


class Wallet(BaseModel):
    balance: WalletEntry
    loan: WalletEntry

    class Config:
        schema_extra = {
            "example": {
                "balance": {"value": 1014, "expiry": "2029-09-21T00:00:00.000+03:00"},
                "loan": {"value": 2000, "expiry": "2029-04-15T00:00:00.000+03:00"},
            }
        }


def get_wallet(msisdn: str) -> Union[Wallet, Error]:
    """Main wallet balance + negative credit subscription"""

    try:
        raw_balance: dict[str, Any] = zend_balance(msisdn)
        """{"amount": 100000, "validity":"20220801"}"""
        raw_subscriptions: list[dict[str, Any]] = zend_subcriptions(msisdn)
        """[{"id": "123", "cyle_end": "20220426000000", "expire_time":"20370101000000"}]"""

        loan = WalletEntry(value=None, expiry=None)
        for sub in raw_subscriptions:
            if sub["id"] in NEGCRED_LOOKUP:
                loan.value = NEGCRED_LOOKUP[sub["id"]]
                loan.expiry = sub["cycle_end"]  # expiry_time timestamp?
                break

        amount = int(int(raw_balance["amount"]) / 1000)  # convert from Fils to IQD
        balance = WalletEntry(value=amount, expiry=str(raw_balance["validity"]))
        return Wallet(balance=balance, loan=loan)
    except JSONDecodeError:
        return Error()
