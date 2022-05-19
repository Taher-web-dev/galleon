from typing import Any, Dict, Union
from utils.api_responses import Error
from api.number.balance import Wallet
from utils.api_responses import ApiResponse
from .sim import Sim
from .subscriptions import Subscription


class StatusResponse(ApiResponse):
    data: Sim


class SubscriptionsResponse(ApiResponse):
    data: list[Subscription]


class WalletResponse(ApiResponse):
    data: Union[Wallet, Error]


class ChargeVoucherResponse(ApiResponse):
    data: Dict[str, Any]
