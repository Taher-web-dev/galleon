""" Zain backend services (aka zend) """

import os
import requests
import requests_mock
from typing import Any
from pathlib import Path
from api.models.response import ApiException, ApiResponse
from api.number.subaccount import Subaccount
from api.models.utils import api_exception, api_response
from api.models.data import Error
from utils.settings import settings
from fastapi import status
from api.number import cms
from .sim_helper import get_unified_sim_status

zend_check_4g_api = f"{settings.zend_api}wewebit/query-usim-service/"

zend_balance_api = f"{settings.zend_api}esb/query-balance/"
zend_sim_api = f"{settings.zend_api}esb/subscriber-information/"
zend_recharge_voucher_api = f"{settings.zend_api}esb/recharge-voucher"
zend_payment_voucher_api = f"{settings.zend_api}esb/payment-voucher"
zend_subscriptions_api = f"{settings.zend_api}cbs/query-mgr-service/"
zend_send_sms_api = f"{settings.zend_api}sms/send"
zend_free_units_api = f"{settings.zend_api}esb/free-units"
zend_change_supplementary_offering_api = (
    f"{settings.zend_api}esb/change-supplementary-offering"
)
zend_query_bill = f"{settings.zend_api}esb/billing-details/"

path = f"{os.path.dirname(__file__)}/mocks/"

headers = {"Content-Type": "application/json"}


def get_free_units(msisdn: str) -> list[Subaccount]:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                f"{zend_free_units_api}/{msisdn}",
                text=Path(f"{path}./zand_free_units.json").read_text(),
            )
            response = requests.get(f"{zend_free_units_api}/{msisdn}")
    else:
        response = requests.get(f"{zend_free_units_api}/{msisdn}")

    if not response.ok:
        raise api_exception(response)

    free_units: list[Subaccount] = []
    json_response = response.json().get("data")
    for one in json_response["free_units"]:
        free_units.append(
            Subaccount(
                account_type=one["account_type"],
                amount=one["amount"],
                expiry_date=one["expiry_date"],
            )
        )

    return free_units


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
                zend_change_supplementary_offering_api,
                headers=headers,
                json=request_data,
            )
    else:
        response = requests.post(
            zend_change_supplementary_offering_api, headers=headers, json=request_data
        )
    if not response.ok:
        raise api_exception(response)
    return api_response(response)


def recharge_voucher(msisdn: str, pin: str) -> ApiResponse:
    request_data = {"msisdn": msisdn, "pincode": pin}

    not_eligible_exception = ApiException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error=Error(
            code=99,
            type="number",
            message="this phone number is not eligible to receive vouchers",
        ),
    )

    backend_sim_status = zend_sim(msisdn)

    if backend_sim_status.get("subscriber_type") not in [0, 1]:
        raise not_eligible_exception

    url = ""

    if backend_sim_status["is_post_paid"]:
        url = zend_payment_voucher_api
    elif backend_sim_status["is_pre_paid"]:
        url = zend_recharge_voucher_api
    else:
        raise not_eligible_exception

    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.post(
                url,
                text=Path(f"{path}./zend_recharge_voucher.json").read_text(),
            )
            response = requests.post(url, headers=headers, json=request_data)
    else:
        response = requests.post(url, headers=headers, json=request_data)
    if not response.ok:
        raise api_exception(response)
    return api_response(response)


def zend_send_sms(msisdn: str, message: str) -> dict:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.post(
                zend_send_sms_api, text=Path(f"{path}./zend_sms_sent.json").read_text()
            )
            response = requests.post(
                zend_send_sms_api,
                headers=headers,
                json={"msisdn": msisdn, "message": message},
            )
    else:
        response = requests.post(
            zend_send_sms_api,
            headers=headers,
            json={"msisdn": msisdn, "message": message},
        )
    if not response.ok:
        raise api_exception(response)
    return response.json().get("data")


