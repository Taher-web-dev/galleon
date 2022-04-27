from .mocks import BalanceResponseMock, SubscriptionsResponseMock
from .utils import negcred_lookup


def check_negcred(subscriptions: list) -> dict:
    # later this would be via CMS
    neg_cred_ids = negcred_lookup.keys()

    data = {"loan": {"value": None, "expiry": None}}

    for sub in subscriptions:
        if sub.get("id") in neg_cred_ids:
            data["loan"]["value"] = negcred_lookup[sub.get("id")]
            data["loan"]["expiry"] = sub.get(
                "cycle_end"
            )  # might need to be expire_time, and needs to be a timestamp

    return data


def get_wallet(
    msisdn: str = None, balance_mock: int = 0, subscription_mock: int = 0
) -> dict:
    """
    Combines Zain main wallet with negative credit subscriptions
    """
    # we would replace these with calls to the BE API GW
    # currently handling happy scenario only i.e., no error message
    balance_response = BalanceResponseMock(state=balance_mock).data
    subscriptions_response = SubscriptionsResponseMock(state=subscription_mock).data

    data = {**balance_response.get("data"), **subscriptions_response.get("data")}
    amt = int(data['amount'])/1000 # converts to IQD
    validity = data['validity']

    return {
        "balance": {"value": amt, "expiry": validity},
        **check_negcred(data.get("subscriptions"))
    }
