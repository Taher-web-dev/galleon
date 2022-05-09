from pydantic.main import BaseModel
from typing import Any
import json

from .cms import eligible_primary_offerings, sim_nba_lookup, usim_cta

from .zend import zend_sim


class Sim(BaseModel):
    app_eligibility: dict
    customer_type: str  # = "Individual"
    subcriber_type: int  # = 0
    sim_compatible_4G: bool
    associated_with_user: bool = False

    class Config:
        schema_extra = {
            "example": {
                "associated_with_user": False,
                "is_eligible": True,
                "customer_type": "Individual",
                "subscriber_type": 0,
                "primary_offering_id": 2122764,
                "activation_date": "2022-01-30 16:00:25+03:00",
                "cbs_status_code": 1,
                "crm_status_code": "B01",
                "crm_status_details": "Normal",
                "expiry_date": "2022-05-19 00:00:00+03:00",
            }
        }


def get_sim_details(msisdn: str) -> Sim:
    """
    Gets info on the provided customer's SIM status incl.
    - Eligibility to use the application
    - Whether SIM is 4G-eligible

    TODO Add WeWebit USIM service
    """
    # fetch SIM status
    sim_status = zend_sim(msisdn)
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

    # fetch USIM status
    usim_status = {
        "sim_compatible_4G": True
    }  # Hardcoded until the service is available

    # assess app eligibility
    app_eligibility = check_app_eligibility(sim_status)

    return Sim(
        app_eligibility=app_eligibility,
        sim_compatible_4G=usim_status["sim_compatible_4G"],
        customer_type=sim_status["customer_type"],
        subcriber_type=sim_status["subscriber_type"],
    )


def check_app_eligibility(sim_status:dict) -> dict:
    app_eligibility = {"code": 9999, "message": "Ineligible"}

    # TODO do we need to handle for errors in SIM status response or does FastAPI do that?
    if (
        "primary_offering_id" in sim_status
        and sim_status["primary_offering_id"] in eligible_primary_offerings
        and sim_status["customer_type"] == "Individual"
        and sim_status["subscriber_type"] == 0
    ):
        app_eligibility = {"code": 0, "message": "Prepaid B2C Mobile"}

    return app_eligibility
