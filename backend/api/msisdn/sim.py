from pydantic.main import BaseModel
from typing import Any
import json

from .cms import eligible_primary_offerings, SIM_STATUS_LOOKUP, USIM_NBA, SIM99, SIM_NBA_LOOKUP

from .zend import zend_sim


class SimEligibility(BaseModel):
    code: int
    message: str

    class Config:
        schema_extra = {"example": {"code": 0, "message": "Prepaid B2C Mobile"}}


class MiddlewareSimStatus(BaseModel):
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
    app_eligibility: SimEligibility
    is_eligible: bool
    mw_sim_status: MiddlewareSimStatus
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
                "is_eligible": True,
                "mw_sim_status": {"code": 0, "message": "Normal, no NBA"},
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
    backend_sim_status = zend_sim(msisdn)

    # fetch USIM status
    usim_status = {
        "sim_compatible_4G": True
    }  # Hardcoded until the service is available

    # assess app eligibility
    app_eligibility = check_app_eligibility(backend_sim_status)

    mw_sim_status = get_mw_sim_status(backend_sim_status)

    nba = get_nba(msisdn, mw_sim_status, usim_status)

    return Sim(
        # backend response - mainly for debug
        primary_offering_id=backend_sim_status["primary_offering_id"],
        cbs_status_code=backend_sim_status["cbs_status_code"],
        crm_status_code=backend_sim_status["crm_status_code"],
        crm_status_details=backend_sim_status["crm_status_details"],
        activation_date=backend_sim_status["activation_date"],
        expiry_date=backend_sim_status["expiry_date"],
        customer_type=backend_sim_status["customer_type"],
        subscriber_type=backend_sim_status["subscriber_type"],
        # injected info
        app_eligibility=app_eligibility,
        is_eligible=True if app_eligibility["code"] == 0 else False,
        mw_sim_status=mw_sim_status,
        sim_compatible_4G=usim_status["sim_compatible_4G"],
        nba=nba,
        # user info
        associated_with_user=False,
    )


def check_app_eligibility(backend_sim_status: dict, mw_sim_status: MiddlewareSimStatus) -> dict:
    """
    Given raw backend sim_status response and a sim_nba,
    confirm eligiblity & handling on the app

    TODO should we raise as errors not return?
    """
    # starting point
    app_eligibility = SimEligibility(code=9999, message="Generic ineligibility")

    # handle for missing critical data points
    if (
        "primary_offering_id" not in backend_sim_status
        or "customer_type" not in backend_sim_status
        or "subscriber_type" not in backend_sim_status
    ):
        return SimEligibility(code=9001, message="Incomplete backend response")

    # handle for datapoint validity
    if backend_sim_status["primary_offering_id"] not in eligible_primary_offerings:
        return SimEligibility(code=9002, message="Ineligible primary offering")
    if backend_sim_status["customer_type"] != "Individual":
        return SimEligibility(code=9003, message="Ineligible customer type")
    if backend_sim_status["subscriber_type"] != 0:
        return SimEligibility(code=9004, message="Ineligible subscriber type")

    # handle for sim-specific issues
    if mw_sim_status.code == 90:
        return SimEligibility(code=9007, message="Blocked SIM card - call support")

    if mw_sim_status.code == 0:
        return SimEligibility(code=9008, message="Inactive SIM, please activate")

    if mw_sim_status.code == 99:
        return SimEligibility(
            code=9999, message="Unknown SIM configuration, please investigate"
        )

    # handle for our one specific eligibility (a bit redundant but later will make sense with postpaid)
    if backend_sim_status["subscriber_type"] == 0:
        return SimEligibility(code=0, message="Prepaid B2C Mobile")

    return app_eligibility


def get_mw_sim_status(backend_sim_status: dict) -> MiddlewareSimStatus:
    """
    Based on provided sim_status (with CRM and CBS code keys),
    we return the next best action for the SIM e.g., to recharge.

    sim_status: dict should contain crm_status_code & cbs_status_code from Zain backend.

    Example response:
    {"code": 0, "message": "Normal, no NBA"}
    {"code": 1, "message": "Restricted, recharge!"}
    """
    if (
        "crm_status_code" in backend_sim_status
        and backend_sim_status["crm_status_code"] in SIM_STATUS_LOOKUP
        and "cbs_status_code" in backend_sim_status
        and backend_sim_status["cbs_status_code"]
        in SIM_STATUS_LOOKUP[backend_sim_status["crm_status_code"]]
    ):
        mw_sim_status = SIM_STATUS_LOOKUP[backend_sim_status["crm_status_code"]][
            backend_sim_status["cbs_status_code"]
        ]
        return MiddlewareSimStatus(**mw_sim_status)
    else:
        # TODO log this & ideally post to Slack or the CMS (later)
        return MiddlewareSimStatus(code=SIM99["code"], message=SIM99["message"])


def get_nba(msisdn: str, sim_nba: MiddlewareSimStatus, usim_status: dict) -> Nba:
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

    # if we get a SIM status NBA that isn't normal, use it
    if sim_nba.code != 1:
        nba = Nba(**SIM_NBA_LOOKUP[sim_nba.code])

    # otherwise, if SIM not 4G eligible then use this one
    elif usim_status["sim_compatible_4G"] == 0:
        nba = Nba(**USIM_NBA)

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
