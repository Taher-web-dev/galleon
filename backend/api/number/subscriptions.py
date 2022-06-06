import os
from pathlib import Path
from pydantic import Field
import requests
import requests_mock
from api.models.utils import api_exception, api_response
from api.models.response import ApiResponse
from utils.settings import settings
from .zend import zend_subscriptions
from pydantic.main import BaseModel
from typing import Any
from datetime import datetime


subscription_subscribe_api = f"{settings.zend_api}kyo/subscribe"
subscription_unsubscribe_api = f"{settings.zend_api}kyo/unsubscribe"

path = f"{os.path.dirname(__file__)}/mocks/"
headers = {"Content-Type": "application/json"}


class Subscription(BaseModel):
    id: int = Field(None, example=991)
    cycle_start: str = Field(None, example="2022-04-26 00:00:00+03:00")
    cycle_end: str = Field(None, example="2022-04-18 00:00:00+03:00")
    effective_time: str = Field(None, example="2022-04-18 13:12:29+03:00")
    expire_time: str = Field(
        None,
        example="2037-01-01 00:00:00+03:00",
    )
    status: int = Field(None, example=0)

    app_handling: str = ""
    offer: dict = {}

    def load(self, raw: dict[str, Any]):
        self.status = int(raw.get("status", 0))

        self.id = raw["offer_id"]
        if "expire_time" in raw and raw["expire_time"]:
            self.expire_time = int(
                datetime.fromisoformat(raw["expire_time"]).timestamp()
            )

        # print(raw["cycle_end"], raw["id"])
        if "cycle_end" in raw and raw["cycle_end"]:
            self.cycle_end = int(datetime.fromisoformat(raw["cycle_end"]).timestamp())
        self.app_handling = self.get_app_handling()
        self.offer = self.get_offer()
        return self

    def get_offer(self) -> dict:
        """Placeholder for fetching CMS offer details"""
        return {"name": "Offer ABC"}

    def is_relevant(self) -> bool:
        """If an offer should be listed on the app"""
        # cycle end date exists i.e., recurring or temporary offer
        # not an expired or soon-to-be expired offer
        # not an expired or soon-to-be expired offer
        # print(self.id, self.cycle_end, self.status, self.expire_time)
        # print(int(datetime.today().timestamp()))
        # 2022-04-18 00:00:00+03:00
        return (
            # TODO disscuss this
            not self.cycle_end
            and not self.expire_time
            and datetime.fromisoformat(self.cycle_end)
            < datetime.fromisoformat(self.expire_time)
            and self.status != 2
            and self.expire_time >= int(datetime.today().timestamp())
        )

    def get_app_handling(self) -> str:
        """How the app should handle an offer"""

        if not self.cycle_end or not self.expire_time:
            return "Invalid"

        if self.status == 0:
            if self.expire_time == self.cycle_end:
                return "Expiring"
            elif self.expire_time > self.cycle_end:
                return "Renewing"
        elif self.status == 1:
            if self.expire_time == self.cycle_end:
                return "Cancelled"
            elif self.expire_time > self.cycle_end:
                return "Suspended"
        return "Invalid"


def get_subscriptions(msisdn: str) -> list[Subscription]:
    """Get subscriptions for the provided msisdn"""
    raw_subscriptions = zend_subscriptions(msisdn)
    """
    [ {
      "id": 991,
      "cycle_end": "2022-04-26 00:00:00+03:00",
      "cycle_start": "2022-04-18 00:00:00+03:00",
      "effective_time": "2022-04-18 13:12:29+03:00",
      "expire_time": "2037-01-01 00:00:00+03:00",
      "status": 0
    } ]
    """

    subscriptions: list[Subscription] = []

    for raw in raw_subscriptions:
        subscription = Subscription().load(raw)

        if subscription.is_relevant():
            subscriptions.append(subscription)

    # print("subscriptions:", subscriptions)
    return subscriptions


def redeem_registration_gift(msisdn: str) -> dict:
    return {"msisdn": msisdn}


def set_subscriptions(msisdn: str, offer_id: int, subscribe: bool) -> ApiResponse:
    request_data = {"msisdn": msisdn, "offer_id": offer_id}

    url = subscription_subscribe_api if subscribe else subscription_unsubscribe_api

    if settings.mock_zain_api:
        mock_path = (
            f"{path}./subscribe.json" if subscribe else f"{path}./unsubscribe.json"
        )
        with requests_mock.Mocker() as m:
            m.post(
                url,
                text=Path(mock_path).read_text(),
            )
            print(mock_path)
            response = requests.post(url, headers=headers, json=request_data)
    else:
        response = requests.post(url, headers=headers, json=request_data)

    if not response.ok:
        raise api_exception(response)
    return api_response(response)
