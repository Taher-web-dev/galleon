import datetime as dt
from .mocks import SubscriptionsResponseMock
from .utils import get_sub_cms_details


def relevant_subscription(sub):
    """
    Tells us whether an offer should be listed on the app
    """
    # set default as irrelevant
    relevant = False

    # cycle end date exists i.e., recurring or temporary offer
    if sub["cycle_end"]:
        # not an expired or soon-to-be expired offer
        if sub["status"] != "2":
            # not an expired or soon-to-be expired offer
            if (
                dt.datetime.strptime(sub["expire_time"], "%Y%m%d%H%M%S")
                >= dt.datetime.today()
            ):
                relevant = True
    return relevant


def label_subscription(sub):
    """
    Tells us how the app should handle an offer
    """
    if sub["status"] == "0":
        if sub["expire_time"] == sub["cycle_end"]:
            sub["app_handling"] = "Expiring"
        elif sub["expire_time"] > sub["cycle_end"]:
            sub["app_handling"] = "Renewing"
    elif sub["status"] == "1":
        if sub["expire_time"] == sub["cycle_end"]:
            sub["app_handling"] = "Cancelled"
        elif sub["expire_time"] > sub["cycle_end"]:
            sub["app_handling"] = "Suspended"
    else:
        raise ValueError
    return sub


def get_subscriptions(msisdn: str = None, subscription_mock: int = 0) -> dict:
    """
    Gets required info on the provided customer's current subscriptions
    """
    # we would replace with calls to the BE API GW
    # currently handling happy scenario only i.e., no error message
    data = SubscriptionsResponseMock(state=subscription_mock).data.get("data")

    # add app handling
    app_handling = [
        label_subscription(sub)
        for sub in data.get("subscriptions")
        if relevant_subscription(sub)
    ]

    # add offer details
    offer_details = [get_sub_cms_details(sub) for sub in app_handling]

    # augment old subscriptions data with new app handling & CMS info
    data["subscriptions"] = offer_details

    return data
