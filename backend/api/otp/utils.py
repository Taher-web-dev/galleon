import random
import string
import json
import sys
import requests
from utils.settings import settings


def gen_alphanumeric(length=16):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def gen_numeric(length=4):
    return "".join(random.choice(string.digits) for _ in range(length))


def slack_notify(msisdn: str, code: str):

    # If no webhook is configured, do nothing.
    if not settings.slack_webhook_url or not settings.slack_notify:
        return

    slack_data = {
        "username": "Galleon",
        "icon_emoji": ":robot_face:",  # ":satellite:",
        "channel": "#mbb_otp_notifier",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "value": f"Otp code `{code}` for msisdn `{msisdn}`",
                        "short": "true",
                    }
                ],
            }
        ],
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {"Content-Type": "application/json", "Content-Length": byte_length}
    response = requests.post(
        settings.slack_webhook_url, data=json.dumps(slack_data), headers=headers
    )
    # print(json.dumps(slack_data))
    # print(response.text)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
