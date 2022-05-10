sim0 = {
    "code": 0,
    "message": "Normal, no NBA",
    "nba": {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}
sim1 = {
    "code": 1,
    "message": "Restricted, recharge!",
    "nba": {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}
sim2 = {
    "code": 2,
    "message": "Restricted, call support!",
    "nba": {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}
sim3 = {
    "code": 3,
    "message": "Pre-active, make first call!",
    "nba": {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}
usim_cta = {
    "code": 4,
    "message": "Legacy SIM, upgrade to 4G!",
    "nba": {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}
sim9999 = {
    "code": 9999,
    "message": "Unknown SIM combination",
    "nba": {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}

sim_nba_lookup = {
    "B01": {1: sim0, 2: sim1, 3: sim1, 4: sim2, 5: sim2},
    "B02": {
        1: sim2,
        4: sim2,
    },
    "B03": {1: sim2, 2: sim2, 3: sim2, 4: sim2, 5: sim2},
    "B04": {1: sim2, 2: sim2, 3: sim2, 4: sim2, 5: sim2},
    "B06": {0: sim3},
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

# fake for now, in IQD
negcred_lookup: dict[int, int] = {
    991: 2000,
    992: 4000,
    993: 6000,
    994: 8000,
    995: 10000,
    996: 12000,
}
