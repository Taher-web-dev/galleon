from typing import Optional, Dict, Any
from pydantic import BaseModel
import api.models.errors as api_errors
from .data import Status, Error


# ================================== Response Models
class ApiResponse(BaseModel):
    """The base ApiResponse model"""

    status: Status = Status.success
    error: Optional[Error] = None
    data: Optional[Dict[str, Any]] | Optional[BaseModel] = None

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        kwargs.pop("exclude_none")
        return super().dict(*args, exclude_none=True, **kwargs)

    class Config:
        use_enum_values = True

        @staticmethod
        def schema_extra(schema, model) -> None:
            if schema.get("properties")["status"]["default"] == "success":
                schema.get("properties").pop("error")
            elif schema.get("properties")["status"]["default"] == "failed":
                schema.get("properties").pop("data")


class ApiException(Exception):
    """Base Response in case of Exceptions"""
    status_code: int
    error: Error

    def __init__(self, status_code: int, error: Error):
        super().__init__(status_code)
        self.status_code = status_code
        self.error = error


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
