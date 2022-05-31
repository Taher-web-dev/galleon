from json.decoder import JSONDecodeError
from pydantic import Field
from pydantic.main import BaseModel
from typing import Optional, Any
from fastapi import status
from api.models.response import ApiException
from api.models.data import Error
from .cms import NEGCRED_LOOKUP
from .zend import zend_balance, zend_subscriptions


class WalletEntry(BaseModel):
    value: Optional[int] = Field(None, example=1014)
    expiry: Optional[str] = Field(None, example="2029-09-21T00:00:00.000+03:00")


class Wallet(BaseModel):
    balance: WalletEntry
    loan: WalletEntry


def get_wallet(msisdn: str) -> Wallet:
    """Main wallet balance + negative credit subscription"""

    try:
        raw_balance: dict[str, Any] = zend_balance(msisdn)
        """{"amount": 100000, "validity":"20220801"}"""
        raw_subscriptions: list[dict[str, Any]] = zend_subscriptions(msisdn)
        """[{"id": "123", "cyle_end": "20220426000000", "expire_time":"20370101000000"}]"""

        loan = WalletEntry(value=None, expiry=None)
        for sub in raw_subscriptions:
            if sub["offer_id"] in NEGCRED_LOOKUP:
                loan.value = NEGCRED_LOOKUP[sub["id"]]
                loan.expiry = sub["cycle_end"]  # expiry_time timestamp?
                break

        amount = int(raw_balance["amount"]) // 1_000  # convert from Fils to IQD
        balance = WalletEntry(value=amount, expiry=str(raw_balance["validity"]))
        return Wallet(balance=balance, loan=loan)
    except JSONDecodeError as ex:
        raise ApiException(
            status.HTTP_400_BAD_REQUEST,
            Error(type="wallet", code=10, message="Invalid wallet op"),
        ) from ex
