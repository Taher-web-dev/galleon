from api.number.balance import Wallet
from utils.api_responses import ApiResponse
from .sim import Sim
from .subscriptions import Subscription


class RetrieveStatusResponse(ApiResponse):
    data: Sim


class SubscriptionsResponse(ApiResponse):
    data: list[Subscription]


class WalletResponse(ApiResponse):
    data: Wallet


class RegistrationGiftResponse(ApiResponse):
    data: dict  # TODO: define model


class ChargeVoucherResponse(ApiResponse):
    data: dict  # TODO: define model
