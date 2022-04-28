from pydantic.main import BaseModel
from typing import Any
import json

from .cms import (
    eligible_primary_offerings, 
    sim_nba_lookup,
    usim_cta)

from .zend import zend_sim

class Sim(BaseModel):
    app_eligibility: dict
    customer_type: str # = "Individual"
    subcriber_type: int # = 0
    sim_status_nba: dict[str, Any]

def get_sim_details(msisdn: str) -> Sim:
    """
    Gets info on the provided customer's SIM status incl.
    - Eligibility to use the application
    - Recommended NBA (if any) in case of old sim, NBA is to upgrade to 4G sim

    TODO Combines Zain backend response with the WeWebit USIM service
    """
    sim_status= zend_sim(msisdn)
    # print(json.dumps(sim_status, indent=2))
    """
	{
	  "activation_date": "2022-01-30 16:00:25+03:00",
	  "cbs_status_code": 1,
	  "crm_status_code": "B01",
	  "crm_status_details": "Normal",
	  "customer_type": "Individual",
	  "expiry_date": "2022-05-19 00:00:00+03:00",
	  "primary_offering_id": 2122764,
	  "subscriber_type": 0
	}
    """
    usim_status={"sim_compatible_4G": True} # Hardcoded until the service is available

    app_eligibility = {"code": 9999, "message": "Ineligible"}
    if "primary_offering_id" in sim_status and sim_status["primary_offering_id"] in eligible_primary_offerings:
        app_eligibility = {"code": 0, "message": "Prepaid B2C Mobile"}

    # this function currently only handles for (1) B2C (2) prepaid customers only
    assert sim_status["customer_type"] == "Individual", "Consumer customers only"
    assert sim_status["subscriber_type"] == 0, "Prepaid customers only"
    
    # we overwrite the no SIM NBA if the customer does not have a 4G SIM
    sim_status_nba: dict = {} 
    if usim_status["sim_compatible_4G"] == 0:
        sim_status_nba = usim_cta
    elif "crm_status_code" in sim_status and sim_status["crm_status_code"] in sim_nba_lookup and "cbs_status_code" in sim_status and sim_status["cbs_status_code"] in sim_nba_lookup[sim_status["crm_status_code"]]:
        # otherwise we carry on with no SIM NBA
        # these are our SIM status NBA
        sim_status_nba = sim_nba_lookup[sim_status["crm_status_code"]][sim_status["cbs_status_code"]]
    else: 
        pass # FIXME : What should we do in this case?

    return Sim(
        app_eligibility=app_eligibility, 
        sim_status_nba=sim_status_nba,
        customer_type=sim_status["customer_type"],
        subcriber_type=sim_status["subscriber_type"])

