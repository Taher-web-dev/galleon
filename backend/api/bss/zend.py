import os
import requests
import requests_mock
from typing import Any
from pathlib import Path
from utils.settings import settings

zend_balance_api       = settings.zend_api + "esb/query-balance/"
zend_sim_api    = settings.zend_api + "esb/query-subscriber-information/"
zend_subscriptions_api = settings.zend_api + "cbs/query-mgr-service/"

path = os.path.dirname(__file__) + "/mocks/"

def zend_balance(msisdn: str) -> dict[str, Any]:
    with requests_mock.Mocker() as m:
        m.post(zend_balance_api, text=Path(path+'./zend_balance.json').read_text())
        response = requests.post(zend_balance_api, json={"msisdn": msisdn})
        json = response.json()
        return json["data"]

def zend_sim(msisdn: str) -> dict[str, Any]:
    with requests_mock.Mocker() as m:
        m.post(zend_sim_api, text=Path(path+'./zend_sim.json').read_text())
        response = requests.post(zend_sim_api, json={"msisdn": msisdn})
        json = response.json()
        return json["data"]


def zend_subcriptions(msisdn: str) -> list[dict[str,Any]]:
    with requests_mock.Mocker() as m:
        m.post(zend_subscriptions_api, text=Path(path+'./zend_mgr_service.json').read_text())
        response = requests.post(zend_subscriptions_api, json={"msisdn": msisdn})
        json = response.json()
        return json["data"]["subscriptions"]

