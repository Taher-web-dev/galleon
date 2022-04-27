class SIMResponseMock:
    def __init__(self, state: int = 0):
        states = [
            {
                "response": {"code": "0000", "message": "Success."},
                "data": {
                    "crm_status_code": "B01",
                    "crm_status_details": "Normal",
                    "cbs_status_code": "1",
                    "subscriber_type": "0",
                    "customer_type": "Individual",
                    "expiry_date": "20220519",
                    "primary_offering_id": "2122764",
                    "activation_date": "20220130160025",
                },
            },
            {
                "response": {"code": "0000", "message": "Success."},
                "data": {
                    "crm_status_code": "B01",
                    "crm_status_details": "Normal",
                    "cbs_status_code": None,
                    "subscriber_type": "1",
                    "customer_type": "Individual",
                    "expiry_date": "20370101",
                    "primary_offering_id": "2200695",
                    "activation_date": "20220405141623",
                },
            },
        ]
        self.data = states[state]


class USIMResponseMock:
    def __init__(self, state: int = 0):
        states = [
            {
                "response": {"code": "0", "message": "SUCCESS"},
                "data": {"sim_compatible_4G": 0, "handset_compatible_4G": 0},
            },
            {
                "response": {"code": "0", "message": "SUCCESS"},
                "data": {"sim_compatible_4G": 1, "handset_compatible_4G": 0},
            },
            {
                "response": {"code": "0", "message": "SUCCESS"},
                "data": {"sim_compatible_4G": 0, "handset_compatible_4G": 1},
            },
            {
                "response": {"code": "0", "message": "SUCCESS"},
                "data": {"sim_compatible_4G": 1, "handset_compatible_4G": 1},
            },
            {
                "response": {"code": "1001", "message": "MSISDN CANNOT BE NULL"},
            },
            {
                "response": {"code": "1002", "message": "INVALID MSISDN FORMAT"},
            },
            {
                "response": {"code": "1003", "message": "MSISDN DOESNT EXIST"},
            },
            {
                "response": {"code": "9999", "message": "UNHANDLED EXCEPTION"},
            },
        ]
        self.data = states[state]


class BalanceResponseMock:
    def __init__(self, state: int = 0):
        states = [
            {
                "response": {"code": "0000", "message": "SUCCESS"},
                "data": {"amount": "1000000", "validity": "20220801"},
            },
            {
                "response": {"code": "0000", "message": "SUCCESS"},
                "data": {"amount": "0", "validity": "20220611"},
            },
        ]
        self.data = states[state]


class BillResponseMock:
    def __init__(self, state: int = 0):
        states = [
            {
                "response": {"code": "0000", "message": "Success."},
                "data": {
                    "total_with_tax": "15278000",
                    "total_without_tax": "15278000",
                    "unbilled": "0",
                    "unbilled_tax": "0",
                    "outstanding": "15278000",
                    "deposit": "0",
                    "advanced_payment": "0",
                },
            }
        ]
        self.data = states[state]


class SubscriptionsResponseMock:
    def __init__(self, state: int = 0):
        states = [
            {
                "response": {
                    "code": "405000000",
                    "message": "Operation is successful.",
                },
                "data": {
                    "subscriptions": [
                        {
                            "id": "200092",
                            "effective_time": "20220130153646",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": None,
                            "cycle_end": None,
                        },
                        {
                            "id": "214017",
                            "effective_time": "20220327123942",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": None,
                            "cycle_end": None,
                        },
                        {
                            "id": "55300",
                            "effective_time": "20220418131229",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": "20220418000000",
                            "cycle_end": "20220426000000",
                        },
                        {
                            "id": "100171",
                            "effective_time": "20220130153646",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": None,
                            "cycle_end": None,
                        },
                        {
                            "id": "991",  # this is fake for now
                            "effective_time": "20220430153646",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": "20220430153646",
                            "cycle_end": "20220507153646",
                        },
                    ]
                },
            },
            {
                "response": {
                    "code": "405000000",
                    "message": "Operation is successful.",
                },
                "data": {
                    "subscriptions": [
                        {
                            "id": "200092",
                            "effective_time": "20220130153646",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": None,
                            "cycle_end": None,
                        },
                        {
                            "id": "214017",
                            "effective_time": "20220327123942",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": None,
                            "cycle_end": None,
                        },
                        {
                            "id": "100171",
                            "effective_time": "20220130153646",
                            "expire_time": "20370101000000",
                            "status": "0",
                            "cycle_start": None,
                            "cycle_end": None,
                        },
                    ]
                },
            },
        ]
        self.data = states[state]
