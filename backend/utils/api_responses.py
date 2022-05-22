from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum

class Status(str, Enum):
    success = "success"
    failed = "failed"


class Error(BaseModel):
    type: str
    code: int
    message: str


class ApiException(Exception):
    status_code: int
    error: Error

    def __init__(self, status_code: int, error: Error):
        super().__init__(status_code)
        self.status_code = status_code
        self.error = error


class ApiResponse(BaseModel):
    status: Status = Status.success
    error: Optional[Error] | None 
    data: Optional[dict[str, Any]] | Optional[BaseModel] | None

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        kwargs.pop("exclude_none")
        return super().dict(*args, exclude_none=True, **kwargs)

    class Config:
        use_enum_values = True