def zend_balance(msisdn: str) -> dict[str, Any]:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                zend_balance_api + msisdn,
                text=Path(f"{path}./zend_balance.json").read_text(),
            )
            response = requests.get(zend_balance_api + msisdn)
    else:
        response = requests.get(zend_balance_api + msisdn)  # , json={"msisdn": msisdn})
    if not response.ok:
        raise api_exception(response)
    return response.json().get("data")


def zend_sim(msisdn: str) -> dict[str, Any]:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                zend_sim_api + msisdn, text=Path(f"{path}./zend_sim.json").read_text()
            )
            response = requests.get(zend_sim_api + msisdn)  # , json={"msisdn": msisdn})
    else:
        response = requests.get(zend_sim_api + msisdn)  # , json={"msisdn": msisdn})

    if not response.ok:
        raise api_exception(response)

    backend_sim_status = response.json().get("data")
    backend_sim_status["is_post_paid"] = (
        (backend_sim_status.get("subscriber_type") == 1)
        and ("crm_status_code" in backend_sim_status)
        and ("crm_status_details" in backend_sim_status)
    )
    backend_sim_status["is_pre_paid"] = (
        backend_sim_status.get("subscriber_type") == 0
    ) and (
        "crm_status_code" in backend_sim_status
        and backend_sim_status["crm_status_code"]
        in cms.SIM_STATUS_LOOKUP_PREPAID_CONSUMER_MOBILE
        and "cbs_status_code" in backend_sim_status
        and backend_sim_status["cbs_status_code"]
        in cms.SIM_STATUS_LOOKUP_PREPAID_CONSUMER_MOBILE[
            backend_sim_status["crm_status_code"]
        ]
    )
    unified_sim_status = get_unified_sim_status(backend_sim_status)

    backend_sim_status["unified_sim_status"] = unified_sim_status
    backend_sim_status["is_eligible"] = settings.mock_zain_api | (
        "BLOCK" not in unified_sim_status
    )

    return backend_sim_status


def zend_subscriptions(msisdn: str) -> list[dict[str, Any]]:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                zend_subscriptions_api + msisdn,
                text=Path(f"{path}./zend_mgr_service.json").read_text(),
            )
            response = requests.get(zend_subscriptions_api + msisdn)
    else:
        response = requests.get(zend_subscriptions_api + msisdn)
    if not response.ok:
        raise api_exception(response)
    return response.json().get("data").get("subscriptions")


def query_bill(msisdn: str) -> ApiResponse:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            m.get(
                zend_query_bill + msisdn,
                text=Path(f"{path}./query_bill.json").read_text(),
            )
            response = requests.get(zend_query_bill + msisdn)
    else:
        response = requests.get(zend_query_bill + msisdn)
    if not response.ok:
        raise api_exception(response)
    return api_response(response)


def zend_change_subscription(
    msisdn: str, offer_id: int, subscribe: bool
) -> ApiResponse:
    request_data = {"msisdn": msisdn, "offer_id": offer_id, "add_offering": subscribe}

    if settings.mock_zain_api:
        mock_path = f"{path}./zend_change_supplementary_offering.json"
        with requests_mock.Mocker() as m:
            m.post(
                zend_change_supplementary_offering_api,
                text=Path(mock_path).read_text(),
            )
            response = requests.post(
                zend_change_supplementary_offering_api,
                headers=headers,
                json=request_data,
            )
    else:
        response = requests.post(
            zend_change_supplementary_offering_api, headers=headers, json=request_data
        )

    if not response.ok:
        raise api_exception(response)
    return api_response(response)


def is_4g_compatible(msisdn: str) -> bool:

    if settings.mock_zain_api:
        mock_path = f"{path}./zend_query-usim-service.json"
        with requests_mock.Mocker() as m:
            m.post(
                zend_check_4g_api,
                text=Path(mock_path).read_text(),
            )
            response = requests.post(
                zend_check_4g_api,
                headers=headers,
            )
            return response.json().get("data").get("is_4g_compatible")

    response = requests.get(zend_check_4g_api + msisdn)

    return response.json().get("data").get("is_4g_compatible")
