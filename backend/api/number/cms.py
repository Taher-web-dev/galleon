# NORMAL
NORMAL = "NORMAL"

# NOT NORMAL BUT CAN ACCESS WITH WARNING
WARN_RECHARGE = "WARN_RECHARGE"
WARN_MUST_PAY_BILL = "WARN_MUST_PAY_BILL"
WARN_MUST_RECONNECT = "WARN_MUST_RECONNECT"

# CANNOT ACCESS - GENERIC BUT KNOWN
BLOCK_CRITICAL_SUPPORT = "BLOCK_CRITICAL_SUPPORT"

# CANNOT ACCESS - SPECIFIC TO SIM PROFILE ITSELF
BLOCK_UNSUPPORTED_CUSTOMER_TYPE = "BLOCK_UNSUPPORTED_CUSTOMER_TYPE"
BLOCK_UNSUPPORTED_SUBSCRIBER_TYPE = "BLOCK_UNSUPPORTED_SUBSCRIBER_TYPE"
BLOCK_INELIGIBLE_PRIMARY_OFFERING = "BLOCK_INELIGIBLE_PRIMARY_OFFERING"

# CANNOT ACCESS - SPECIFIC TO SIM LIFECYCLE STATUS (FROM LOOKUP)
BLOCK_MUST_ACTIVATE = "BLOCK_MUST_ACTIVATE"
BLOCK_DISCONNECTED = "BLOCK_DISCONNECTED"

# CANNOT ACCESS - UNKNOWN SIM STATUS COMBINATION
BLOCK_UNKNOWN_SIM_STATUS_COMBINATION = "BLOCK_UNKNOWN_SIM_STATUS_COMBINATION"

SIM_STATUS_LOOKUP_PREPAID_CONSUMER_MOBILE = {
    "B01": {
        1: NORMAL,
        2: WARN_RECHARGE,
        3: WARN_RECHARGE,
        4: BLOCK_DISCONNECTED,
        5: BLOCK_CRITICAL_SUPPORT,
    },
    "B02": {1: BLOCK_DISCONNECTED, 4: BLOCK_CRITICAL_SUPPORT},
    "B03": {
        0: BLOCK_DISCONNECTED,
        1: BLOCK_DISCONNECTED,
        2: BLOCK_DISCONNECTED,
        3: BLOCK_DISCONNECTED,
        4: BLOCK_CRITICAL_SUPPORT,
        5: BLOCK_CRITICAL_SUPPORT,
    },
    "B04": {
        1: BLOCK_CRITICAL_SUPPORT,
        2: BLOCK_CRITICAL_SUPPORT,
        3: BLOCK_CRITICAL_SUPPORT,
        4: BLOCK_CRITICAL_SUPPORT,
        5: BLOCK_CRITICAL_SUPPORT,
    },
    "B06": {0: BLOCK_MUST_ACTIVATE},
}

SIM_STATUS_LOOKUP_POSTPAID_CONSUMER_MOBILE = {
    "B01": {"unhandled": NORMAL},
    "B02": {"unhandled": BLOCK_DISCONNECTED},
    "B03": {
        "dunning_suspend": WARN_MUST_PAY_BILL,
        "suspend_due_to_dunning": WARN_MUST_PAY_BILL,
        "unhandled": BLOCK_DISCONNECTED,
    },
    "B04": {"unhandled": BLOCK_DISCONNECTED},
}

# Other warnings not tied to SIM status itself
WARN_NOT_4G_COMPATIBLE = "WARN_NOT_4G_COMPATIBLE"

SIM_NBA_LOOKUP = {
    WARN_RECHARGE: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
    WARN_NOT_4G_COMPATIBLE: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
    WARN_MUST_PAY_BILL: {
        "href": "",
        "message_en": "",
        "message_ar": "",
        "message_kd": "",
        "href_text_en": "",
        "href_text_ar": "",
        "href_text_kd": "",
    },
}

ELIGIBLE_PRIMARY_OFFERINGS: list[int] = [
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

# using CBS ID
NEGCRED_LOOKUP: dict[int, int] = {
    2086106: 2000,
    2086107: 4000,
    2086108: 6000,
    2086109: 8000,
    2086110: 10000,
    2086111: 12000,
}

POSTPAID_PRIME_PRIMARY_OFFERINGS: list[int] = []

ZAINFI_NBA: dict = {
    "href": "https://apps.iq.zain.com/zain-fi",
    "message_en": "Did you hear about our new Zain-Fi app?",
    "message_ar": "Did you hear about our new Zain-Fi app?",
    "message_kd": "Did you hear about our new Zain-Fi app?",
    "href_text_en": "View app",
    "href_text_ar": "View app",
    "href_text_kd": "View app",
}

POSTPAID_PRIME_NBA: dict = {
    "href": "https://www.iq.zain.com/ar/new-prime-line-strongest-postpaid-line-zain ",
    "message_en": "Upgrade to Postpaid Prime now!",
    "message_ar": "Upgrade to Postpaid Prime now!",
    "message_kd": "Upgrade to Postpaid Prime now!",
    "href_text_en": "Check it out",
    "href_text_ar": "Check it out",
    "href_text_kd": "Check it out",
}
