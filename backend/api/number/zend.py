""" Zain backend services (aka zend) """

import os
import requests
import requests_mock
from typing import Any
from pathlib import Path
from api.models.response import ApiResponse
from api.models.utils import build_exception, build_response
from api.models.data import Status
from utils.settings import settings

zend_balance_api = f"{settings.zend_api}esb/query-balance/"
zend_sim_api = f"{settings.zend_api}esb/subscriber-information/"
zend_recharge_voucher_api = f"{settings.zend_api}esb/recharge-voucher"
zend_subscriptions_api = f"{settings.zend_api}cbs/query-mgr-service/"
zend_send_sms_api = f"{settings.zend_api}sms/send/"
zend_change_supplementary_offering_api = (
    f"{settings.zend_api}esb/change-supplementary-offering"
)

path = f"{os.path.dirname(__file__)}/mocks/"


def change_supplementary_offering(
    msisdn: str, offer_id: str, add_offering: bool
) -> ApiResponse:
    request_data = {
        "msisdn": msisdn,
        "offer_id": offer_id,
        "add_offering": add_offering,
    }
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.post(
                zend_change_supplementary_offering_api,
                text=Path(
                    f"{path}./zend_change_supplementary_offering.json"
                ).read_text(),
            )
            response = requests.post(
                zend_change_supplementary_offering_api, json=request_data
            )
            return response.json()

    response = requests.post(zend_change_supplementary_offering_api, json=request_data)
    return response


def recharge_voucher(msisdn: str, pin: str) -> ApiResponse:
    request_data = {"msisdn": msisdn, "pincode": pin}
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.post(
                zend_recharge_voucher_api,
                text=Path(f"{path}./zend_recharge_voucher.json").read_text(),
            )
            response = requests.post(zend_recharge_voucher_api, json=request_data)
            return response.json()

    response = requests.post(zend_recharge_voucher_api, json=request_data)
    print("request_data", request_data)
    print("response", response)
    return response


def zend_send_sms(msisdn: str, message: str) -> dict:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.post(
                zend_send_sms_api, text=Path(f"{path}./zend_sms_sent.json").read_text()
            )
            response = requests.post(
                zend_send_sms_api, json={"msisdn": msisdn, "message": message}
            )
            return response.json()

    response = requests.post(
        zend_send_sms_api, json={"msisdn": msisdn, "message": message}
    )

    if not response.ok:
        raise build_exception(response)
    return response.json()


def zend_balance(msisdn: str) -> dict[str, Any]:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                zend_balance_api + msisdn,
                text=Path(f"{path}./zend_balance.json").read_text(),
            )
            response = requests.get(
                zend_balance_api + msisdn
            )  # , json={"msisdn": msisdn})
            json = response.json()
            return json["data"]

    response = requests.get(zend_balance_api + msisdn)  # , json={"msisdn": msisdn})
    json = response.json()
    return json["data"]


def zend_sim(msisdn: str) -> dict[str, Any]:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                zend_sim_api + msisdn, text=Path(f"{path}./zend_sim.json").read_text()
            )
            response = requests.get(zend_sim_api + msisdn)  # , json={"msisdn": msisdn})
            json = response.json()
            return json["data"]

    response = requests.get(zend_sim_api + msisdn)  # , json={"msisdn": msisdn})
    json = response.json()
    return json["data"]


def zend_subscriptions(msisdn: str) -> list[dict[str, Any]]:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                zend_subscriptions_api + msisdn,
                text=Path(f"{path}./zend_mgr_service.json").read_text(),
            )
            response = requests.get(zend_subscriptions_api + msisdn)
            json = response.json()
            return json["data"]["subscriptions"]

    response = requests.get(zend_subscriptions_api + msisdn)
    json = response.json()
    return json["data"]["subscriptions"]
