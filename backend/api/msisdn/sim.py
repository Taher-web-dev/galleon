from pydantic.main import BaseModel
from typing import Any
import json

from .cms import eligible_primary_offerings, sim_nba_lookup, usim_cta, sim9999

from .zend import zend_sim


class AppEligibility(BaseModel):
    code: int
    message: str

    class Config:
        schema_extra = {"example": {"code": 0, "message": "Prepaid B2C Mobile"}}


class SimNba(BaseModel):
    code: int
    message: str

    class Config:
        schema_extra = {"example": {"code": 0, "message": "Normal, no NBA"}}


class Nba(BaseModel):
    href: str
    message_en: str
    message_kd: str
    message_kd: str
    href_text_en: str
    href_text_kd: str
    href_text_kd: str

    class Config:
        schema_extra = {
            "example": {
                "href": "https://apps.iq.zain.com/zain-fi",
                "message_en": "Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
                "message_ar": "Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
                "message_kd": "Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
                "href_text_en": "View app",
                "href_text_ar": "View app",
                "href_text_kd": "View app",
            }
        }


class Sim(BaseModel):
    # wrapper around backend response, mainly for debug
    primary_offering_id: int
    cbs_status_code: int
    crm_status_code: str
    crm_status_details: str
    activation_date: str
    expiry_date: str
    customer_type: str
    subscriber_type: int

    # our injected info
    app_eligibility: AppEligibility
    sim_nba: SimNba
    sim_compatible_4G: bool
    nba: Nba

    # TODO discuss - what does this do & should we include user name here?
    associated_with_user: bool = False

    class Config:
        schema_extra = {
            "example": {
                # backend wrapped response
                "primary_offering_id": 2122764,
                "cbs_status_code": 1,
                "crm_status_code": "B01",
                "crm_status_details": "Normal",
                "activation_date": "2022-01-30 16:00:25+03:00",
                "expiry_date": "2022-05-19 00:00:00+03:00",
                "customer_type": "Individual",
                "subscriber_type": 0,
                # injected info
                "app_eligibility": {"code": 0, "message": "Prepaid B2C Mobile"},
                "sim_nba": {"code": 0, "message": "Normal, no NBA"},
                "sim_compatible_4G": True,
                "nba": {
                    "href": "https://apps.iq.zain.com/zain-fi",
                    "message_en": "Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
                    "message_ar": "Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
                    "message_kd": "Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
                    "href_text_en": "View app",
                    "href_text_ar": "View app",
                    "href_text_kd": "View app",
                },
                # user info
                "associated_with_user": False,
            }
        }


def get_sim_details(msisdn: str) -> Sim:
    """
    Gets info on the provided customer's SIM status incl.
    - Eligibility to use the application
    - Whether SIM is 4G-eligible

    TODO Add WeWebit USIM service - prod. env only
    """
    # fetch SIM status
    sim_status = zend_sim(msisdn)

    # fetch USIM status
    usim_status = {
        "sim_compatible_4G": True
    }  # Hardcoded until the service is available

    # assess app eligibility
    app_eligibility = check_app_eligibility(sim_status)

    sim_nba = get_sim_nba(sim_status)

    nba = get_nba(msisdn, sim_nba, usim_status)

    return Sim(
        # backend response - mainly for debug
        primary_offering_id=sim_status["primary_offering_id"],
        cbs_status_code=sim_status["cbs_status_code"],
        crm_status_code=sim_status["crm_status_code"],
        crm_status_details=sim_status["crm_status_details"],
        activation_date=sim_status["activation_date"],
        expiry_date=sim_status["expiry_date"],
        customer_type=sim_status["customer_type"],
        subscriber_type=sim_status["subscriber_type"],
        
        # injected info
        app_eligibility=app_eligibility,
        sim_nba=sim_nba,
        sim_compatible_4G=usim_status["sim_compatible_4G"],
        nba=nba,

        # user info
        associated_with_user=False,
    )


