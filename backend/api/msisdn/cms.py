SIM0 = {"code": 0, "message": "Activate"}
SIM1 = {"code": 1, "message": "Normal"}
SIM2 = {"code": 2, "message": "Recharge"}
SIM3 = {"code": 3, "message": "Support"}  # PLACEHOLDER, NOT USED
SIM90 = {"code": 90, "message": "Critical Support"}
SIM99 = {"code": 99, "message": "Critical Support & Log"}

SIM_STATUS_LOOKUP = {
    "B01": {1: SIM1, 2: SIM2, 3: SIM2, 4: SIM90, 5: SIM90},
    "B02": {1: SIM90, 4: SIM90},
    "B03": {1: SIM90, 2: SIM90, 3: SIM90, 4: SIM90, 5: SIM90},
    "B04": {1: SIM90, 2: SIM90, 3: SIM90, 4: SIM90, 5: SIM90},
    "B06": {0: SIM0},
}

SIM_NBA_LOOKUP = {
    0: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
    1: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
    2: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
    3: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
    90: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
    99: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}


USIM_NBA = {
    "href": "",
    "message_en": "",
    "message_ar": "",
    "message_kd": "",
    "href_text_en": "",
    "href_text_ar": "",
    "href_text_kd": "",
}


eligible_primary_offerings: list[int] = [
    100100,
    100163,
    100133,
    100129,
    2206693,
    100121,
    100120,
    100119,
    100107,
    100108,
    100111,
    2141792,
    100102,
    2176843,
    2201842,
    100130,
    100115,
    100114,
    100113,
    2119793,
    100104,
    100116,
    2229894,
    2231751,
]

# using CBS ID - other IDs available if needed; in IQD
# apparently this is consistent across TB and production envs for CBS IDs
negcred_lookup: dict[int, int] = {
    2086106: 2000,
    2086107: 4000,
    2086108: 6000,
    2086109: 8000,
    2086110: 10000,
    2086111: 12000,
}
