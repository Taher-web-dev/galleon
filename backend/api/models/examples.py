""" Additional Responses (API doc examples) """

from http.client import responses
from typing import Any
from fastapi import status
from .response import (
    InvalidAccessTokenResponse,
    ValidationErrorResponse,
    ExpiredTokenResponse,
)

not_authenticated: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": InvalidAccessTokenResponse,
        "description": "Invalid Token",
    },
    status.HTTP_410_GONE: {
        "model": ExpiredTokenResponse,
        "description": "Expired Token",
    },
}

validation: dict[int | str, dict[str, Any]] = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ValidationErrorResponse,
        "description": "Validation Error",
    }
}


def general_response(responses: list[dict]) -> dict:
    # gen_resp = {}
    keys = []
    vals = []
    for resp in responses:
        for key, val in resp.items():
            keys.append(key)
            vals.append(val)
    gen_resp = dict(zip(keys, vals))
    return gen_resp
