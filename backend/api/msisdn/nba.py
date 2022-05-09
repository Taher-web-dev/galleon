from pydantic.main import BaseModel
from typing import Any
import json
from .cms import eligible_primary_offerings, sim_nba_lookup, usim_cta


class Nba(BaseModel):
    customer_name: str
    href: str
    message_en: str
    message_kd: str
    message_kd: str
    href_text_en: str
    href_text_kd: str
    href_text_kd: str


def get_nba(msisdn: str, sim_status: dict) -> Nba:
    """
    Provides NBA for the MSISDN. Covers:
    - 4G call to action for legacy SIM users
    - Call to action for recharge-only or blocked MSISDN
    - Public announcement from Zain marketing team
    - Personalized offer recommendation
    - Etc.

    TODO: Update from basic example that can be used already by frontend team
    Target state for MVP:
    - If we have a 3G SIM, recommend upgrade [no link]
    - Else If we have a SIM NBA of code 1/2/3 i.e., not normal, recommend NBA [could be link to call, recharge]
    - Else randomly iterate through (equal chance on reload):
        - 3 hardcoded offers [deep link to offer page]
        - Zain-Fi app download link [link to external webpage]
    """
    # # get USIM status
    # usim_status = {
    #     "sim_compatible_4G": True
    # }  # Hardcoded until the service is available

    # # blank slate
    # nba: dict = {}

    # # if SIM not 4G eligible
    # if usim_status["sim_compatible_4G"] == 0:
    #     nba = usim_cta

    # # otherwise if we have a mapping for this
    # elif (
    #     "crm_status_code" in sim_status
    #     and sim_status["crm_status_code"] in sim_nba_lookup
    #     and "cbs_status_code" in sim_status
    #     and sim_status["cbs_status_code"]
    #     in sim_nba_lookup[sim_status["crm_status_code"]]
    # ):
    #     # otherwise we carry on with no SIM NBA
    #     # these are our SIM status NBA
    #     sim_status_nba = sim_nba_lookup[sim_status["crm_status_code"]][
    #         sim_status["cbs_status_code"]
    #     ]
    #     if sim_status_nba["code"] != 0:
    #         nba = sim_status_nba
    # else:
    #     pass  # FIXME : What should we do in this case?

    return Nba(
        customer_name="Stephen",
        href="https://apps.iq.zain.com/zain-fi",
        message_en="Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
        message_ar="Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
        message_kd="Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
        href_text_en="View app",
        href_text_ar="View app",
        href_text_kd="View app",
    )
