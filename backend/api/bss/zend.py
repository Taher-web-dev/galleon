import os
import requests
import requests_mock
from typing import Any
from pathlib import Path
from utils.settings import settings

zend_balance_api = settings.zend_api + "esb/query-balance/"
zend_sim_api = settings.zend_api + "esb/query-subscriber-information/"
zend_subscriptions_api = settings.zend_api + "cbs/query-mgr-service/"
zend_send_sms_api = settings.zend_api + "sms/send/"

path = os.path.dirname(__file__) + "/mocks/"

def zend_send_otp(msisdn: str) -> None:
    with requests_mock.Mocker() as m:
        m.get(zend_send_sms_api, text=Path(path+'./zend_otp_sent.json').read_text())
        response = requests.post(zend_send_sms_api, json={"msisdn": msisdn, "message": "Hello world"})
        return response.json()


def zend_balance(msisdn: str) -> dict[str, Any]:
    with requests_mock.Mocker() as m:
        m.get(zend_balance_api+msisdn, text=Path(path+'./zend_balance.json').read_text())
        response = requests.get(zend_balance_api+msisdn) # , json={"msisdn": msisdn})
        json = response.json()
        return json["data"]

def zend_sim(msisdn: str) -> dict[str, Any]:
    with requests_mock.Mocker() as m:
        m.get(zend_sim_api+msisdn, text=Path(path+'./zend_sim.json').read_text())
        response = requests.get(zend_sim_api+msisdn) # , json={"msisdn": msisdn})
        json = response.json()
        return json["data"]


def zend_subcriptions(msisdn: str) -> list[dict[str,Any]]:
    with requests_mock.Mocker() as m:
        m.get(zend_subscriptions_api+msisdn, text=Path(path+'./zend_mgr_service.json').read_text())
        response = requests.get(zend_subscriptions_api+msisdn) 
        json = response.json()
        return json["data"]["subscriptions"]

