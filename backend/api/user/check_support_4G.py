from utils.settings import settings
import requests
import requests_mock

zend_check_4G_api = f"{settings.zend_api}wewebit/query-usim-service/"


def check_support_4G(msisdn: str) -> bool:
    if settings.mock_zain_api:
        with requests_mock.Mocker() as m:
            return True
    response = requests.get(zend_check_4G_api + msisdn)
    return response.json().get("data").get("supports_4G")
