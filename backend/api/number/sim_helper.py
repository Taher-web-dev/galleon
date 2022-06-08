from api.number import cms


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
        return "BLOCK_UNSUPPORTED_SUBSCRIBER_TYPE"

    if backend_sim_status["customer_type"] != "Individual":
        return "BLOCK_UNSUPPORTED_CUSTOMER_TYPE"

    if backend_sim_status["primary_offering_id"] not in cms.ELIGIBLE_PRIMARY_OFFERINGS:
        return "BLOCK_INELIGIBLE_PRIMARY_OFFERING"

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

    return "BLOCK_UNKNOWN_SIM_STATUS_COMBINATION"


def get_nba(
    msisdn: str,
    unified_sim_status: str,
    is_4g_compatible: bool,
    backend_sim_status: dict,
) -> str:
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
        return unified_sim_status

    # otherwise, if SIM not 4G eligible then use this one
    if is_4g_compatible == 0:
        return "WARN_NOT_4G_COMPATIBLE"

    # non-Prime postpaid special handling
    if (
        backend_sim_status["subscriber_type"] == 1
        and backend_sim_status["primary_offering_id"]
        not in cms.POSTPAID_PRIME_PRIMARY_OFFERINGS
    ):
        return "POSTPAID_PRIME_NBA"

    # otherwise we fall back to Zain-Fi app
    return "ZAINFI_NBA"
