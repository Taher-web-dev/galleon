from api.number.zend import zend_sim
from api.number.sim import get_unified_sim_status


def check_eligibility(msisdn: str):
    backend_sim_status = zend_sim(msisdn)
    unified_sim_status = get_unified_sim_status(backend_sim_status)
    return "BLOCK" not in unified_sim_status
