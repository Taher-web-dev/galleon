# NORMAL
SIM0 = {"code": 0, "message": "Normal"}

# NOT NORMAL BUT CAN ACCESS
SIM1 = {"code": 1, "message": "Recharge"}
SIM2 = {"code": 2, "message": "Support"}

# CANNOT ACCESS - GENERIC BUT KNOWN
SIM90 = {"code": 90, "message": "Critical Support"}

# CANNOT ACCESS - SPECIFIC AND KNOWN
SIM91 = {"code": 91, "message": "Disconnected"}
SIM92 = {"code": 92, "message": "Activate"}

# CANNOT ACCESS - UNKNOWN COMBINATION
SIM99 = {"code": 99, "message": "Critical Support & Log"}

SIM_STATUS_LOOKUP = {
    "B01": {1: SIM0, 2: SIM1, 3: SIM1, 4: SIM2, 5: SIM90},
    "B02": {1: SIM91, 4: SIM90},
    "B03": {0: SIM91, 1: SIM91, 2: SIM91, 3: SIM91, 4: SIM90, 5: SIM90},
    "B04": {1: SIM90, 2: SIM90, 3: SIM90, 4: SIM90, 5: SIM90},
    "B06": {0: SIM92},
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
