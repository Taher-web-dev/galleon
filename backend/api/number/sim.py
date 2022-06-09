from pydantic import Field
from pydantic.main import BaseModel
from .zend import is_4g_compatible

from .zend import zend_sim


class Sim(BaseModel):
    # wrapper around backend response, mainly for debug
    primary_offering_id: int = Field(..., example=2122764)
    cbs_status_code: int | None = Field(None, example=1)
    crm_status_code: str = Field(..., example="B01")
    crm_status_details: str = Field(..., example="Normal")
    activation_date: str = Field(..., example="2022-01-30 16:00:25+03:00")
    expiry_date: str = Field(..., example="2022-05-19 00:00:00+03:00")
    customer_type: str = Field(..., example="Individual")
    subscriber_type: int = Field(..., example=0)

    # our injected info
    unified_sim_status: str = Field(..., example="apNORMALp")
    is_4g_compatible: bool = Field(..., example=True)
    is_eligible: bool = Field(..., example=False)
    # nba: Nba

    # TODO discuss - what does this do & should we include user name here?
    associated_with_user: bool = False


def get_sim_details(msisdn: str) -> Sim:
    """
    Gets info on the provided customer's SIM status incl.
    - Eligibility to use the application
    - Whether SIM is 4G-eligible

    TODO Add WeWebit USIM service - prod. env only
    """
    # fetch SIM status & USIM status (hardcode USIM in UAT)
    backend_sim_status = zend_sim(msisdn)

    # get details
    unified_sim_status = zend_sim(msisdn)["unified_sim_status"]
    # nba = get_nba(msisdn, unified_sim_status, usim_status, backend_sim_status)

    return Sim(
        # backend response - mainly for debug
        primary_offering_id=backend_sim_status["primary_offering_id"],
        cbs_status_code=backend_sim_status.get("cbs_status_code", None),
        crm_status_code=backend_sim_status["crm_status_code"],
        crm_status_details=backend_sim_status["crm_status_details"],
        activation_date=backend_sim_status["activation_date"],
        expiry_date=backend_sim_status["expiry_date"],
        customer_type=backend_sim_status["customer_type"],
        subscriber_type=backend_sim_status["subscriber_type"],
        # injected info
        unified_sim_status=unified_sim_status,
        is_4g_compatible=is_4g_compatible(msisdn),
        is_eligible=False if "BLOCK" in unified_sim_status else True,
        # nba=nba,
        # user info
        associated_with_user=False,  # FIXME
    )
