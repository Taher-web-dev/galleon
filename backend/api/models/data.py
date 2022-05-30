"""Pydantic data models to be reusable anywhere"""

from typing import Optional
from pydantic import BaseModel
from enum import Enum


class Status(str, Enum):
    success = "success"
    failed = "failed"


class Error(BaseModel):
    type: str
    code: int
    message: str | list[dict]
    extra: Optional[dict] = None
