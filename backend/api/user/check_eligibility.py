from api.number.zend import zend_sim
from api.number.sim import get_unified_sim_status
from utils.settings import settings


def check_eligibility(msisdn: str):
    backend_sim_status = zend_sim(msisdn)
    unified_sim_status = get_unified_sim_status(backend_sim_status)
    if settings.mock_zain_api:
        return True
    return "BLOCK" not in unified_sim_status