def check_app_eligibility(sim_status: dict, sim_nba: SimNba) -> dict:
    """
    Given raw backend sim_status response and a sim_nba,
    confirm eligiblity & handling on the app

    TODO should we raise as errors not return?
    """
    # starting point
    app_eligibility = AppEligibility(code=9999, message="Generic ineligibility")

    # handle for missing critical data points
    if "primary_offering_id" not in sim_status:
        return AppEligibility(code=9001, message="Primary offering not found")

    if "customer_type" not in sim_status:
        return AppEligibility(code=9002, message="Customer type not found")

    if "subscriber_type" not in sim_status:
        return AppEligibility(code=9003, message="Subscriber type not found")

    # handle for datapoint validity
    if sim_status["primary_offering_id"] not in eligible_primary_offerings:
        return AppEligibility(code=9004, message="Ineligible primary offering")

    if sim_status["customer_type"] != "Individual":
        return AppEligibility(code=9005, message="Ineligible customer type")

    if sim_status["subscriber_type"] != 0:
        return AppEligibility(code=9006, message="Ineligible subscriber type")

    # handle for sim-specific issues
    if sim_nba.code == 2:
        return AppEligibility(code=9007, message="Blocked SIM card - call support")

    # handle for our one specific eligibility (a bit redundant but later will make sense with postpaid)
    if sim_status["subscriber_type"] == 0:
        return AppEligibility(code=0, message="Prepaid B2C Mobile")

    return app_eligibility


def get_sim_nba(sim_status: dict) -> SimNba:
    """
    Based on provided sim_status (with CRM and CBS code keys),
    we return the next best action for the SIM e.g., to recharge.

    sim_status: dict should contain crm_status_code & cbs_status_code from Zain backend.

    Example response:
    {"code": 0, "message": "Normal, no NBA"}
    {"code": 1, "message": "Restricted, recharge!"}
    """
    if (
        "crm_status_code" in sim_status
        and sim_status["crm_status_code"] in sim_nba_lookup
        and "cbs_status_code" in sim_status
        and sim_status["cbs_status_code"]
        in sim_nba_lookup[sim_status["crm_status_code"]]
    ):
        nba = sim_nba_lookup[sim_status["crm_status_code"]][
            sim_status["cbs_status_code"]
        ]
        return SimNba(code=nba["code"], message=nba["message"])
    else:
        # TODO log this & ideally post to Slack or the CMS (later)
        return SimNba(code=sim9999["code"], message=sim9999["message"])


def get_nba(msisdn: str, sim_nba: SimNba, usim_status: dict) -> Nba:
    """
    Provides NBA for the MSISDN. Covers:
    - 4G call to action for legacy SIM users
    - Call to action for recharge-only or blocked MSISDN
    - Public announcement from Zain marketing team
    - Personalized offer recommendation
    - Etc.

    TODO: Update from basic example that can be used already by frontend team
    Target state for MVP:
    1. If we have a SIM NBA of code 1/2/3 i.e., not normal, recommend NBA [could be link to call, recharge]
    2. Else If we have a 3G SIM, recommend upgrade [no link]
    3. Else randomly iterate through (equal chance on reload):
        - N top price point offers [deep link to offer page] the MSISDN is eligible for
        - Zain-Fi app download link [link to external webpage]
    """
    # blank slate
    nba: dict = {}

    # if we get a SIM status NBA that makes sense i.e., not normal or unknown, use it
    if sim_nba.code not in [0, 9999]:
        nba = {**sim_nba["nba"]}

    # otherwise, if SIM not 4G eligible then use this one
    elif usim_status["sim_compatible_4G"] == 0:
        nba = {**usim_cta["nba"]}

    # TODO this is where we'll put step 3 logic later incl. offers (which could be driven by MSISDN)
    else:
        pass

    # for now, returning the basic object because we will need deep-links or discussion with FE
    # for certain actions and they can be added later
    return Nba(
        href="https://apps.iq.zain.com/zain-fi",
        message_en="Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
        message_ar="Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
        message_kd="Hello {{customer_name}}, did you hear about our new Zain-Fi app?",
        href_text_en="View app",
        href_text_ar="View app",
        href_text_kd="View app",
    )
