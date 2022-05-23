from fastapi import status
from typing import Any, Dict
from utils.api_responses import Error, Status, ApiResponse

# ================================== Models
# TODO rename to SuccessResponse
class StatusResponse(ApiResponse):
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
            }
        }


class NotAuthenticatedResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = Error(type="jwtauth", code=10, message="Not authenticated")


# ================================== Additional Responses (API doc examples)
# for every JWT dependent endpoint
not_authenticated: Dict[int | str, Dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": NotAuthenticatedResponse,
        "description": "Not authenticated",
    }
}
