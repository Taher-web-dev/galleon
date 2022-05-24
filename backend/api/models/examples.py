""" Additional Responses (API doc examples) """

from typing import Any
from fastapi import status
from .response import NotAuthenticatedResponse

not_authenticated: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": NotAuthenticatedResponse,
        "description": "Not authenticated",
    }
}
