from api.number.balance import Wallet
from api.models.response import ApiResponse
from api.number.sim import Sim
from api.number.subscriptions import Subscription


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
