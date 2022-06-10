import json

from api.models.data import Error


def error_response(error: Error):
    return {
        "application/json": {
            "example": {"status": "failed", "error": json.loads(error.json())}
        }
    }
