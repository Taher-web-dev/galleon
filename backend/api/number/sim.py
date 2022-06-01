from pydantic import Field
from pydantic.main import BaseModel

from api.number import cms

from .zend import zend_sim


class Nba(BaseModel):
    href: str = Field(..., example="https://apps.iq.zain.com/zain-fi")
    message_en: str = Field(
        ..., example="Hello {{customer_name}}, did you hear about our new Zain-Fi app?"
    )
    message_ar: str = Field(
        ..., example="Hello {{customer_name}}, did you hear about our new Zain-Fi app?"
    )
    message_kd: str = Field(
        ..., example="Hello {{customer_name}}, did you hear about our new Zain-Fi app?"
    )
    href_text_en: str = Field(..., example="View app")
    href_text_ar: str = Field(..., example="View app")
    href_text_kd: str = Field(..., example="View app")


class Sim(BaseModel):
    # wrapper around backend response, mainly for debug
    primary_offering_id: int = Field(..., example=2122764)
    cbs_status_code: int = Field(..., example=1)
    crm_status_code: str = Field(..., example="B01")
    crm_status_details: str = Field(..., example="Normal")
    activation_date: str = Field(..., example="2022-01-30 16:00:25+03:00")
    expiry_date: str = Field(..., example="2022-05-19 00:00:00+03:00")
    customer_type: str = Field(..., example="Individual")
    subscriber_type: int = Field(..., example=0)

    # our injected info
    unified_sim_status: str = Field(..., example="apNORMALp")
    is_4g_compatible: bool = Field(..., example=True)
    nba: Nba

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
    usim_status = {"is_4g_compatible": True}

    # get details
    unified_sim_status = get_unified_sim_status(backend_sim_status)
    nba = get_nba(msisdn, unified_sim_status, usim_status, backend_sim_status)

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
        unified_sim_status=unified_sim_status,
        is_4g_compatible=usim_status["is_4g_compatible"],
        nba=nba,
        # user info
        associated_with_user=False,  # FIXME
    )


def get_unified_sim_status(backend_sim_status: dict) -> str:
    """
    Based on provided sim_status (with customer/subscriber type, etc. CRM and CBS code keys),
    we return the next best action for the SIM e.g., to recharge.

    sim_status: dict should contain crm_status_code & cbs_status_code & cms_status_details from Zain backend.

    Responses fit into "NORMAL", "WARN_X" and "BLOCK_Y" taxonomy.

    Illustrative responses:
    "NORMAL" vs. "WARN_RECHARGE" vs. "BLOCK_DISCONNECTED"
    """
    # first check fundamental SIM-level issues to ensure it's prepaid or postpaid (not hybrid)
    if backend_sim_status.get("subscriber_type") not in [0, 1]:
        return cms.BLOCK_UNSUPPORTED_SUBSCRIBER_TYPE

    if backend_sim_status["customer_type"] != "Individual":
        return cms.BLOCK_UNSUPPORTED_CUSTOMER_TYPE

    if backend_sim_status["primary_offering_id"] not in cms.ELIGIBLE_PRIMARY_OFFERINGS:
        return cms.BLOCK_INELIGIBLE_PRIMARY_OFFERING

    # prepaid
    if backend_sim_status.get("subscriber_type") == 0:
        if (
            "crm_status_code" in backend_sim_status
            and backend_sim_status["crm_status_code"]
            in cms.SIM_STATUS_LOOKUP_PREPAID_CONSUMER_MOBILE
            and "cbs_status_code" in backend_sim_status
            and backend_sim_status["cbs_status_code"]
            in cms.SIM_STATUS_LOOKUP_PREPAID_CONSUMER_MOBILE[
                backend_sim_status["crm_status_code"]
            ]
        ):
            return cms.SIM_STATUS_LOOKUP_PREPAID_CONSUMER_MOBILE[
                backend_sim_status["crm_status_code"]
            ][backend_sim_status["cbs_status_code"]]

    # postpaid
    if (
        backend_sim_status.get("subscriber_type") == 1
        and "crm_status_code" in backend_sim_status
        and "crm_status_details" in backend_sim_status
    ):
        if (
            backend_sim_status["crm_status_details"]
            in cms.SIM_STATUS_LOOKUP_POSTPAID_CONSUMER_MOBILE
        ):
            return cms.SIM_STATUS_LOOKUP_POSTPAID_CONSUMER_MOBILE[
                backend_sim_status["crm_status_code"]
            ][backend_sim_status["crm_status_details"]]
        else:
            return cms.SIM_STATUS_LOOKUP_POSTPAID_CONSUMER_MOBILE[
                backend_sim_status["crm_status_code"]
            ]["unhandled"]

    return cms.BLOCK_UNKNOWN_SIM_STATUS_COMBINATION


def get_nba(
    msisdn: str, unified_sim_status: str, usim_status: dict, backend_sim_status: dict
) -> Nba:
    """
    Provides NBA for the MSISDN. Covers:
    - Call to action for recharge-only, must-pay-bill SIMs
    - 4G call to action for legacy SIM users
    - Postpaid prime promotion
    - Zain-Fi app push
    - Etc.

    See https://oryx2020.atlassian.net/browse/GAL-23
    """
    # if we get a SIM status NBA that isn't normal, use it [we know it isn't NORMAL or BLOCK_X]
    if unified_sim_status != "NORMAL" and unified_sim_status in cms.SIM_NBA_LOOKUP:
        return Nba(**cms.SIM_NBA_LOOKUP[unified_sim_status])

    # otherwise, if SIM not 4G eligible then use this one
    if usim_status["is_4g_compatible"] == 0:
        return Nba(**cms.SIM_NBA_LOOKUP[cms.WARN_NOT_4G_COMPATIBLE])

    # non-Prime postpaid special handling
    if (
        backend_sim_status["subscriber_type"] == 1
        and backend_sim_status["primary_offering_id"]
        not in cms.POSTPAID_PRIME_PRIMARY_OFFERINGS
    ):
        return Nba(**cms.POSTPAID_PRIME_NBA)

    # otherwise we fall back to Zain-Fi app
    return Nba(**cms.ZAINFI_NBA)
