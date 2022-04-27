from .utils import sim_nba_lookup, eligible_primary_offerings, usim_cta
from .mocks import SIMResponseMock, USIMResponseMock


def check_primary_offering(primary_offering_id: str) -> dict:
    """
    Checks how the app should handle the customer based on their SIM profile.
    """

    # later need a CMS for this but for now hardcoding
    if primary_offering_id in eligible_primary_offerings:
        primary_offering_result = {"code": 0, "message": "Prepaid B2C Mobile"}
    else:
        primary_offering_result = {"code": 9999, "message": "Ineligible"}
    return primary_offering_result


def get_sim_details(msisdn: str = None, sim_mock:int=0, usim_mock:int=0) -> dict:
    """
    Gets info on the provided customer's SIM status incl.
    - Eligibility to use the application
    - Any next best action to recommend
    - A call to action on upgrading from a legacy SIM to a 4G one

    Combines Zain backend response with the WeWebit USIM service
    """
    # we would replace these with calls to the BE API GW
    # currently handling happy scenario only i.e., no error message
    sim_status_response = SIMResponseMock(state=sim_mock).data
    usim_status_response = USIMResponseMock(state=usim_mock).data

    # unpack data from both services into one dict
    data = {**sim_status_response.get("data"), **usim_status_response.get("data")}

    # we would actually need to raise an error but for now just leaving as a data field
    data["eligible_for_app"] = check_primary_offering(data["primary_offering_id"])

    # this function currently only handles for (1) B2C (2) prepaid customers only
    assert data["customer_type"] == "Individual", "Consumer customers only"
    assert data["subscriber_type"] == "0", "Prepaid customers only"

    # these are our SIM status NBA
    data["sim_status_nba"] = sim_nba_lookup.get(data["crm_status_code"]).get(
        data["cbs_status_code"]
    )

    # we overwrite the no SIM NBA if the customer does not have a 4G SIM
    if data["sim_compatible_4G"] == 0:
        data["sim_status_nba"] = usim_cta

    # otherwise we carry on with no SIM NBA

    return data
