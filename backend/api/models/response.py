from utils.api_responses import Error, Status, ApiResponse
import api.models.errors as api_errors

# ================================== Response Models
class SuccessResponse(ApiResponse):
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
            }
        }


# ================================== ErrorResponse Models
class NotAuthenticatedResponse(ApiResponse):
    status: Status = Status.failed
    error: Error = api_errors.NOT_AUTHENTICATED
