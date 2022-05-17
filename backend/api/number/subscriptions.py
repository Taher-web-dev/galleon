from .zend import zend_subcriptions

from pydantic.main import BaseModel
from typing import Any
from datetime import datetime


class Subscription(BaseModel):
    cycle_end: int = 0
    expire_time: int = 0
    status: int = 0
    app_handling: str = ""
    offer: dict = {}
    id: int = 0

    class Config:
        schema_extra = {
            "example": {
                "id": 991,
                "cycle_end": "2022-04-26 00:00:00+03:00",
                "cycle_start": "2022-04-18 00:00:00+03:00",
                "effective_time": "2022-04-18 13:12:29+03:00",
                "expire_time": "2037-01-01 00:00:00+03:00",
                "status": 0,
            }
        }

    def load(self, raw: dict[str, Any]):
        self.status = int(raw.get("status", 0))

        self.id = raw["id"]
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
        return (
            self.cycle_end > 0
            and self.status != 2
            and self.expire_time >= int(datetime.today().timestamp())
        )

    def get_app_handling(self) -> str:
        """How the app should handle an offer"""
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
    raw_subscriptions = zend_subcriptions(msisdn)
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
    return subscriptions


def redeem_registration_gift(msisdn: str) -> dict:
    return {"msisdn": msisdn}