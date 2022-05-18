from pydantic import BaseModel
from typing import Any
from enum import Enum


class Status(str, Enum):
    success = "success"
    failed = "failed"


class Error(BaseModel):
    type: str
    code: int
    message: str


class ApiResponse(BaseModel):
    status: Status
    errors: list[Error] | None = None
    data: dict[str, Any] | BaseModel | None = None 

    class Config:
        use_enum_values = True
