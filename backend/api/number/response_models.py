from utils.api_responses import ApiResponse
from .sim import Sim
from .subscriptions import Subscription


class StatusResponse(ApiResponse):
    data: Sim


class SubscriptionsResponse(ApiResponse):
    data: list[Subscription]
