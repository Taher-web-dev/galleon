""" Additional Responses (API doc examples) """

from http.client import responses
from typing import Any
from fastapi import status
from .response import NotAuthenticatedResponse, ValidationErrorResponse

not_authenticated: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": NotAuthenticatedResponse,
        "description": "Not authenticated",
    }
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
        keys.append(*list(resp.keys()))
        vals.append(*list(resp.values()))
    gen_resp = dict(zip(keys, vals))
    return gen_resp
