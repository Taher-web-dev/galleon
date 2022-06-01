from api.number.balance import Wallet
from api.number.subaccount import Subaccount
from api.models.response import ApiResponse
from api.number.sim import Sim
from api.number.subscriptions import Subscription


class RetrieveStatusResponse(ApiResponse):
    data: Sim


class SubscriptionsResponse(ApiResponse):
    data: list[Subscription]


class WalletResponse(ApiResponse):
    data: Wallet


class SubaccountsResponse(ApiResponse):
    data: list[Subaccount]

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": [
                    {
                        "account_type": 4425,
                        "amount": 10,
                        "expiry_date": "2037-01-01T00:00:00",
                    },
                    {
                        "account_type": 5016,
                        "amount": 1,
                        "expiry_date": "2037-01-01T00:00:00",
                    },
                ],
            }
        }


class RegistrationGiftResponse(ApiResponse):
    ...


class ChargeVoucherResponse(ApiResponse):
    ...
